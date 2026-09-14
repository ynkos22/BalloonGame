from core import Balloon, Observation, Context
import numpy as np



class Strategy:

    PARAMS = []
    KEY = ""
    REGISTER = {}

    def __init__(self, name: str, ctx: Context, rng: np.random.Generator):
        self.name = name
        self.PnL = 0
        self.rng = rng
        self.ctx = ctx
        self.belief_state = {} # each color and the corresponding threshold

        # Initialize belief state with uniform belief
        for color in self.ctx.colors:
            self.belief_state[color] = 1

    
    def __init_subclass__(cls, **kwargs):

        if cls.KEY not in Strategy.REGISTER:
            Strategy.REGISTER[cls.KEY] = cls
        else:
            # Already contains the strategy
            raise ValueError(f"duplicate strategy key {cls.KEY}: already registered")
        
    # Returns the pump threshold (at which value to cash) for a balloon
    def action(self, balloon: Balloon) -> int:
        return 1 # default pump

    # updates strategies' beliefs
    def update_beliefs(self, obs: Observation) -> None:
        pass

    # Infers how many successful and unsuccesful pumps from own_threshold and pop_val
    # The opponent's payout is deliberately ignored: it only reveals how deep the balloon
    # went when the opponent SURVIVED, so using it would censor at an outcome-dependent
    # depth and bias the pop-probability estimate downwards.
    # returns np.array([num_suc, num_fail])
    def payout_infer(self, own_threshold: int, pop_val: int) -> np.array:
        result_list = [0, 0]
        if pop_val == 999:
            result_list[0] += own_threshold
        else:
            result_list[0] += max(pop_val-1, 0)
            result_list[1] += 1
        return np.array(result_list)


class constant_pump(Strategy):

    PARAMS = [("pump_times", int)]
    KEY = "constant_pump"

    def __init__(self, pump_times: int, ctx: Context, rng: np.random.Generator):
        super().__init__(name = f"constant_pump_{pump_times}", ctx=ctx, rng=rng)
        self.pump_times = pump_times

    def action(self, balloon: Balloon) -> int:
        return self.pump_times


class explore_exploit(Strategy):

    PARAMS = [("ratio", float)]
    KEY = "explore_exploit"

    def __init__(self, ratio: float, ctx: Context, rng: np.random.Generator):
        super().__init__(name="explore_exploit_" + self.helper_for_naming(str(ratio), ".", "_"), ctx=ctx, rng=rng)
        self.ratio = ratio
        self.num_balloons = ctx.num_balloons

        # Initialize memory with uniform
        # Each color has [#successful, #failures] vector
        self.memory = {}
        for color in ctx.colors:
            self.memory[color] = np.array([1, 1])

    def action(self, balloon: Balloon) -> int:
        if balloon.id <= self.ratio * self.num_balloons:
            # Exploration phase
            return 1000
        else:
            return self.belief_state[balloon.color]

    def update_beliefs(self, obs: Observation):

        succ_fail_vector = self.payout_infer(obs.own_threshold, obs.pop_time)

        # Update self.memory
        self.memory[obs.balloon_color] += succ_fail_vector
        
        # Update self.belief_state
        p = self.memory[obs.balloon_color][1]/(self.memory[obs.balloon_color][0] + self.memory[obs.balloon_color][1])
        self.belief_state[obs.balloon_color] = max(1, int(np.ceil((1-p)/p)))

    # replaces bad letter in string with good letter
    # this function is needed since 0.2 can't be in a filename
    def helper_for_naming(self, string: str, bad_letter: str, good_letter: str):

        new_string = ""

        for letter in string:
            if letter == bad_letter:
                new_string += good_letter
            else:
                new_string += letter

        return new_string


class thompson_sampling(Strategy):

    KEY = "thompson_sampling"

    def __init__(self, ctx: Context, rng: np.random.Generator):
        super().__init__(name = "thompson_sampling", ctx=ctx, rng=rng)

        self.memory = {}
        colors = ctx.colors
        for color in colors:
            self.memory[color] = np.array([1, 1])

    def action(self, balloon: Balloon) -> int:
        return self.belief_state[balloon.color]

    def update_beliefs(self, obs: Observation):
        succ_fail_vector = self.payout_infer(obs.own_threshold, obs.pop_time)
        
        # Update self.memory
        self.memory[obs.balloon_color] += succ_fail_vector

        p = self.thompson_sampler(*self.posterior(obs.balloon_color))
        self.belief_state[obs.balloon_color] = self.decision_rule(p)

    def posterior(self, color):
        return self.memory[color]

    # Given Beta posterior parameters, this function samples a probability p from this distribution
    def thompson_sampler(self, a: int, b: int) -> float:
        sample = self.rng.beta(b, a)
        return sample

    def decision_rule(self, p: float):
        return max(1, int(np.ceil((1-p)/p)))


class oracle(Strategy):

    KEY = "oracle"
    PARAMS = [("color_map", dict)]

    def __init__(self, ctx: Context, rng: np.random.Generator, color_map: dict[str, float]):
        super().__init__(name = "oracle", ctx=ctx, rng=rng)
        self.color_map = color_map

    def action(self, balloon: Balloon):
        p = self.color_map[balloon.color]
        return max(1, int(np.ceil((1-p)/p)))



# With a probability eps, the strategy explores
# and with a probability 1-eps, the strategy exploits

class epsilon_greedy(Strategy):

    PARAMS = [("eps", float)]
    KEY = "epsilon_greedy"

    def __init__(self, ctx, rng, eps: float):
        super().__init__(name=self.helper_for_naming(str(eps), ".", "_") + "_greedy", ctx=ctx, rng=rng)
        self.eps = eps

        # Initialize memory with uniform
        # Each color has [#successful, #failures] vector
        self.memory = {}
        for color in ctx.colors:
            self.memory[color] = np.array([1, 1])

    def action(self, balloon: Balloon) -> int:

        random_draw = self.rng.random()

        if random_draw > self.eps:
            # exploitation phase
            return self.belief_state[balloon.color]
        else:
            # exploration phase
            return 1000

    def update_beliefs(self, obs: Observation) -> None:
        succ_fail_vector = self.payout_infer(obs.own_threshold, obs.pop_time)
        
        # Update self.memory
        self.memory[obs.balloon_color] += succ_fail_vector
        
        # Update self.belief_state
        p = self.memory[obs.balloon_color][1]/(self.memory[obs.balloon_color][0] + self.memory[obs.balloon_color][1])
        self.belief_state[obs.balloon_color] = max(1, int(np.ceil((1-p)/p)))

    # replaces bad letter in string with good letter
    # this function is needed since 0.2 can't be in a filename
    def helper_for_naming(self, string: str, bad_letter: str, good_letter: str):

        new_string = ""

        for letter in string:
            if letter == bad_letter:
                new_string += good_letter
            else:
                new_string += letter

        return new_string


class guess(Strategy):
    PARAMS = [("n", int)]
    KEY = "guess"
    def __init__(self, n, ctx, rng):
        super().__init__(name = f"guess_{n}", ctx=ctx, rng=rng)
        self.n = n

    def action(self, balloon: Balloon):
        return int(self.rng.integers(low=1, high=self.n))


class average_balloon(Strategy):
    KEY = "average_balloon"
    def __init__(self, ctx, rng):
        super().__init__(name="average_balloon", ctx=ctx, rng=rng)


    def action(self, balloon: Balloon):
        return 1



# =============================================================================
# MY STRATEGIES
# =============================================================================


def _logsumexp(x: np.ndarray, axis: int) -> np.ndarray:
    m = np.max(x, axis=axis, keepdims=True)
    return np.squeeze(m + np.log(np.sum(np.exp(x - m), axis=axis, keepdims=True)), axis=axis)


class _BayesDPTable:
    """
    Finite-horizon Bayesian dynamic program for ONE color, solved once and cached.

    Model. Every pump is a Bernoulli(p) trial, so whatever the prior on p, the likelihood of
    everything seen for a color is p^i (1-p)^j with
        i = number of pops observed          (each pop is one "failure" trial)
        j = number of survived pumps observed (k on a survival, V-1 on a pop at V).
    (i, j) is therefore a sufficient statistic even under censoring, and the prior can be any
    density on a grid: W[i, j] = sum_g prior(p_g) p_g^i (1-p_g)^j is all that is ever needed,
        P(pop on pump v | i, j) = W[i+1, j+v-1] / W[i, j]
        P(survive k pumps | i, j) = W[i, j+k]     / W[i, j].

    Bellman recursion over m = balloons of this color still to play (including the current one):
        V_m(i, j) = max_k [ k * P(surv k) + sum_{v<=k} P(pop v) V_{m-1}(i+1, j+v-1)
                                         + P(surv k) V_{m-1}(i, j+k) ]
    with V_1 the myopic posterior expected payout. policy[m, i, j] is the maximising k. That is the
    Bayes-optimal threshold: it trades payout now against the information that more pumps buy,
    automatically leaning high early (when a lower p would be worth a lot and a higher threshold
    observes more trials) and becoming myopic as the horizon runs out.

    States outside the table (i > I or j > J) have a sharp posterior, so the myopic threshold is
    used there. Their continuation values are approximated by m * (myopic value).
    """

    def __init__(self, p_grid: np.ndarray, log_prior: np.ndarray, I: int, J: int, K: int, M: int):
        self.p_grid = np.asarray(p_grid, dtype=float)
        lp = np.asarray(log_prior, dtype=float)
        self.log_prior = lp - _logsumexp(lp, 0)
        self.logp = np.log(self.p_grid)
        self.logq = np.log1p(-self.p_grid)
        self.I, self.J, self.K, self.M = int(I), int(J), int(K), int(M)
        self.ks = np.arange(1, self.K + 1)
        self._build()

    def _build(self) -> None:
        I, J, K, M = self.I, self.J, self.K, self.M
        Jext = J + 2 * K
        jj = np.arange(Jext + 1)

        # logW[i, j] = log E_prior[ p^i (1-p)^j ], the unnormalised posterior mass
        logW = np.empty((I + 3, Jext + 1))
        base = self.log_prior[None, :] + jj[:, None] * self.logq[None, :]
        for i in range(I + 3):
            logW[i] = _logsumexp(base + i * self.logp[None, :], axis=1)

        ks = self.ks
        # Myopic per-balloon value on the extended range i in 0..I+1, j in 0..J+K
        Je = J + K
        Vmyo = np.empty((I + 2, Je + 1))
        for i in range(I + 2):
            surv = np.exp(logW[i, jj[None, : Je + 1] + ks[:, None]] - logW[i, None, : Je + 1])
            Vmyo[i] = np.max(ks[:, None] * surv, axis=0)

        # Transition probabilities on the DP core i in 0..I, j in 0..J
        jcore = np.arange(J + 1)
        jv_idx = jcore[None, :] + (ks[:, None] - 1)     # (K, J+1): state j after a pop at v = j + v - 1
        jk_idx = jcore[None, :] + ks[:, None]           # (K, J+1): state j after surviving k = j + k
        Ppop = np.empty((I + 1, K, J + 1), dtype=np.float32)
        Psurv = np.empty((I + 1, K, J + 1), dtype=np.float32)
        for i in range(I + 1):
            Ppop[i] = np.exp(logW[i + 1, jv_idx] - logW[i, None, : J + 1])
            Psurv[i] = np.exp(logW[i, jk_idx] - logW[i, None, : J + 1])
        R = ks[None, :, None].astype(np.float32) * Psurv

        policy = np.zeros((M + 1, I + 1, J + 1), dtype=np.int8)
        policy[1] = np.argmax(R, axis=1) + 1
        V_prev = Vmyo.astype(np.float32)
        for m in range(2, M + 1):
            V_new = (m * Vmyo).astype(np.float32)
            for i in range(I + 1):
                after_pop = np.cumsum(Ppop[i] * V_prev[i + 1][jv_idx], axis=0)   # sum over v <= k
                after_surv = Psurv[i] * V_prev[i][jk_idx]
                Q = R[i] + after_pop + after_surv
                V_new[i, : J + 1] = np.max(Q, axis=0)
                policy[m, i] = np.argmax(Q, axis=0) + 1
            V_prev = V_new
        self.policy = policy

    def posterior_weights(self, i: int, j: int) -> np.ndarray:
        logpost = self.log_prior + i * self.logp + j * self.logq
        w = np.exp(logpost - logpost.max())
        return w / w.sum()

    def myopic_threshold(self, i: int, j: int) -> int:
        """argmax_k E_posterior[ k (1-p)^k ], used outside the table."""
        w = self.posterior_weights(i, j)
        Eq = np.exp(self.ks[:, None] * self.logq[None, :]) @ w
        return int(self.ks[np.argmax(self.ks * Eq)])


class bayes_dp(Strategy):
    """
    Bayes-optimal threshold policy (single player) with an opponent-modelling best response
    (head-to-head).

    SINGLE PLAYER
    - Per color, keep the exact censored-geometric sufficient statistic (pops, survived pumps).
    - Prior on p: uniform on [p_lo, p_hi] with relative density `tail` outside it (down to 0.005
      and up to 0.995), so probabilities outside the expected range can still be learned.
    - The threshold is looked up in a finite-horizon dynamic program (see _BayesDPTable) indexed
      by the sufficient statistic and the expected number of balloons of this color still to
      come, (N - id - 1) / #colors + 1. The table is built once per parameter set and cached at
      class level; look-ups are O(1).

    HEAD TO HEAD (detected automatically once obs.payout has two entries)
    - The opponent's threshold is reconstructed from the payouts: it is known exactly whenever
      they survive, and bounded below (k2 >= V if they popped with me, k2 > k if they popped
      alone). A per-color histogram with exponential forgetting tracks it; censored observations
      are spread over the feasible thresholds in proportion to the current histogram.
    - The pop probability is still learned from own observations only (unbiased). Under that
      posterior, the expected payoff of every threshold k against the opponent histogram is
          k > k2: (k + k2) E[q^k]      k < k2: k (E[q^k] - E[q^k2])      k = k2: k E[q^k]
      and k is drawn from a quantal response (softmax with temperature `temp` relative to the
      best payoff). temp = 0 is the pure best response, which is strongest against opponents
      that do not adapt but is itself exploitable by leapfrogging; the default 0.1 randomises
      just enough to be robust in self-play.
    """

    KEY = "bayes_dp"
    PARAMS = [("p_lo", float), ("p_hi", float), ("tail", float), ("max_k", int),
              ("forget", float), ("temp", float)]
    DEFAULTS = {"p_lo": 0.1, "p_hi": 0.9, "tail": 0.05, "max_k": 60, "forget": 0.7, "temp": 0.1}
    TABLE_I, TABLE_J, TABLE_M_MAX = 60, 1200, 120
    _TABLE_CACHE = {}

    def __init__(self, ctx: Context, rng: np.random.Generator, p_lo: float = 0.1, p_hi: float = 0.9,
                 tail: float = 0.05, max_k: int = 60, forget: float = 0.7, temp: float = 0.1):
        given = {"p_lo": p_lo, "p_hi": p_hi, "tail": tail, "max_k": max_k, "forget": forget, "temp": temp}
        # The name doubles as SQL table / file name, so keep it to [A-Za-z0-9_]
        suffix = "".join(f"_{k}{str(v).replace('.', 'p').replace('-', 'm')}"
                         for k, v in given.items() if v != self.DEFAULTS[k])
        super().__init__(name="bayes_dp" + suffix, ctx=ctx, rng=rng)
        if not (0.0 < p_lo < p_hi < 1.0) or not (0.0 < tail <= 1.0):
            raise ValueError("bayes_dp needs 0 < p_lo < p_hi < 1 and 0 < tail <= 1")
        max_k = int(min(max(max_k, 1), 120))
        self.num_colors = len(ctx.colors)
        self.N = ctx.num_balloons
        M = min(int(np.ceil(self.N / self.num_colors)) + 5, self.TABLE_M_MAX)
        key = (p_lo, p_hi, tail, max_k, M)
        if key not in bayes_dp._TABLE_CACHE:
            grid = np.linspace(0.005, 0.995, 199)
            log_prior = np.where((grid >= p_lo) & (grid <= p_hi), 0.0, np.log(tail))
            bayes_dp._TABLE_CACHE[key] = _BayesDPTable(grid, log_prior, I=self.TABLE_I, J=self.TABLE_J, K=max_k, M=M)
        self.table = bayes_dp._TABLE_CACHE[key]
        self.K = max_k
        self.state = {c: [0, 0] for c in ctx.colors}           # color -> [pops, survived pumps]

        # Head-to-head machinery
        self.forget = forget
        self.temp = temp
        self.multiplayer = False
        self.ks = np.arange(1, self.K + 1)
        self.k2s = np.arange(0, self.K + 1)
        self.opp_hist = {c: np.r_[0.0, np.full(self.K, 1.0 / self.K)] for c in ctx.colors}
        self._Qmat = np.exp(self.k2s[:, None] * self.table.logq[None, :])     # (K+1, G): (1-p)^t
        self._over = self.ks[:, None] > self.k2s[None, :]
        self._tie = self.ks[:, None] == self.k2s[None, :]

    # ------------------------------------------------------------------ actions
    def action(self, balloon: Balloon) -> int:
        i, j = self.state[balloon.color]
        if self.multiplayer:
            return self._action_head_to_head(balloon.color, i, j)
        t = self.table
        m = 1 + (self.N - balloon.id - 1) / self.num_colors      # expected balloons of this color left
        m = int(min(max(round(m), 1), t.M))
        if i <= t.I and j <= t.J:
            return int(t.policy[m, i, j])
        return t.myopic_threshold(i, j)

    def _action_head_to_head(self, color: str, i: int, j: int) -> int:
        Eq = self._Qmat @ self.table.posterior_weights(i, j)   # E[(1-p)^t], t = 0..K
        hist = self.opp_hist[color]
        pi = hist / hist.sum()
        ks, k2s = self.ks, self.k2s
        Eqk = Eq[ks][:, None]
        u = np.where(self._over, (ks[:, None] + k2s[None, :]) * Eqk, ks[:, None] * (Eqk - Eq[k2s][None, :]))
        u = np.where(self._tie, ks[:, None] * Eqk, u)
        U = u @ pi
        if self.temp <= 0:
            return int(ks[np.argmax(U)])
        w = np.exp((U - U.max()) / (max(U.max(), 1e-9) * self.temp))
        return int(self.rng.choice(ks, p=w / w.sum()))

    # ------------------------------------------------------------------ learning
    def update_beliefs(self, obs: Observation) -> None:
        st = self.state[obs.balloon_color]
        if obs.pop_time == 999:
            st[1] += max(int(obs.own_threshold), 0)
        else:
            st[0] += 1
            st[1] += int(obs.pop_time) - 1
        if len(obs.payout) == 2:
            self.multiplayer = True
            self._update_opponent(obs)

    def _update_opponent(self, obs: Observation) -> None:
        opp_name = next(n for n in obs.payout if n != self.name)
        P_opp, P_me, k = obs.payout[opp_name], obs.payout[self.name], obs.own_threshold
        revealed, bound = None, None
        if obs.pop_time != 999:                  # I popped, V is known
            if P_opp > 0:
                revealed = P_opp                 # opponent survived: k2 = P_opp
            else:
                bound = obs.pop_time             # opponent popped too: k2 >= V
        else:                                    # I survived
            if P_me > k:
                revealed = P_me - k              # both survived, I won (includes the tie: P_me = 2k)
            elif P_me == 0 and P_opp > 0:
                revealed = P_opp - k             # both survived, opponent won
            elif P_me == k:
                bound = k + 1                    # opponent popped: k2 > k
        hist = self.opp_hist[obs.balloon_color]
        hist *= self.forget
        if revealed is not None:
            hist[int(min(max(revealed, 0), self.K))] += 1.0
        elif bound is not None:
            L = int(min(bound, self.K))
            mass = hist[L:].sum()
            if mass > 1e-9:
                hist[L:] += hist[L:] / mass      # spread the censored observation to the right
            else:
                hist[L] += 1.0

