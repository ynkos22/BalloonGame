"""
Figures for game logs.

Nothing here computes a metric -- that is metrics.py's job. Every plot function
takes an already-prepared DataFrame, returns a matplotlib Figure, and never calls
plt.show() or touches global pyplot state, so the same function works from a
notebook, a script, or a batch regeneration of the whole plots folder.

save_figure() is the only thing that knows about the filesystem.
"""

import hashlib
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import NullFormatter, ScalarFormatter

import metrics
from paths import GAME_LOG_PATH, PLOT_PATH

# PALETTE
# Categorical slots, in the fixed order they must be assigned in -- the ordering is
# what keeps adjacent pairs separable under colour-vision deficiency, so slots are
# handed out in order and never cycled or reshuffled.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

INK = {
    "surface": "#fcfcfb",
    "primary": "#0b0b0b",
    "secondary": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
}

LINEWIDTH = 1.5
FIGSIZE = (9, 5)
DPI = 150

_color_assignment = {}


# Applies the chart chrome: hairline solid grid, recessive axes, no top/right spines
def style_axes(ax) -> None:
    ax.set_facecolor(INK["surface"])
    ax.grid(True, color=INK["grid"], linewidth=0.8, linestyle="-")
    ax.set_axisbelow(True)

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK["axis"])
        ax.spines[side].set_linewidth(0.8)

    ax.tick_params(colors=INK["muted"], labelsize=9, length=0)
    ax.xaxis.label.set_color(INK["secondary"])
    ax.yaxis.label.set_color(INK["secondary"])


def new_figure(title: str, xlabel: str, ylabel: str, figsize=FIGSIZE):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_facecolor(INK["surface"])
    style_axes(ax)

    ax.set_title(title, color=INK["primary"], fontsize=12, loc="left", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig, ax


# Maps strategy name -> colour, assigned once over EVERY strategy present in the log
# folder rather than per figure. Plotting a subset therefore leaves the survivors on
# the colours the reader already learned, instead of repainting them.
def color_for(strategy_name: str, game_log_path: str = GAME_LOG_PATH) -> str:
    if not _color_assignment:
        names = set()
        for game_id in metrics.list_runs(game_log_path):
            csv_path = os.path.join(game_log_path, f"game_{game_id}_log.csv")
            names.update(pd.read_csv(csv_path, usecols=["strategy_name"])["strategy_name"].unique())

        for slot, name in enumerate(sorted(names)):
            _color_assignment[name] = PALETTE[slot % len(PALETTE)]

    if strategy_name not in _color_assignment:
        _color_assignment[strategy_name] = PALETTE[len(_color_assignment) % len(PALETTE)]

    return _color_assignment[strategy_name]


# Names the series at the end of its own line, so identity survives without the legend.
# Three of the palette slots sit under 3:1 against the surface, so the label itself
# stays in text ink and a colour chip beside it carries the identity.
def end_label(ax, x, y, text: str, color: str) -> None:
    ax.plot([x], [y], marker="o", markersize=4, color=color, markeredgecolor=INK["surface"], markeredgewidth=1.5, zorder=5)
    ax.annotate(
        f" {text}",
        xy=(x, y),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        color=INK["secondary"],
    )


def finish(fig, ax, legend: bool = True) -> None:
    if legend:
        leg = ax.legend(frameon=False, fontsize=9, loc="upper left")
        for text in leg.get_texts():
            text.set_color(INK["secondary"])
    fig.tight_layout()


# PLOTS

# Cumulative PnL per strategy
def plot_pnl(df: pd.DataFrame, meta: dict):
    fig, ax = new_figure(
        f"Cumulative PnL  ·  game {meta['game_id']}",
        "balloon number",
        "cumulative PnL",
    )

    for name, group in df.groupby("strategy_name"):
        group = group.sort_values("balloon_id")
        color = color_for(name)
        ax.plot(group["balloon_id"], group["cum_payoff"], color=color, linewidth=LINEWIDTH, label=name)
        end_label(ax, group["balloon_id"].iloc[-1], group["cum_payoff"].iloc[-1], name, color)

    finish(fig, ax)
    return fig


# Cumulative regret per strategy: realised against the benchmark (solid) and expected
# / pseudo-regret (dashed). Both are in payoff units, so they share one axis honestly.
# Colour carries the strategy, line style carries which regret -- so the two never rely
# on hue alone to be told apart.
def plot_regret(df: pd.DataFrame, meta: dict, which=("regret", "pseudo_regret")):
    benchmark = "best response" if meta["multiplayer"] else "oracle"

    fig, ax = new_figure(
        f"Cumulative regret vs {benchmark}  ·  game {meta['game_id']}",
        "balloon number",
        "cumulative regret",
    )

    styles = {"regret": ("-", "realised"), "pseudo_regret": ("--", "expected (pseudo)")}

    for name, group in df.groupby("strategy_name"):
        group = group.sort_values("balloon_id")
        color = color_for(name)

        for kind in which:
            linestyle, label = styles[kind]
            column = "cum_regret" if kind == "regret" else "cum_pseudo_regret"
            ax.plot(
                group["balloon_id"],
                group[column],
                color=color,
                linewidth=LINEWIDTH,
                linestyle=linestyle,
                label=f"{name} — {label}",
            )

        last = "cum_regret" if "regret" in which else "cum_pseudo_regret"
        end_label(ax, group["balloon_id"].iloc[-1], group[last].iloc[-1], name, color)

    ax.axhline(0, color=INK["axis"], linewidth=0.8)
    finish(fig, ax)
    return fig


# Threshold convergence, one panel per balloon colour.
# Raw thresholds span 1 to 1000 (the exploration threshold), so the y-axis is log --
# clipping would hide exactly the exploration phase this plot exists to show.
def plot_thresholds(df: pd.DataFrame, meta: dict, window: int = 25):
    color_map = meta["color_map"]
    colors = sorted(color_map)
    strategies = sorted(df["strategy_name"].unique())

    fig, axes = plt.subplots(1, len(colors), figsize=(4 * len(colors), 4), dpi=DPI, sharey=True)
    fig.patch.set_facecolor(INK["surface"])
    axes = np.atleast_1d(axes)

    for ax, balloon_color in zip(axes, colors):
        style_axes(ax)
        ax.set_yscale("log")
        ax.set_title(f"{balloon_color}  (p = {color_map[balloon_color]})", color=INK["primary"], fontsize=10, loc="left")
        ax.set_xlabel("balloon number")

        panel = df[df["balloon_color"] == balloon_color]
        for name in strategies:
            group = panel[panel["strategy_name"] == name].sort_values("balloon_id")
            smoothed = group["threshold"].rolling(window, min_periods=1).median()
            ax.plot(group["balloon_id"], smoothed, color=color_for(name), linewidth=LINEWIDTH, label=name)

        # A log axis defaults to 6x10^0 style labels, which is unreadable for the small
        # integers thresholds actually take.
        ticks = [t for t in (1, 2, 3, 5, 10, 30, 100, 300, 1000) if t <= max(3, panel["threshold"].max())]
        ax.set_yticks(ticks)
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())

        optimal = metrics.optimal_threshold(color_map[balloon_color])
        ax.axhline(optimal, color=INK["muted"], linewidth=0.8, linestyle="--")
        ax.annotate(
            f"optimal {optimal}",
            xy=(0, optimal),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
            color=INK["muted"],
        )

    axes[0].set_ylabel(f"threshold (rolling median, window {window})")
    leg = axes[0].legend(frameon=False, fontsize=9, loc="upper right")
    for text in leg.get_texts():
        text.set_color(INK["secondary"])

    fig.suptitle(f"Threshold convergence  ·  game {meta['game_id']}", color=INK["primary"], fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    return fig


# Mean cumulative regret across seeds, with a +/- 1 standard deviation band.
# dfs are the prepared frames for the same strategy set under different balloon seeds.
def plot_regret_across_seeds(dfs: list[pd.DataFrame], meta: dict, column: str = "cum_pseudo_regret"):
    label = "expected (pseudo)" if "pseudo" in column else "realised"
    benchmark = "best response" if meta["multiplayer"] else "oracle"

    fig, ax = new_figure(
        f"Mean cumulative regret vs {benchmark}, {len(dfs)} seeds × {meta['num_balloons']} balloons  ·  {label}",
        "balloon number",
        "cumulative regret",
    )

    summary = metrics.aggregate_seeds(dfs, column)

    for name, group in summary.groupby("strategy_name"):
        group = group.sort_values("balloon_id")
        color = color_for(name)

        ax.fill_between(
            group["balloon_id"],
            group["mean"] - group["std"],
            group["mean"] + group["std"],
            color=color,
            alpha=0.15,
            linewidth=0,
        )
        ax.plot(group["balloon_id"], group["mean"], color=color, linewidth=LINEWIDTH, label=f"{name} (n={int(group['count'].iloc[0])})")
        end_label(ax, group["balloon_id"].iloc[-1], group["mean"].iloc[-1], name, color)

    ax.axhline(0, color=INK["axis"], linewidth=0.8)
    finish(fig, ax)
    return fig


# SAVING

# Canonical filename for a figure.
#
#   {kind}__{scope}__{strategies}__seed{seed}__n{balloons}__cfg{hash}.png
#
# Fields are separated by DOUBLE underscore because strategy names already contain
# single ones (thompson_sampling, explore_exploit_0_2), so a single underscore cannot
# be a field boundary. Strategies join on "-vs-" head to head and "+" otherwise.
# cfg is a short hash of the colour map: it decides the regret benchmark, so the same
# strategies under different pop probabilities are genuinely different plots and must
# not overwrite each other.
#
# Names are deterministic rather than timestamped -- re-running overwrites in place, so
# the plots folder stays a mirror of current results instead of accumulating duplicates.
def canonical_name(
    kind: str,
    strategies: list[str],
    scope: str,
    seed=None,
    num_seeds=None,
    num_balloons=None,
    color_map: dict = None,
    ext: str = "png",
) -> str:
    joiner = "-vs-" if scope == "h2h" else "+"
    parts = [kind, scope, joiner.join(sorted(strategies))]

    if seed is not None:
        parts.append(f"seed{seed}")
    elif num_seeds is not None:
        parts.append(f"seeds{num_seeds}")

    if num_balloons is not None:
        parts.append(f"n{num_balloons}")

    if color_map is not None:
        digest = hashlib.sha1(json.dumps(color_map, sort_keys=True).encode()).hexdigest()
        parts.append(f"cfg{digest[:6]}")

    return "__".join(parts) + "." + ext


# Writes a figure under its canonical name and returns the path
def save_figure(fig, kind: str, meta: dict, num_seeds=None, plot_path: str = PLOT_PATH) -> str:
    strategies = meta["strategies"]
    scope = "h2h" if meta["multiplayer"] else "single"
    if num_seeds is not None:
        scope = "agg"

    filename = canonical_name(
        kind,
        strategies,
        scope,
        seed=meta["seed"] if num_seeds is None else None,
        num_seeds=num_seeds,
        num_balloons=meta["num_balloons"],
        color_map=meta["color_map"],
    )

    os.makedirs(plot_path, exist_ok=True)
    out = os.path.join(plot_path, filename)
    fig.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return out


# DRIVERS

# Every per-game figure for one run
def plot_run(game_id: str, game_log_path: str = GAME_LOG_PATH, plot_path: str = PLOT_PATH) -> list[str]:
    df, meta = metrics.prepared_run(game_id, game_log_path)

    written = [
        save_figure(plot_pnl(df, meta), "pnl", meta, plot_path=plot_path),
        save_figure(plot_regret(df, meta), "regret", meta, plot_path=plot_path),
        save_figure(plot_thresholds(df, meta), "thresholds", meta, plot_path=plot_path),
    ]
    return written


# Regenerates the whole plots folder: per-game figures, plus one across-seed figure for
# each set of strategies that was run under more than one balloon seed.
def plot_all(game_log_path: str = GAME_LOG_PATH, plot_path: str = PLOT_PATH) -> list[str]:
    written = []
    by_strategies = {}

    for game_id in metrics.list_runs(game_log_path):
        df, meta = metrics.prepared_run(game_id, game_log_path)
        written.extend(plot_run(game_id, game_log_path, plot_path))
        by_strategies.setdefault(tuple(sorted(meta["strategies"])), []).append((df, meta))

    for runs in by_strategies.values():
        # One game per seed. The same seed and strategies is by construction the same
        # game, so a log saved twice under two different ids (the multiplayer game_id
        # gained a separator) must not be averaged in twice.
        by_seed = {}
        for df, meta in runs:
            by_seed.setdefault(meta["seed"], (df, meta))

        runs = list(by_seed.values())
        if len(runs) < 2:
            continue

        dfs = [df for df, _ in runs]
        meta = dict(runs[0][1])
        meta["seed"] = None

        for column, kind in (("cum_pseudo_regret", "pseudo_regret"), ("cum_regret", "regret")):
            fig = plot_regret_across_seeds(dfs, meta, column)
            written.append(save_figure(fig, kind, meta, num_seeds=len(dfs), plot_path=plot_path))

    return written
