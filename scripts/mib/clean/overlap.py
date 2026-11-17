''' Helper functions for managing time intervals '''

from mib.external import pd, np

# Overlaps
def find_overlaps(df:pd.DataFrame, colS:str, colE:str) -> tuple[pd.DataFrame, pd.DataFrame, list[tuple]]:
    '''
    Identify overlapping intervals
    
    Interval boundaries are defined by columns *colS* and *colE* in DataFrame *df*

    Returns:
    * DataFrame: intervals that do not overlap
    * DataFrame: intervals that do overlap at least one other interval
    * list of tuples: row indices of overlapping intervals
    '''

    idxs = df.sort_values([colS, colE]).index.values

    bad = []
    ovlps = []
    for i in range(1, len(idxs)):
        j = idxs[i-1]
        k = idxs[i]

        if df.at[j, colE] >= df.at[k, colS]:
            bad.extend([j, k])
            ovlps.append((j, k))

    dfOvlp = df.loc[bad].drop_duplicates()
    dfDiscrete = df.loc[df.index.difference(dfOvlp.index)]
    return dfDiscrete, dfOvlp, ovlps

def merge_intervals(df:pd.DataFrame, colS:str, colE:str) -> pd.DataFrame:
    '''
    Merge overlapping intervals
    
    Interval boundaries are defined by columns *colS* and *colE* in DataFrame *df*
    '''

    tmp = df.sort_values(colS).reset_index()
    tmp.loc[0, "InPrev"] = False
    tmp.loc[1: ,"InPrev"] = tmp.loc[1:, colS].values > (tmp.loc[:len(tmp)-2, colE] + pd.Timedelta(seconds=1)).values
    tmp["GrpCount"] = tmp["InPrev"].cumsum()
    return tmp.groupby("GrpCount").agg({colS : np.min, colE : np.max}).reset_index()

def merge_overlapping(df:pd.DataFrame, colS:str, colE:str) -> pd.DataFrame:
    '''
    Recursively merge overlapping intervals until all intervals are discrete

    Interval boundaries are defined by columns *colS* and *colE* in DataFrame *df*
    '''

    dfM = merge_intervals(df, colS, colE)
    dfDiscrete, dfOvlp, _ = find_overlaps(dfM, colS, colE)

    if dfOvlp.empty:
        return dfDiscrete

    return merge_overlapping(pd.concat([dfDiscrete, dfOvlp]), colS, colE)

def split_overlapping(df:pd.DataFrame, colS:str, colE:str) -> pd.DataFrame:
    '''
    Split overlapping intervals

    Interval boundaries are defined by columns *colS* and *colE* in DataFrame *df*
    '''

    dfDiscrete, dfOvlp, ovlps = find_overlaps(df, colS, colE)

    if dfOvlp.empty:
        return df

    iS = list(df.columns).index(colS)
    iE = list(df.columns).index(colE)

    split_dfs = [dfDiscrete] + [pd.DataFrame()] * len(ovlps)

    for i, (j, k) in enumerate(ovlps):

        # fully encompasses
        if (df.at[j, colS] <= df.at[k, colS]) and (df.at[j, colE] >= df.at[k, colE]):
            tmp = df.loc[[j, k, j]]
            tmp.iat[0, iE] = df.at[k, colS] - pd.Timedelta(seconds=1)
            tmp.iat[2, iS] = df.at[k, colE] + pd.Timedelta(seconds=1)

        # partial overlap
        else:
            tmp = df.loc[[j, k]]
            tmp.iat[0, iE] = df.at[k, colS] - pd.Timedelta(seconds=1)

        split_dfs[i+1] = tmp.reset_index(drop=True)

    return split_overlapping(pd.concat(split_dfs, ignore_index=True), colS, colE)
