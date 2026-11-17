''' Code to generate Figure 1 '''

from mib.external import os, pd, np, plt
from mib.utils.constants import *

os.makedirs(f"{PROJECT_DIR}/analysis/figures", exist_ok=True)

series = DAY_SETS + ["agg"]

# load data
secs = pd.read_csv(f"{PROJECT_DIR}/data/budgets/MIB_Agatha_budgets_seconds.tsv", sep="\t")
props = pd.read_csv(f"{PROJECT_DIR}/data/budgets/MIB_Agatha_budgets_proportions.tsv", sep="\t")
data = props[series].values

# colorbar limits
biologic = props[props["behavior"].isin(["Uncertain", "Unknown"]) == False][series]
vmin = biologic.min(axis=None)
vmax = biologic.max(axis=None)

# labels
props["labels"] = props["behavior"].apply(lambda x: BEHAVIORS[x].replace("-\n", "-").replace("\n", " ") if x in BEHAVIORS else x)
labels = secs[series].values

# Figure
fig, ax = plt.subplots(figsize=(7, 6), layout="constrained")

# Heatmap
hm = ax.imshow(data, cmap="YlGn", vmin=0, vmax=0.043, aspect="auto")

# colorbar
cb = fig.colorbar(hm, ax=ax, pad=0.03, fraction=0.15, aspect=30, extend="max")
cb.set_label("Proportion of Time (seconds)", size=9.75, rotation=270, labelpad=15)
cb.ax.tick_params(axis="y", labelsize=8)

# Data Labels
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        p = data[i, j]
        if p > 0:
            c = "white" if (p > 0.035) else "black"
            ax.text(j, i, f"{labels[i, j]:,}", ha="center", 
                    va="center", size="8", color=c, linespacing=0)

# Axis
ax.set_title("Time Budgets (seconds)", size=10.5)

# tick labels
ax.set_xticks(range(data.shape[1]), labels=[DAY_PALETTE[s][1] for s in series], size=10)
ax.set_yticks(range(data.shape[0]), labels=props["labels"].values, size=9.5)
for i, t in enumerate(ax.get_yticklabels(minor=False)):
    if data[i].sum() == 0:
        t.set_fontstyle("italic")

# borders
ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
ax.tick_params(axis="both", which="minor", length=0)
ax.grid(which="minor", color="white", linestyle="-", linewidth=1.5)

# save figure
fig.savefig(f"{PROJECT_DIR}/analysis/figures/fig1_budget_summary.png", 
            bbox_inches="tight", dpi=1024)
