# Balloon Game — Complete Game Dynamics Specification

This document describes, precisely and exhaustively, how the Balloon Game works as implemented in this repository (`modules/engine.py`, `modules/strategies.py`, `modules/core.py`, `modules/e2e_harness.py`). It is written for an agent that will design its own strategy. Everything here is derived from the actual code, and every numeric claim was checked numerically. Where the code has quirks that differ from the intended design, they are called out explicitly in §11.

Your goal is to write a strategy that **maximizes cumulative points (PnL)** over a finite sequence of balloons, which is the same as **minimizing cumulative regret** against an oracle that knows the true pop probabilities. A second mode pits two strategies against each other on the same balloons (§6).

---

## 1. The game in one paragraph

A game is a sequence of `N` balloons (e.g. 300). Each balloon has a color. Each color `c` has a fixed, **hidden** pop probability `p_c` in (0, 1). Every pump pops the balloon independently with probability `p_c`: the pop risk is memoryless and does not grow with more pumps. For each balloon, your strategy commits **up front** to a single integer threshold `k`, the number of pumps it will attempt before cashing. If the balloon survives all `k` pumps, you bank `k` points. If it pops on or before pump `k`, you bank 0. You then receive feedback and move to the next balloon. You never see the probabilities. You must learn them from censored feedback while also earning points.

This is a version of the Balloon Analogue Risk Task (BART). It is structurally a **per-color multi-armed bandit with a continuum of integer arms and right-censored feedback**.

---

## 2. Balloon generation (exact)

For each game, the engine creates all `N` balloons up front from a seeded RNG (`Game.initialization`):

```python
for i in range(N):
    color     = rng.choice(colors)          # uniform over the color list
    p         = color_map[color]
    pop_value = rng.geometric(p)            # support {1, 2, 3, ...}
    Balloon(color, pop_value, p, id=i)
```

Facts that follow:

- **Colors are i.i.d. uniform** over the configured colors. With `K` colors, each color shows up about `N/K` times (e.g. 300 balloons / 4 colors ≈ 75 per color), with binomial variation. The order is random, and the strategy cannot know the upcoming color in advance.
- **`pop_value` = V is the pump number on which the balloon pops.** `P(V = v) = (1-p)^(v-1) · p` for v ≥ 1. The minimum is 1: a balloon can pop on the very first pump.
- **Survival:** a threshold `k` survives iff `k < V`, i.e. `k ≤ V − 1`. So `P(survive k pumps) = (1−p)^k`. The largest bankable amount on a given balloon is `V − 1`, and a balloon with `V = 1` pays 0 no matter what you do.
- Balloons are independent of each other and of your actions. **Your actions never change future balloons.** There is no state carried between balloons except your own knowledge.
- The same game seed yields the same balloon sequence (colors *and* pop values) for every strategy. Strategies in one experiment are therefore compared on identical balloons, which makes paired comparisons valid (§9).
- Balloon ids run `0 … N−1` in order.

---

## 3. Single-player rules (exact)

`Game.calc_payout` with one player:

| Threshold `k` | Outcome | Payout |
|---|---|---|
| `0 ≤ k < V` | survived | `k` |
| `k ≥ V` | popped | `0` |
| `k < 0` | (degenerate) | `0` |

- Threshold `0` always pays 0. Useful thresholds are integers ≥ 1.
- PnL is the running sum of payouts. There are no negative payouts, no costs, and no discounting. Only final PnL matters, though regret curves also measure how fast you learn.

---

## 4. What a strategy can see and do (the interface)

### 4.1 The contract

Strategies subclass `Strategy` in `modules/strategies.py`:

```python
class my_strategy(Strategy):
    KEY = "my_strategy"                  # unique registry key, REQUIRED
    PARAMS = [("some_param", float)]     # (name, type) pairs; [] if none

    def __init__(self, ctx, rng, some_param: float):
        super().__init__(name="my_strategy_<unique>", ctx=ctx, rng=rng)
        ...

    def action(self, balloon: Balloon) -> int:
        ...  # return the threshold k for this balloon

    def update_beliefs(self, obs: Observation) -> None:
        ...  # called once after every balloon resolves
```

- Instantiation is `cls(**params, ctx=ctx, rng=rng)`, with all arguments passed by keyword.
- YAML parameters are type-checked with `isinstance`. A `float` param must be written `0.0`, not `0`. A strategy with no params needs `params: {}`.
- `self.rng` is a seeded `numpy.random.Generator`. **Use only `self.rng` for randomness** so runs are reproducible. Do not use `random`, `np.random.*` globals, or time.
- `self.PnL` is your running PnL. The engine maintains it, and you may read it.
- `self.belief_state` is a dict pre-filled with `{color: 1}`. You may use it or ignore it.
- Return a **plain Python `int`**, e.g. `int(k)`.

### 4.2 Timing of one round (`Game.balloon_loop`)

```
for balloon in balloons:
    thresholds = {s.name: s.action(balloon) for s in strategies}   # all decide first
    payouts    = calc_payout(thresholds, balloon)
    PnL       += payouts
    for s in strategies: s.update_beliefs(obs_for[s.name])
```

- In multiplayer, both players choose **simultaneously**. Neither sees the other's current threshold before acting.
- `update_beliefs` is called exactly once per balloon, after resolution, and always before the next `action`.
- The whole game runs in one process, and the strategy object persists across balloons. You can store any history you want (a full log, sufficient statistics, and so on).

### 4.3 `Context` (`self.ctx`)

- `ctx.num_balloons`: total balloons `N` in this game. The horizon is known.
- `ctx.colors`: list of all possible colors (unique). The number of colors `K` is known.
- Pop probabilities are **not** given. Color frequencies are not given either, though they are uniform by construction.

### 4.4 The `Balloon` passed to `action`

| Field | Legitimate to use? |
|---|---|
| `balloon.color` | **Yes**: this is the context |
| `balloon.id` | **Yes**: index 0…N−1, so `N − id` balloons remain including this one |
| `balloon.pop_value` | **NO. Reading it is cheating.** It is the future outcome. |
| `balloon.prob` | **NO. Reading it is cheating.** It is the hidden parameter. |

The engine passes the whole object for convenience, but a legitimate strategy must decide using only color, id, context, and past observations. Do not mutate the balloon object either, because it is shared between players.

### 4.5 The `Observation` passed to `update_beliefs`

```python
obs.balloon_color   # color of the balloon just played
obs.own_threshold   # the k you submitted
obs.pop_time        # V exactly, IF YOU POPPED (own_threshold >= V); otherwise the sentinel 999
obs.payout          # dict {strategy_name: payout} for ALL players this round (copy)
```

**Censoring is the core informational feature.**
- **Pop** (`k ≥ V`): you learn V **exactly** (`obs.pop_time`). That is an uncensored draw from Geometric(p).
- **Survive** (`k < V`): you only learn `V > k`, a right-censored observation. `pop_time == 999`.

In single-player, `obs.payout = {your_name: k or 0}`, which carries no information beyond the above.

---

## 5. Single-player mathematics

### 5.1 Optimal threshold with known `p`

Expected payout of threshold `k`: `f(k) = k · (1−p)^k`.

`f(k+1)/f(k) = (1−p)(k+1)/k`, which is ≥ 1 iff `k ≤ (1−p)/p`. Hence the optimum is

```
k*(p) = max(1, ceil((1−p)/p))
```

If `(1−p)/p` is an integer, `k*` and `k*+1` tie exactly. This is what `oracle` plays. Continuous intuition: `k* ≈ −1/ln(1−p) ≈ 1/p − 1/2`. At the optimum, the survival probability is about 0.34 to 0.42 for small `p`. **The optimal policy pops more often than it survives** whenever `p ≤ 0.5`.

### 5.2 Reference table (verified)

| p | k* | EV per balloon at k* | P(survive) at k* |
|---|---|---|---|
| 0.05 | 19 | 7.170 | 0.377 |
| 0.10 | 9 (=10) | 3.487 | 0.387 |
| 0.20 | 4 (=5) | 1.638 | 0.410 |
| 0.25 | 3 | 1.266 | 0.422 |
| 0.30 | 3 | 1.029 | 0.343 |
| 0.40 | 2 | 0.720 | 0.360 |
| 0.50 | 1 (=2) | 0.500 | 0.500 |
| 0.60 | 1 | 0.400 | 0.400 |
| 0.80 | 1 | 0.200 | 0.200 |

Note how strongly **value is concentrated in low-p colors**. With `p = {0.1, 0.4, 0.6, 0.8}`, the oracle earns 3.487 / 0.72 / 0.4 / 0.2 per balloon, averaging 1.20. The red (p=0.1) balloons alone produce about 72% of the oracle's points. **Getting the low-p colors right is what matters most. Errors on high-p colors are cheap in absolute points.**

### 5.3 Sensitivity: how costly is a wrong threshold? (EV as % of optimal, verified)

```
p=0.1 k*=9 | 1:26% 2:46% 3:63% 4:75% 5:85% 6:91% 7:96% 8:99% 9:100% 10:100% 11:99% 12:97% 13:95% 14:92% 15:89% 16:85% 17:81% 18:77% 19:74% 20:70%
p=0.2 k*=4 | 1:49% 2:78% 3:94% 4:100% 5:100% 6:96% 7:90% 8:82% 9:74% 10:66%
p=0.4 k*=2 | 1:83% 2:100% 3:90% 4:72% 5:54% 6:39%
p=0.6 k*=1 | 1:100% 2:80% 3:48% 4:26% 5:13%
p=0.8 k*=1 | 1:100% 2:40% 3:12% 4:3% 5:1%
```

Takeaways:
- For low `p`, the curve is flat near the top and **asymmetric: overshooting costs less than undershooting by the same number of pumps** (e.g. p=0.1: k=13 → 95%, but k=5 → 85%).
- For high `p` the opposite holds in absolute terms: k=1 is correct, and pumping more collapses value quickly. But the absolute stakes are small (0.2 to 0.4 points per balloon).
- Mistakes are measured on a **multiplicative** scale in `k`, which roughly corresponds to errors in `log p`.

### 5.4 Learning `p`: exact Bayesian update with censoring

With a Beta prior `p ~ Beta(a, b)` (a counts pops/"failures", b counts survived pumps/"successes"), the geometric likelihood is conjugate **even under censoring**:

- **Popped, V = v observed:** likelihood `(1−p)^(v−1) · p` → `a += 1`, `b += v − 1`.
- **Survived k pumps (V > k):** likelihood `(1−p)^k` → `b += k`.

This is exactly what the built-in `Strategy.payout_infer` computes (returns `[b_increment, a_increment]`). Built-in learners start from `[1, 1]`, a uniform prior, and use the posterior mean `p̂ = a / (a + b)`.

This censored-geometric likelihood gives a consistent estimator whenever thresholds are ≥ 1. Every pump you attempt is one Bernoulli(p) trial you get to observe. **The information you collect is basically the number of pump trials you observe: each balloon adds `min(k, V)` trials, of which at most one is a pop.** Higher thresholds collect more trials per balloon (more information) at the cost of expected payout. Threshold 1000 ("full exploration") pops almost surely: it yields V exactly (≈ 1/p trials) and earns 0.

### 5.5 Deciding under uncertainty: plug-in vs Bayesian expected value

The built-in greedy strategies plug the posterior mean into `k*(p̂)`. That is not the Bayes-optimal myopic decision. Under the posterior `p ~ Beta(a, b)`, the expected payout of threshold `k` is exact and cheap to compute:

```
E[k · (1−p)^k] = k · B(a, b+k) / B(a, b) = k · Π_{i=0}^{k−1} (b+i)/(a+b+i)
```

Because `(1−p)^k` is convex in `p`, Jensen's inequality gives `E[(1−p)^k] ≥ (1−E[p])^k`, and the gap grows with `k`. **Under uncertainty, the Bayes-myopic threshold is typically higher than the plug-in threshold.** Example (verified): with `a=3, b=20` (posterior mean p≈0.13), plug-in gives `k = ceil(0.87/0.13) = 7`, while the posterior expected payout peaks at `k = 10–11` (3.105). This effect matters most early in the game and for low-p colors.

### 5.6 The exploration–exploitation structure

- Per color, you face about `N/K` decisions. The horizon is known (`ctx.num_balloons`, `balloon.id`), so the remaining number of balloons of a color can be estimated as `(N − id)/K`.
- **Exploiting also produces information.** A threshold near `k*` pops about 60% of the time for low p, which reveals V exactly. Survivals add `k` censored trials. Pure greedy learners therefore keep learning without explicit exploration, and they self-correct. If `k` is too low, frequent survivals push `p̂` down and `k` up. If `k` is too high, frequent pops push `p̂` up and `k` down.
- **Explicit exploration has been costly in experiments** (§10): every ε > 0 lost to ε = 0, and Thompson sampling lost to plain greedy. An explore round at threshold 1000 forfeits the full EV of that balloon (up to 3.5 points for p=0.1).
- **Where a smarter policy can still gain:** early-game decisions (first ~5–15 balloons per color) under a weak prior; exploiting the asymmetric loss curve (lean high on colors that look low-p); using the known horizon (information is worth less near the end, so be myopic late); and choosing thresholds by posterior expected value rather than by plugging in a point estimate. The gap between the best learners and the oracle is only about 5% of PnL (§10), so gains come from getting many small things right.
- **Colors are independent.** No mechanism links different colors' probabilities. A hierarchical prior across colors (e.g. learning that probabilities in this game tend to be low) is the only cross-color transfer available, and it is a legitimate modeling choice. Configured probabilities have historically spanned 0.1–0.9.

---

## 6. Multiplayer mode (two players, head-to-head)

Enabled with `multiplayer: 1`. With more than 2 strategies configured, a **round robin** is played: every unordered pair plays a separate game on each balloon seed, and each pair game uses the same balloon sequence for that seed.

### 6.1 Payout rules (exact, `calc_payout` with 2 players)

Given thresholds `k1, k2` and pop value `V`:

| Case | Player 1 gets | Player 2 gets |
|---|---|---|
| both pop (`k1 ≥ V`, `k2 ≥ V`) | 0 | 0 |
| only 1 pops (`k1 ≥ V > k2`) | 0 | `k2` |
| only 2 pops (`k2 ≥ V > k1`) | `k1` | 0 |
| both survive, `k1 > k2` | **`k1 + k2`** | 0 |
| both survive, `k1 < k2` | 0 | **`k1 + k2`** |
| both survive, `k1 == k2` | fair coin: winner gets `2k`, loser 0 | |

**Winner takes the pot when both survive.** The higher threshold that did not pop collects both players' thresholds. If exactly one player survives, that player keeps only their own threshold. This works like an auction for a common-value asset: you want to bid higher than your opponent but not higher than the (unknown) true value.

### 6.2 Expected payoff for fixed thresholds (verified)

With `q = 1 − p`:

```
k1 > k2 :  U1 = q^k1 · (k1 + k2)
k1 < k2 :  U1 = k1 · (q^k1 − q^k2)        # you only get paid when the opponent pops and you don't
k1 = k2 :  U1 = k · q^k
```

The game is not zero-sum. The total paid out never exceeds `k1 + k2`.

### 6.3 Strategic consequences (verified numerically)

**Best responses leapfrog.** To an opponent at `k2`, the best response is usually `k2 + 1`, until `k2` is so high that it pays to drop down and collect the balloons where the opponent pops:

```
p=0.1  BR(k2=0..11) = [9, 8, 8, 6, 5, 6, 7, 8, 9, 10, 11, 12]
p=0.4  BR(k2=0..11) = [2, 2, 3, 4, 5, 2, 2, 2, 2, 2, 2, 2]
p=0.6  BR(k2=0..11) = [1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1]
p=0.8  BR(k2=0..11) = [1, 1, 1, ...]
```

**The single-player optimum is badly exploitable.** Against an opponent who plays the oracle threshold `k*`:

| p | oracle vs oracle (each) | best response | BR earns | oracle then earns |
|---|---|---|---|---|
| 0.1 | 3.487 | k = 10 | **6.625** | 0.349 |
| 0.2 | 1.638 | k = 5 | **2.949** | 0.328 |
| 0.4 | 0.720 | k = 3 | **1.080** | 0.288 |
| 0.6 | 0.400 | k = 2 | **0.480** | 0.240 |
| 0.8 | 0.200 | k = 1 | 0.200 | 0.200 |

So **against a known, predictable opponent, go one pump above their threshold** (for p ≤ 0.6). That nearly doubles your per-balloon value and crushes theirs.

**There is no pure equilibrium for low p.** Symmetric equilibria:
- p = 0.8: pure `k = 1`.
- p = 0.6: pure `k = 2` is a symmetric equilibrium (value 0.32 each). Another mixes `{2: 0.64, 3: 0.36}` (value 0.274).
- p = 0.4: no pure equilibrium. One mixed equilibrium is `{3: 0.389, 4: 0.056, 5: 0.556}`, value 0.497 each.
- p = 0.3: mixed over roughly k = 3…8, with mass rising toward the top, value ≈ 0.70.
- p = 0.2: mixed over roughly k = 3…13, value ≈ 1.12.
- p = 0.1: mixed over roughly k = 8…28, value ≈ 2.39.

These were found by support enumeration and verified against all deviations up to k = 60. Other equilibria may exist. The qualitative picture is robust: **in head-to-head play, equilibrium thresholds are randomized and sit well above the single-player optimum, and each player's value falls below the single-player oracle value.** A deterministic, learnable threshold invites leapfrogging, so randomization (via `self.rng`) is strategically meaningful here.

### 6.4 Information in multiplayer (what you can infer from `obs`)

You still get your own `pop_time` only if **you** popped. You never directly see the opponent's threshold. However, `obs.payout` contains both payouts. The opponent's name is the key that is not `self.name`. Let `k` be your threshold, `P_me` and `P_opp` the payouts:

| What you observe | What happened | What you learn |
|---|---|---|
| you popped, `P_opp > 0` | opponent survived | `k_opp = P_opp`, and `V > k_opp` (extra censored obs) |
| you popped, `P_opp = 0` | opponent popped too (or `k_opp = 0`) | `k_opp ≥ V` (V known to you) |
| you survived, `P_me = k + x` with `x > 0` | both survived, you won | `k_opp = x < k`; no new info on V beyond `V > k` |
| you survived, `P_me = 2k` | tie, you won the coin flip | `k_opp = k`, `V > k` |
| you survived, `P_me = k` (k > 0) | opponent popped, or `k_opp = 0` | `k < V ≤ k_opp` (k_opp unknown but > k) |
| you survived, `P_me = 0`, `P_opp > 0` | opponent survived with `k_opp ≥ k` | `k_opp = P_opp − k`, and `V > k_opp` (extra censored obs) |

Implications:
- You can **reconstruct the opponent's threshold** in many rounds and model their policy per color (e.g. a learning curve, a fixed rule, a randomization pattern).
- You can get **extra information about `p`** from the opponent's survivals (`V > k_opp`). Caution: the opponent's threshold is revealed *selectively*, depending on the outcome. If you add `V > k_opp` only when it is revealed and ignore the cases where it isn't, your estimate becomes biased. In the "you survived, opponent popped" case, you learn `V ∈ (k, k_opp]` with `k_opp` hidden, and that is informative. The built-in strategies deliberately ignore opponent information to avoid this bias. A correct approach uses the full likelihood, e.g. marginalizing over a model of the opponent's threshold.
- The opponent can do the same to you.

---

## 7. Evaluation metrics used in this project

Per game, the log CSV has one row per (balloon, strategy):
`balloon_id, balloon_color, pop_time, strategy_name, threshold, end_PnL`
(`pop_time` in the log is always the true V. Strategies never see this log.)

- **End PnL**, averaged over many seeds (typically 50).
- **Realized cumulative regret** (`metrics.add_regret`, single-player): per balloon, `oracle_gain − your_gain`, where the oracle plays `ceil((1−p)/p)` on the same balloon. This can be negative on individual balloons through luck.
- **Pseudo-regret (expected regret):** `k*·(1−p)^k* − k·(1−p)^k` per balloon, which removes pop-luck noise.
- **Threshold distance:** `d = (k − k*)^2`.
- Regret curves are plotted per balloon and averaged over seeds. **Learning speed (the shape of the regret curve) is judged, not just final PnL.** Good learners show regret flattening to a roughly logarithmic curve.

---

## 8. Experiment configuration (how games are run)

`config.yaml`:

```yaml
run_name: <folder name>
master_seed: 111           # int
num_seeds: 50              # games per strategy (different balloon sequences)
num_balloons: 300
multiplayer: 0             # 0 = each strategy plays alone; 1 = round-robin head-to-head
strategies:
    - name: epsilon_greedy
      params: {eps: 0.0}
    - name: my_strategy
      params: {}
color_map:                 # hidden from strategies
    red: 0.1
    blue: 0.4
    orange: 0.6
    purple: 0.8
```

- A master seed generates `num_seeds` balloon seeds. In single-player mode, every strategy plays each balloon seed alone, on identical balloons.
- Seeds for each strategy's RNG come from the balloon seed, so results are fully reproducible.

---

## 9. Noise and statistical care

- Over 300 balloons with the reference color map, final PnL has a **standard deviation of about 45** across seeds for every strategy, while strategy differences are about 10–30 points. The variance comes mostly from the balloons, not the strategy.
- Because all strategies face **identical balloons per seed**, compare strategies with **paired differences per seed**, or with pseudo-regret. Raw means over 50 seeds are too noisy to separate close strategies.
- A strategy tuned to the reference color map may overfit. Test on several color maps (e.g. all-low `{0.1, 0.2, 0.3, 0.4}`, all-high `{0.6, 0.7, 0.8, 0.9}`, spread `{0.2, 0.4, 0.7, 0.9}`) and several horizons (N = 10 … 2000).

---

## 10. Empirical results so far (from `output/game_logs`, mean ± sd of end PnL over 50 seeds)

**Reference map `{red 0.1, blue 0.4, orange 0.6, purple 0.8}`, N = 300** (oracle EV ≈ 1.2017 × 300 ≈ 360.5):

| strategy | end PnL |
|---|---|
| oracle (knows p) | 367.7 ± 41.8 |
| bayes_myopic (not present in current code) | 348.6 ± 46.2 |
| ε-greedy, ε = 0 (plug-in posterior mean) | 347.9 ± 44.8 |
| Thompson sampling (plug-in of a Beta sample) | 335.8 ± 44.0 |

**Map `{0.2, 0.4, 0.7, 0.9}`:**

| strategy | N=10 | N=25 | N=50 | N=100 | N=300 | N=500 |
|---|---|---|---|---|---|---|
| oracle | 7.7 | 19.6 | 37.9 | 72.7 | 212.0 | 350.8 |
| ε = 0.02 greedy | 5.7 | 16.2 | 32.7 | 65.0 | — | 335.2 |
| ε = 0.08 greedy | 5.2 | 14.9 | 30.0 | 59.9 | — | 314.5 |
| ε = 0.32 greedy | 3.9 | 11.5 | 22.4 | 45.8 | — | 235.8 |
| ε = 0.1 greedy / explore-then-exploit 0.1 | — | — | 30 | 60 | 184–186 | — |
| guess uniform 1..4 (`guess_5`) | — | — | — | — | 160.7 | — |
| always 1 | — | — | — | — | 136.0 | — |

**Map `{0.1, 0.2, 0.3, 0.4}`, N = 300:** oracle 517.3, ε=0 greedy 488.0, ε=0.02 478.7, ε=0.08 450.7.

Observed patterns:
1. Lower ε is always better, at every horizon (10 to 2000) and every map tested. ε = 0 is best of the ε family.
2. Explore-then-exploit with ratio r is about equivalent to ε-greedy with ε = r.
3. Thompson sampling (one posterior sample plugged into `k*`) is worse than greedy.
4. The best learners sit about 20–30 points (≈ 5–6%) below the oracle on N=300. **That gap is the room available for improvement.**

---

## 11. Implementation quirks and pitfalls (important)

1. **Cheating fields.** `balloon.pop_value` and `balloon.prob` are reachable in `action()`. Do not use them (§4.4).
2. **Negative thresholds in multiplayer are not guarded.** Single-player clamps `k < 0` to 0, but multiplayer does not. A negative `k` "never pops", earns a negative payout when the opponent pops, and reduces the opponent's pot when they win. This is an unintended bug, not a mechanic. Return integers ≥ 1.
3. **Strategy names must be unique within a game.** Thresholds and payouts are dicts keyed by `strategy.name`. Two players with the same name overwrite each other and the game silently degrades to single-player logic. Make the name include distinguishing parameters.
4. **`KEY` must be unique and non-empty.** Registering a subclass with a duplicate `KEY` raises at import time.
5. **Return type.** Return a Python `int`. Floats would produce float payouts, and arrays such as `rng.integers(..., size=1)` store garbage in the log.
6. **`pop_time == 999` is the "survived" sentinel.** Don't treat it as a real pop value.
7. **Threshold 0** is never useful: it always earns 0, in both modes.
8. **Ties in the posterior→threshold map.** `ceil((1−p)/p)` has floating-point edges at integer ratios (e.g. p=0.1 may give 9 or 10). Both are equally optimal, so this is harmless.
9. `update_beliefs` receives every balloon's observation, including ones where your threshold was 0 or very large.

---

## 12. Summary of levers for a strong strategy

**Single-player:**
- Model each color's `p` with the exact censored-geometric Beta posterior (§5.4). Choose a prior deliberately. A uniform Beta(1,1) is weak, and a hierarchical or empirical prior across colors may help.
- Choose `k` by **posterior expected payout** (§5.5), not a plug-in point estimate. Consider going beyond myopic: the value of information depends on the remaining count for that color, `(N − id)/K`, and higher thresholds buy more observed trials.
- Respect the asymmetric loss (§5.3). Undershooting low-p colors is expensive, and overshooting high-p colors costs little in absolute points.
- Most points come from the lowest-p colors. Learn those first and best.
- Judge candidate strategies with paired per-seed differences and pseudo-regret across many color maps and horizons.

**Multiplayer:**
- The oracle threshold is exploitable by +1 leapfrogging (§6.3). Equilibrium play is randomized and higher than the single-player optimum.
- Reconstruct the opponent's thresholds from `obs.payout` (§6.4), model their policy per color, and best-respond to it, while staying hard to exploit yourself (randomize with `self.rng`).
- Use the opponent's survivals as extra evidence about `p` only with a likelihood that is correct under selective revelation.
