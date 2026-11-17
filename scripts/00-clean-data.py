''' Code used in data cleaning/filtering '''

from mib.external import os, pd
from mib.utils.constants import *
from mib.clean.format import *
from mib.clean.build import *
from mib.clean.overlap import *

os.makedirs(f"{PROJECT_DIR}/data/cleaned", exist_ok=True)
os.makedirs(f"{PROJECT_DIR}/data/budgets", exist_ok=True)

# ===== Load Data ===== #

xlsx_dict = {k : pd.read_excel(v, sheet_name=None) for k,v in XLSX_FILES.items()}

# ----- Video Coding ----- #

code_df = compile_codes(xlsx_dict)
uniq = process_codes(code_df)
uniq[["Video_File_Name", "code"]].to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_video_coding.tsv", sep="\t")

# valid filenames
name_db = build_filename_db(code_df)

# ===== Observations ===== #

df0 = compile_entries(xlsx_dict, name_db)
df0.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v0_raw.tsv", sep="\t", index=False)

# ----- Filter Entries ----- #

# specified start/end time AND valid time range
df1 = df0[df0["video_start_time"].notna() & df0["video_end_time"].notna() & (df0["video_start_time"] < df0["video_end_time"])]
df1["code_idx"] = df1.apply(lambda x: clean_filename(x["Video_File_Name"], x["year"], x["month"], x["day"], x["camera"]), axis=1)
df1.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v1_valid_entries.tsv", sep="\t", index=False)

# ----- Filter Videos ----- #

dfV = df1[df1["code_idx"].isin(uniq.index.values)]
dfV.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v2a_coding_known.tsv", sep="\t", index=False)

# 1 coder OR coding agreement
dfAgree = dfV[dfV["code_idx"].isin(uniq[uniq["code"] > 0].index.values)]
dfAgree.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v2b_coding_agreement_entries.tsv", sep="\t", index=False)

df2 = dfAgree.sort_values("Is the Focal Animal seen?", ascending=False).drop_duplicates(subset="code_idx")
df2.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v2_coding_agreement_videos.tsv", sep="\t", index=False)

# seen
df3 = df2[df2["Is the Focal Animal seen?"].str.startswith("Yes")]
df3.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v3_fa_seen_videos.tsv", sep="\t", index=False)

# ===== Actions ===== #

df4 = extract_actions(df3)
df4.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v4_all_actions.tsv", sep="\t", index=False)

# ----- Filter Actions ----- #

df5 = df4[(df4["action"] != "Out of Sight") & 
          df4["action_start_timecode"].notna() & df4["action_end_timecode"].notna() &
          df4["action_start_timecode"].apply(lambda x: not any(c.isalpha() for c in str(x))) &
          df4["action_end_timecode"].apply(lambda x: not any(c.isalpha() for c in str(x)))]

df5["action_start_time"] = df5.apply(lambda x: fmt_action_time(x, "action_start_timecode"), axis=1)
df5["action_end_time"] = df5.apply(lambda x: fmt_action_time(x, "action_end_timecode"), axis=1)
df5 = df5[(df5["action_start_time"] <= df5["action_end_time"]) &
          (df5["video_start_time"] <= df5["action_start_time"]) &
          (df5["video_end_time"] >= df5["action_end_time"])].drop(
    columns=["action_start_timecode", "action_end_timecode"]
).reset_index(names="action_idx")

df5.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v5_valid_actions.tsv", sep="\t", index=False)

# ----- Split Overlaps ----- #

df6 = split_overlapping(df5, "action_start_time", "action_end_time")
df6["action_length"] = df6["action_end_time"] - df6["action_start_time"] + pd.Timedelta(seconds=1)
df6.to_csv(f"{PROJECT_DIR}/data/cleaned/MIB_Agatha_observations_v6_non_overlapping_actions.tsv", sep="\t", index=False)

# ----- Time Budgets ----- #

# Budget in Timedelta
budget_td = create_budget(df6, df0, dfAgree)
budget_td.index.name = "behavior"
budget_td["agg"] = budget_td.sum(axis=1)
budget_td.to_csv(f"{PROJECT_DIR}/data/budgets/MIB_Agatha_budgets_timedeltas.tsv", sep="\t")

# Budget in seconds
budget_sec = pd.concat([budget_td[c].dt.total_seconds() for c in budget_td.columns], axis=1).astype(int)
budget_sec.to_csv(f"{PROJECT_DIR}/data/budgets/MIB_Agatha_budgets_seconds.tsv", sep="\t")

# Budget as proportions
budget_prop = budget_sec.divide(budget_sec.sum())
budget_prop.to_csv(f"{PROJECT_DIR}/data/budgets/MIB_Agatha_budgets_proportions.tsv", sep="\t")
