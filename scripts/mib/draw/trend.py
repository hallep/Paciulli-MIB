''' Helper functions for visualizing longitudinal trends '''

from mib.external import pd, plt
from mib.utils.interest import *

def get_color(yvals:pd.Series, adj:dict[str, bool]) -> str:
    ''' Get color based on monotonicity '''

    vals = yvals.copy()

    for i in vals.index[:-1]:
        if not adj[i]:
            vals.at[i] = vals.at[i+1]

    if vals.is_monotonic_increasing:
        return "#669900"
    
    if vals.is_monotonic_decreasing:
        return "#FF3300"
    
    if vals.values[0] < vals.values[1]:
        return "#9900CC"

    return "#0033CC"


def draw_trend(ax:plt.Axes, name:str, nx:float, yvals:pd.Series, clds:pd.Series,
               adj:dict[int, bool], sets:list[str], palette:dict[str, tuple[str, str]], 
               labely:bool=False):
    ''' Plot longitudinal change '''

    color = get_color(yvals, adj)

    # mean line
    ax.axhline(yvals.mean(), color="#545454", lw=1, ls="--", zorder=1)

    # Lines
    for i in range(nx-1):
        y1 = yvals.loc[i]
        y2 = yvals.loc[i+1]

        ls = "-" if adj[i] else "--"
        lw = 2 if adj[i] else 1.5

        ax.plot([i, i+1], [y1, y2], color=color, ls=ls, lw=lw, zorder=3)

    # Points
    for i, y in enumerate(yvals):
        if y == 0:
            ax.scatter(i, y, marker="o", ec=color, fc="white", zorder=5)

    # annotate CLD
    mid = (yvals.max() + yvals.min()) / 2
    for i in range(nx):
        y = yvals.loc[i]
        dXY = (0, -7) if (y > mid) else (0, 7)
        va = "top" if (y > mid) else "bottom"
        ax.annotate(clds.loc[i], (i, y), dXY, ha="center", va=va,
                    textcoords="offset points", size=9.5, weight="bold")

    # Axes
    ax.set_title(name, size=10)

    if labely:
        ax.set_ylabel("Proportion of Time Budget", size=9)

    # x ticks
    ax.set_xticks(range(nx), labels=[palette[e][1] for e in sets])
    ax.tick_params(axis="x", labelsize=10)
    ax.set_xlim(-0.25, nx - 0.75)

    # y ticks
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.tick_params(axis="y", labelsize=8)
    ax.yaxis.get_offset_text().set_fontsize(8)

    ax.spines[["top", "right"]].set_visible(False)
