''' Code to generate Figure 4 '''

from mib.external import os, pd, plt
from mib.utils.constants import *
from mib.utils.interest import *
from mib.draw.trend import *

os.makedirs(f"{PROJECT_DIR}/analysis/figures", exist_ok=True)

# load results
aim2 = pd.read_csv(f"{PROJECT_DIR}/analysis/aim2/aim2_ztests_foldchange.tsv", sep="\t")

prop_cols = [f"prop.{d}" for d in DAY_SETS]
pval_thresh = 0.05 / (3 * 20)
fc_thresh = 1.5

# non-empty behaviors
todraw = aim2[(aim2["agg"] > 0) & 
              (aim2["behavior"] != "Uncertain") & 
              (aim2["behavior"] != "Unknown")]
todraw["label"] = todraw["behavior"].apply(lambda x: BEHAVIORS[x].replace("\n", ""))

# sort by variation
todraw["std"] = todraw[DAY_SETS].std(axis=1)
todraw["mean"] = todraw[prop_cols].mean(axis=1)
todraw = todraw.sort_values("std", ascending=False).set_index("label", drop=False)

m = len(DAY_SETS)
cld_df, adj = get_cld(todraw, DAY_SETS, nlogp_thresh=-np.log10(pval_thresh), logfc_thresh=np.log2(fc_thresh))
yvals = todraw[prop_cols]
yvals.columns = range(m)

# Figure
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(10, 6), sharex=True, layout="constrained")
fig.supylabel("Proportion of Time Budget", size=10)

axes = axes.flatten()

# For each behavior
for ax, l in zip(axes, todraw.index):
    draw_trend(ax, name=l, nx=m, yvals=yvals.loc[l], clds=cld_df.loc[l], adj=adj[l], 
               sets=DAY_SETS, palette=DAY_PALETTE, labely=False)

# save figure
fig.savefig(f"{PROJECT_DIR}/analysis/figures/fig4_aim2_longitudinal.png", 
            bbox_inches="tight", dpi=1024)
