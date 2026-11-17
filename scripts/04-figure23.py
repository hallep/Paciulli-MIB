''' Code to generate volcano plots (Figures 2 and 3) '''

from mib.external import os, pd
from mib.utils.constants import *
from mib.draw.volcano import *

os.makedirs(f"{PROJECT_DIR}/analysis/figures", exist_ok=True)

# ===== Figure 2 ===== #

# load results
aim1 = pd.read_csv(f"{PROJECT_DIR}/analysis/aim1/aim1_ztests_foldchange.tsv", sep="\t")

aim1_annots = {
    "Feeding" : {
        "Jun6" : dict(dX=20, ha="left"),
        "Jun7" : dict(dX=20, ha="left"),
        "Jun8" : dict(dX=10, dY=30, va="bottom"),
    },
    "Hand auto-\ngrooming" : {
        "Jun6" : dict(dX=20, ha="left"),
        "Jun7" : dict(dX=-15, dY=45, va="bottom"),
        "Jun8" : dict(dX=-20, ha="right"),
    },
    "Mouth auto-\ngrooming" : {
        "Jun6" : dict(dX=20, dY=-10, ha="left"),
        "Jun7" : dict(dX=-65, dY=100, va="bottom"),
        "Jun8" : dict(dX=-20, ha="right"),
    },
    "Resting" : {
        "Jun6" : dict(dX=-35, dY=30, ha="right", va="bottom"),
        "Jun7" : dict(dY=20, ha="right", va="bottom"),
        "Jun8" : dict(dX=5, dY=15, ha="left", va="bottom"),
    },
    "Traveling" : {
        "Jun6" : dict(dX=5, dY=-15, ha="left", va="top"),
        "Jun7" : dict(dY=20, va="bottom"),
        "Jun8" : dict(dY=20, va="bottom"),
    },
}

draw_volcano(
    data=aim1, sets=DAY_SETS, title="Behavioral Enrichment", figsize=(8.5, 5), 
    filename=f"{PROJECT_DIR}/analysis/figures/fig2_aim1_volcano.png",
    palette=DAY_PALETTE, annot_args=aim1_annots, gaps=[(-23, -7)], 
    legend_loc="upper left", xmin=-34.5, xmax=4.5, xPos=0.5, xNeg=0.7
)

# ===== Figure 3 ===== #

# load results
aim2 = pd.read_csv(f"{PROJECT_DIR}/analysis/aim2/aim2_ztests_foldchange.tsv", sep="\t")

aim2_annots = {
    "Feeding" : {
        "Jun6.v.Jun7" : dict(dX=5, dY=15, ha="left", va="bottom"),
        "Jun7.v.Jun8" : dict(dX=5, dY=15, ha="left", va="bottom"),
        "Jun6.v.Jun8" : dict(dY=20, va="bottom"),
    },
    "Hand auto-\ngrooming" : {
        "Jun6.v.Jun7" : dict(dX=20, ha="left"),
        "Jun7.v.Jun8" : dict(dX=5, dY=15, ha="left", va="bottom"),
        "Jun6.v.Jun8" : dict(dX=20, ha="left"),
    },
    "Resting" : {
        "Jun6.v.Jun7" : dict(dX=-5, dY=15, ha="right", va="bottom"),
        "Jun7.v.Jun8" : dict(dX=20, ha="left"),
        "Jun6.v.Jun8" : dict(dY=-20, va="top"),
    },
}

draw_volcano(
    data=aim2, sets=PAIR_SETS, title="Pairwise Differences in Behavior",
    figsize=(8.5, 5), filename=f"{PROJECT_DIR}/analysis/figures/fig3_aim2_volcano.png",
    palette=PAIR_PALETTE, annot_args=aim2_annots, gaps=[(-22, -8), (8, 22)],
    legend_loc="upper right", xmin=-34, xmax=34, xticks=list(range(-30, 35, 5)), 
    annotate_x0=False, yXlab=0.015
)
