''' Helper functions for generating volcano plots '''

from mib.external import pd, np, plt
from mib.utils.interest import *

# Limits
def compute_xlim(data:pd.DataFrame, sets:list[str], padL:float=0.025, padR:float=0.025) -> tuple[float, float]:
    ''' 
    Get volcano plot x axis limits based on fold-change values in *data* for tests in *sets*
        
    Define left (*padL*) and right (*padR*) margin padding as fractions of the x-axis
    '''

    cols = [f"{s}.logfc" for s in sets]
    maxFC = data[cols].max(axis=None)
    minFC = data[cols].min(axis=None)
    
    rngFC = maxFC - minFC
    xmin = minFC - (rngFC * padL)
    xmax = maxFC + (rngFC * padR)

    return xmin, xmax

def compute_ylim(data:pd.DataFrame, sets:list[str], padT:float=0.025, padB:float=0.175) -> tuple[float, float]:
    '''
    Get volcano plot y axis limits based on p-values in *data* for tests in *sets*
        
    Define top (*padT*) and bottom (*padB*) margin padding as fractions of the y-axis
    '''

    maxP = data[[f"{s}.nlogp" for s in sets]].replace(np.inf, np.nan).max(axis=None)
    yrng = maxP / (1 - (padB + padT))

    ymin = maxP - (yrng * (1 - padT))
    ymax = ymin + yrng

    return ymin, ymax

# Thresholds
def draw_bounds(ax:plt.Axes, nlogp_thresh:float, fc_thresh:float,
                xmin:float=None, xmax:float=None, ymin=0, ymax:float=None, 
                annotate:bool=True, yArrow:float=0.1, yText:float=0.08,
                xNeg:float=0.5, xPos:float=0.5,
                neg_label:str="Depleted", pos_label:str="Enriched"):

    ''' 
    Draw significance threshold boundaries 
    * p-value (*NLOGP_THRESH*) on y-axis
    * fold-change (*fc_thresh*) on x-axis
    
    Annotate enrichment directionality (optional)
    '''

    if (xmin == None) or (xmax == None):
        xmin, xmax = ax.get_xlim()
    
    if (ymin == None) or (ymax == None):
        ymin, ymax = ax.get_ylim()
    
    # FC = 0
    ax.vlines(0, ymin=ymin, ymax=ymax, color="#545454", lw=0.8, zorder=1)

    # thresholds
    thresh_dict = dict(color="#545454", lw=0.8, ls="--", zorder=1)
    ax.axhline(nlogp_thresh, **thresh_dict)
    ax.vlines([-fc_thresh, fc_thresh], ymin=ymin, ymax=ymax, **thresh_dict)

    # fold-change annotations
    if annotate:

        # arrows
        arrow_dict = dict(
            arrowprops=dict(arrowstyle="->", lw=1, color="black"),
            transform=ax.transAxes, clip_on=False,
            xycoords=ax.get_xaxis_transform()
        )

        ax.annotate("", (xmax, yArrow), (fc_thresh, yArrow), **arrow_dict)
        ax.annotate("", (xmin, yArrow), (-fc_thresh, yArrow), **arrow_dict)

        # labels
        label_dict = dict(color="black", size=8.5, ha="center", va="top", 
                          style="italic", transform=ax.get_xaxis_transform())

        ax.text((xmax + fc_thresh) * xPos, yText, pos_label, **label_dict)
        ax.text((xmin - fc_thresh) * xNeg, yText, neg_label, **label_dict)

# Scatter Plot Annotation
def annotate_point(ax:plt.Axes, label:str, x:float, y:float, dX:float=0, dY:float=0,
                   ha:str="center", va:str="center", arrow:bool=True,
                   color:str="black", size:float=7.5, draw:bool=True):
    '''
    Add a text annotation (*label*) to point (*x*, *y*). 
    The text will be positioned *dX* points (unit) to the left, and 
    *dY* points (unit) to the right of (*x*, *y*).
    '''

    style_dict = dict(
        color=color, size=size, linespacing=1.25, clip_on=False,
        bbox=dict(ec="None", fc="None", boxstyle="square,pad=0")
    )

    if arrow:
        style_dict["arrowprops"] = dict(
            arrowstyle="->", lw=1, color="#333333",
            shrinkA=1, shrinkB=5
        )

    if draw:
        ax.annotate(label, (x, y), (dX, dY), textcoords="offset points", 
                    ha=ha, va=va, **style_dict)

# Volcano Plot
def draw_volcano(data:pd.DataFrame, sets:list[str], title:str,
                 filename:str, palette:dict[str, str], annot_args:dict[str, dict],
                 figsize:tuple[float, float], xmin:float, xmax:float, xticks:list[float]=None,
                 gaps:list[tuple[float, float]]=[], legend_loc:str="best",
                 pval_thresh:float=0.05/60, fc_thresh:float=1.5, alpha:float=0.8,
                 padL:float=0.125, padR:float=0.945, padT:float=0.86, padB:float=0.11,
                 padW:float=0.03, yArrow:float=-0.0875, yText:float=-0.11,
                 xNeg:float=0.5, xPos:float=0.5, annotate_x0:bool=True, yXlab:float=-0.025):

    # significance
    nlogp_thresh = -np.log10(pval_thresh)
    logfc_thresh = np.log2(fc_thresh)

    # Limits
    _, ymax = compute_ylim(data, sets, padT=0.05, padB=0.05)
    ymin = 0

    segments = [(-np.inf, xmin)] + gaps + [(xmax, np.inf)]

    nplots = len(gaps) + 1
    rngs = [0] * nplots
    for i in range(nplots):
        rngs[i] = (segments[i][1], segments[i+1][0])
        if (segments[i][1] < 0) and (segments[i+1][0]):
            mid = i

    wr = [(e - s) for s, e in rngs]

    # Figure
    fig, axes = plt.subplots(ncols=nplots, width_ratios=wr, sharey=True, squeeze=False, figsize=figsize)
    fig.subplots_adjust(left=padL, right=padR, top=padT, bottom=padB, wspace=padW)
    axes = axes[0]

    # # Scatter Plot
    handles = []
    for elt in sets:
        color, label = palette[elt]

        # coordinates
        x = data[f"{elt}.logfc"].values
        y = data[f"{elt}.nlogp"].values

        # colors
        ec = [color if ((p > nlogp_thresh) and (abs(fc) > logfc_thresh)) 
            else "white" for fc, p in zip(x, y)]
        fc = [(c, alpha) for c in ec]

        # plot
        for ax in axes:
            ax.scatter(x, y, fc=fc, ec=color, s=35, lw=0.8, zorder=3)

        # label (for legend)
        h = axes[0].scatter([1e10], [1e10], fc=(color, alpha), ec=color, s=35, lw=0.8, label=label)
        handles.append(h)

    # Significance
    gw = [(e - s) for s, e in gaps]
    for i, ax in enumerate(axes):
        left = xmin + sum(gw[:i]) - (padW * np.mean(wr) * len(gw[:i]))
        right = xmax - sum(gw[i:]) + (padW * np.mean(wr) * len(gw[i:]))
        draw_bounds(ax, nlogp_thresh, logfc_thresh, xmin=left, xmax=right,
                    ymin=0, ymax=ymax, yArrow=yArrow, yText=yText, 
                    xPos=xPos, xNeg=xNeg, annotate=(annotate_x0 and (i==mid)))

    # Axis Labels
    midX = (padL + padR) / 2
    fig.suptitle(title, size=12.5, x=midX, y=0.9)
    fig.supxlabel(r'$\mathrm{log_2(Fold\ Change)}$', size=11, x=midX, y=yXlab)
    axes[0].set_ylabel(r'$\mathrm{-log_{10}(}p\mathrm{)}$', size=11, labelpad=6)

    # Legend
    if legend_loc.endswith("left"): axL = axes[0]
    elif legend_loc.endswith("right"): axL = axes[-1]
    else: axL = axes[i]
    axL.legend(handles=handles, loc=legend_loc, fontsize=8, handletextpad=0.5)

    # Axis Spines
    axes[0].spines[["top", "right"]].set_visible(False)
    for ax in axes[1:]:
        ax.spines[["top", "left", "right"]].set_visible(False)
        ax.tick_params(axis="y", length=0)

    # # divider
    div_args = dict(marker=[(-1, -1), (1, 1)], ls="none", 
                    color="black", ms=10, mew=1, clip_on=False)
    for i, ax in enumerate(axes):
        if i < (nplots - 1): ax.plot(1, 0, transform=ax.transAxes, **div_args)
        if i > 0: ax.plot(0, 0, transform=ax.transAxes, **div_args)

    # # Axis Limits
    for ax, (s, e) in zip(axes, rngs):
        ax.set_xlim(s, e)
        ax.set_ylim(ymin, ymax)

        if xticks != None:
            ax.set_xticks([x for x in xticks if (x > s) and (x < e)])

        ax.set_facecolor("none")

    # Annotate Points
    signif = get_significant(data, sets, nlogp_thresh, logfc_thresh)
    for s, b, x, y in signif[signif["label"].isin(annot_args)].values:

        # find interval
        for ax, (i, j) in zip(axes, rngs):
            if (x >= i) and (x <= j):
                annotate_point(ax, b, x, y, **annot_args[b][s])
                continue

    # save
    fig.savefig(filename, bbox_inches="tight", dpi=1024)
