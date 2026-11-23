''' Helper functions for constructing DataFrames '''

from mib.external import pd, np
from mib.utils.constants import *
from mib.clean.format import FILENAME_REGEX, clean_filename, fmt_entry_filename
from mib.clean.overlap import merge_overlapping

def compile_entries(xlsx_dict:dict[int, dict[str, pd.DataFrame]], code_df:pd.DataFrame) -> pd.DataFrame:
    ''' Compile data from all days and cameras '''

    df = pd.concat([
        pd.concat([xlsx_dict[d][s] for s in DATA_TABS[d]], 
                keys=list(CAMERA_CODES), names=["camera", "sheet_idx"], axis=0).copy().reset_index() for d in DAYS
    ], axis=0, keys=DAYS, names=["year", "month", "day", "day_idx"]).copy().reset_index().rename(columns={
        "Video File Name " : "Video_File_Name",
        "Focal Animal (FA)" : "FA"
    }).reset_index(names="entry_idx")

    df["date"] = (df["year"].astype(str) + df["month"].astype(str).str.rjust(2, "0") + 
                  df["day"].astype(str).str.rjust(2, "0")).apply(pd.to_datetime)

    # filename
    name_db = build_filename_db(code_df)
    df["video_file"] = df.apply(lambda x: fmt_entry_filename(x, name_db), axis=1)

    # get video start/end times
    nf = df["video_file"].str.split("_", expand=True)
    nf["start"] = (df["date"].dt.strftime('%Y%m%d') + nf[3].str[-6:])
    nf["end"] = (df["date"].dt.strftime('%Y%m%d') + nf[4].str[-6:])

    # convert to datetime
    nf["video_start_time"] = nf.apply(lambda x: pd.to_datetime(x["start"]) if pd.notna(x[3]) else pd.NaT, axis=1)
    nf["video_end_time"] = nf.apply(lambda x: pd.to_datetime(x["end"]) if pd.notna(x[4]) else pd.NaT, axis=1)

    df["video_start_time"] = nf[3].apply(lambda x: pd.to_datetime(x) if pd.notna(x) else pd.NaT)
    df["video_end_time"] = nf[4].apply(lambda x: pd.to_datetime(x) if pd.notna(x) else pd.NaT)

    return df

def compile_codes(xlsx_dict:dict[int, dict[str, pd.DataFrame]]) -> pd.DataFrame:
    ''' Compile coding agreement data '''

    code_df = pd.concat([
        pd.concat([xlsx_dict[d][s] for s in CODE_TABS[d]], 
                keys=list(CAMERA_CODES), names=["camera", "sheet_idx"], axis=0).copy().reset_index() for d in DAYS
    ], axis=0, keys=DAYS, names=["year", "month", "day", "day_idx"]).copy().reset_index()

    # format
    code_df.rename(columns={"Video File Name " : "Video_File_Name"}, inplace=True)
    code_df["video_index"] = code_df.apply(lambda x: clean_filename(
            x["Video_File_Name"], year=x["year"], month=x["month"], day=x["day"], camera=x["camera"]
    ), axis=1)
    
    return code_df[code_df["video_index"].str.lower() != "total"].dropna(subset=["Video_File_Name"])

def process_codes(code_df:pd.DataFrame) -> pd.DataFrame:
    ''' Get unique videos with specified codes '''

    # subset
    codes = code_df.dropna(subset=["Agree", "One Coder", "Disagree"], how="all")

    # remove duplicates
    uniq = codes.groupby(["year", "month", "day", "camera", "video_index"]).aggregate({
        "Agree" : "sum", 
        "One Coder" : "sum", 
        "Disagree" : "sum", 
        "Video_File_Name" : ",".join
    })

    uniq["code"] = uniq.apply(
        lambda x: 0 if (x["Disagree"] > 0) else 
            1 if (x["One Coder"] > 0) else 
            2 if (x["Agree"] > 0) else -1, axis=1
    )

    return uniq[["Video_File_Name", "code"]]

def build_filename_db(code_df:pd.DataFrame) -> pd.DataFrame:
    ''' Build a reference database of valid filenames '''

    name_db = code_df[code_df["video_index"].str.fullmatch(fr"{FILENAME_REGEX}(\.asf)?")][["video_index"]]
    name_db = name_db.drop_duplicates()

    fields = name_db["video_index"].str.split("_", expand=True)
    name_db["camera"] = fields[1]
    name_db["start"] = fields[3]
    name_db["end"] = fields[4]

    return name_db

def extract_actions(dfE:pd.DataFrame) -> pd.DataFrame:
    ''' Extract distinct actions from entries in *dfE* '''

    obsStart, = np.where(dfE.columns.str.startswith("Which action?"))

    entry = ["entry_idx", "video_file", "date", "camera", "video_start_time", "video_end_time", "FA"]
    column_names = entry + ["action", "sampling_time_mmss", "action_start_timecode", "action_end_timecode", "location"]

    # get observations
    dfs = [pd.DataFrame()] * len(obsStart)

    for i, s in enumerate(obsStart):
        cols = entry + list(dfE.columns[s:s+5])
        df = dfE[cols]
        df.columns = column_names
        dfs[i] = df

    # stack
    return pd.concat(dfs, axis=0).dropna(subset="action").drop_duplicates(
        subset=["video_file", "action", "action_start_timecode", "action_end_timecode"], 
        ignore_index=True
    )

def create_budget(dfA:pd.DataFrame, dfValid:pd.DataFrame, dfAgree:pd.DataFrame) -> pd.DataFrame:
    '''
    Create time budgets from actions (*dfA*), 
    valid entries (*dfValid*), and entries in agreement (*dfAgree*)
    '''

    def split_by_days(df:pd.DataFrame, colS:str, colE:str) -> dict[int, pd.Timestamp]:
        df = df.copy()
        if "date" not in df.columns:
            df["date"] = (df["year"].astype(str) + df["month"].astype(str).str.rjust(2, "0") +
                          df["day"].astype(str).str.rjust(2, "0")).apply(pd.to_datetime)
        
        df_dict = {}

        for d in DATE_STRINGS:
            dfDay = merge_overlapping(df[df["date"] == d], colS, colE)
            dfDay["length"] = dfDay[colE] - dfDay[colS] + pd.Timedelta(seconds=1)
            df_dict[d] = dfDay["length"].sum()
        
        return df_dict

    durations = {
        b : [dfA[(dfA["action"] == b) & (dfA["date"] == d)]["action_length"].sum() for d in DATE_STRINGS] 
        for b in BEHAVIORS.keys()
    }

    valid = split_by_days(dfValid, "video_start_time", "video_end_time")
    agree = split_by_days(dfAgree, "video_start_time", "video_end_time")
    actions = split_by_days(dfA, "action_start_time", "action_end_time")
    uncovered = {d : pd.Timedelta(days=1) - valid[d] for d in DATE_STRINGS}

    durations["Uncertain"] = [valid[d] - agree[d] for d in DATE_STRINGS]
    durations["Unknown"] = [uncovered[d] + agree[d] - actions[d] for d in DATE_STRINGS]

    return pd.DataFrame(durations, index=[f"{dt.strftime("%b")}{dt.day}" for dt in DATETIMES]).T
