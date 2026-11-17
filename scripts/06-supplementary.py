''' Code to generate supplementary tables and figures '''

from mib.external import os, pd, np
from mib.utils.constants import *
from mib.clean.overlap import merge_overlapping

os.makedirs(f"{PROJECT_DIR}/analysis/supplement", exist_ok=True)

# ===== Filtering Process ===== #

convert = {
    "date" : pd.to_datetime,
    "action_start_time" : pd.to_datetime,
    "action_end_time" : pd.to_datetime,
    "video_start_time" : pd.to_datetime,
    "video_end_time" : pd.to_datetime,
}
cols = ["day", "camera", "video_file", "code_idx", "action_idx", "action"] + list(convert)

def get_tsv(filename:str) -> pd.DataFrame:
    return pd.read_csv(
        f"{PROJECT_DIR}/data/cleaned/{filename}.tsv", sep="\t", converters=convert,
        usecols=lambda c: (c in cols) or (str(c).startswith("Which action?")), 
)

df0 = get_tsv("MIB_Agatha_observations_v0_raw")
df1 = get_tsv("MIB_Agatha_observations_v1_valid_entries")
dfV = get_tsv("MIB_Agatha_observations_v2a_coding_known")
dfAgree = get_tsv("MIB_Agatha_observations_v2b_coding_agreement_entries")
df2 = get_tsv("MIB_Agatha_observations_v2_coding_agreement_videos")
df3 = get_tsv("MIB_Agatha_observations_v3_fa_seen_videos")
df4 = get_tsv("MIB_Agatha_observations_v4_all_actions")
df5 = get_tsv("MIB_Agatha_observations_v5_valid_actions")
df6 = get_tsv("MIB_Agatha_observations_v6_non_overlapping_actions")

# ----- Figure S1 ----- #

def get_lengths(df:pd.DataFrame, element:str) -> pd.DataFrame:
    colS = f"{element}_start_time"
    colE = f"{element}_end_time"
    colL = f"{element}_length"

    dfM = merge_overlapping(df, colS, colE)
    dfM[colL] = dfM[colE] - dfM[colS] + pd.Timedelta(seconds=1)

    return dfM

def process_video(df:pd.DataFrame, video_col:str="code_idx") -> tuple[pd.DataFrame, int, int, pd.Timedelta, int]:

    dfM = get_lengths(df, "video")
    aCols, = np.where(df.columns.str.startswith("Which action?"))

    nEntries = len(df)
    nVideos = len(df[video_col].unique())
    vLengths = dfM["video_length"].sum()
    nActions = df.iloc[:, aCols].notna().sum(axis=None)

    return dfM, nEntries, nVideos, vLengths, nActions

def process_action(df:pd.DataFrame) -> tuple[pd.DataFrame, int, pd.Timedelta, int, pd.Timedelta]:
    dfM = get_lengths(df, "video")

    nVideos = len(df["video_file"].unique())
    vLengths = dfM["video_length"].sum()
    nActions = len(df)
    
    if ("action_start_time" in df.columns) and ("action_end_time" in df.columns):
        aLengths = (df["action_end_time"] - df["action_start_time"]).sum() + pd.Timedelta(seconds=1)
    else:
        aLengths = pd.NaT

    return dfM, nVideos, vLengths, nActions, aLengths

dfM0, ne0, nv0, vl0, na0 = process_video(df0, "video_file")
dfM1, ne1, nv1, vl1, na1 = process_video(df1)
dfM2, ne2, nv2, vl2, na2 = process_video(dfAgree)
dfM3, ne3, nv3, vl3, na3 = process_video(df3)
dfM4, nv4, vl4, na4, al4 = process_action(df4)

dfInv = df4[df4.index.isin(df5["action_idx"]) == False]
naOoS = len(dfInv[dfInv["action"] == "Out of Sight"])
nvOoS = len(dfInv[dfInv["action"] == "Out of Sight"]["video_file"].unique())
naInv = len(dfInv[dfInv["action"] != "Out of Sight"])
nvInv = len(dfInv[dfInv["action"] != "Out of Sight"]["video_file"].unique())

dfM5, nv5, vl5, na5, al5 = process_action(df5)
dfM6, nv6, vl6, na6, al6 = process_action(df6)

s1 = f"""Data Cleaning

##### (0) Input Data #####
* Total: {vl0}
    - {ne0:,} entries
    - {nv0:,} videos
    - {na0:,} actions

##### (1) Video Filtering #####
* Valid video times: {vl1}
    - {ne1:,} entries
    - {nv1:,} videos
    - {na1:,} actions
* Invalid video times:
    - {(ne0 - ne1):,} entries

##### (2) Coding Filtering #####
* Coding agreement: {vl2}
    - {ne2:,} entries
    - {nv2:,} videos
    - {na2:,} actions
* Discarded: {vl1 - vl2}
    - Coding unknown: {(ne1 - len(dfV)):,} entries
    - Coding disagreement: {(len(dfV) - ne2):,} entries

##### (3) Observed Filtering #####
* FA seen: {vl3}
    - {ne3:,} entries
    - {nv3:,} videos
    - {na3:,} actions
* FA not seen: {vl2 - vl3}
    - {(nv2 - nv3):,} videos

##### (4) Behaviors #####
* Specified actions:
    - {nv4:,} videos ({vl4})
    - {na4:,} actions
* No actions: 
    - {(nv3 - nv4):,} videos ({vl3 - vl4})

##### (5) Action Filtering #####
* Valid actions:
    - {na5:,} actions ({al5})
    - {nv5:,} videos ({vl5})
* Discarded: {vl4 - vl5}
    - 'Out of Sight': {naOoS:,} actions, {nvOoS:,} videos
    - Invalid times: {naInv:,} actions, {nvInv:,} videos

##### (6) Interval Splitting #####
* Non-overlapping intervals:
    - {na6:,} actions ({al6})
    - {nv6:,} videos ({vl6})
"""

with open(f"{PROJECT_DIR}/analysis/supplement/figure_S1_data.txt", "w") as file:
    file.write(s1)

# ----- Table S4 ----- #

def get_grouped(df:pd.DataFrame, name:str) -> pd.DataFrame:
    if "date" not in df.columns:
        df["date"] = (df["year"].astype(str) + df["month"].astype(str).str.rjust(2, "0") +
                      df["day"].astype(str).str.rjust(2, "0")).apply(pd.to_datetime)

    grp = df.groupby(["date", "camera"]).size().reset_index()
    grp["day"] = grp["date"].dt.day
    grp = grp.set_index(["day", "camera"])[0]
    grp.name = name
    return grp

s4 = pd.concat([
    get_grouped(df0, "all_entries"),
    get_grouped(df1, "valid_entries"),
    get_grouped(dfAgree, "coding_agreement_entries"),
    get_grouped(df2, "coding_agreement_videos"),
    get_grouped(df3, "fa_seen_videos"),
    get_grouped(df4, "all_actions"),
    get_grouped(df5, "valid_actions"),
    get_grouped(df6, "non_overlapping_actions"),
], axis=1).fillna(0).astype(int).T

s4.columns.names = [None, None]
s4.to_csv(f"{PROJECT_DIR}/analysis/supplement/table_S4.tsv", sep="\t")
