''' Identify items of interest '''

from mib.external import pd, np, sp
from mib.utils.constants import BEHAVIORS

# Significant Results
def get_significant(data:pd.DataFrame, sets:list[str], nlogp_thresh:float, logfc_thresh:float) -> pd.DataFrame:
    
    # stack sets
    signif = pd.concat(
        [data[["behavior", f"{s}.nlogp", f"{s}.logfc"]].rename(
            columns={f"{s}.nlogp" : "nlogp", f"{s}.logfc" : "logfc"}
        ) for s in sets], axis=0, keys=sets, names=["set", "idx"]
    ).reset_index(level=0)

    # filter significant
    signif = signif[
        (signif["behavior"].isin(["Uncertain", "Unknown"]) == False) & 
        (signif["nlogp"] > nlogp_thresh) & (signif["nlogp"] != np.inf) & 
        (signif["logfc"].abs() > logfc_thresh)
    ].sort_values(by=["behavior", "set"], ignore_index=True)

    signif["label"] = signif["behavior"].apply(lambda x: BEHAVIORS[x])

    return signif[["set", "label", "logfc", "nlogp"]]

# Compact Letter Display
def get_cld(data:pd.DataFrame, sets:list, nlogp_thresh:float, logfc_thresh:float) -> tuple[pd.DataFrame, dict[str, list[bool]]]:
    
    m = len(sets)
    clds = {}
    adj = {}

    for l in data.index:
        mat = np.ones((m, m))
        adj[l] = [False] * (m - 1)

        for i in range(m):
            for j in range(m):
                if i == j: continue

                # pair
                p1, p2 = min(i, j), max(i, j)

                # is significant?
                p = data.at[l, f"{sets[p1]}.v.{sets[p2]}.nlogp"]
                fc = data.at[l, f"{sets[p1]}.v.{sets[p2]}.logfc"]
                s = (p > nlogp_thresh) and (abs(fc) > logfc_thresh)

                # matrix
                if s: mat[i, j] = 0.01

                # adjacent
                if i + 1 == j: adj[l][i] = s

        clds[l] = sp.compact_letter_display(mat, alpha=0.05).str.strip()

    cld_df = pd.concat(clds.values(), axis=1, keys=clds.keys()).T
    return cld_df, adj
