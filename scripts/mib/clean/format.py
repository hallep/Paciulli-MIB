''' Helper functions for formatting human-entered data '''

from mib.external import pd, np, re
from mib.utils.constants import *

# file naming convention
def clean_filename(filename:str, year:int|str=None, month:int|str=None, day:int|str=None, camera:str=None) -> str:
    '''
    Fix the most common file name formatting issues:
        * remove trailing whitespace
        * replace dashes (-) with underscores (_) 
        * remove file extension
        * fix typos
        * set camera and date (if given)
    '''
    
    # erroneous characters
    file = str(filename).strip().strip("'").strip('"')
    file = file.removeprefix("Copy of ").replace("-", "_").replace(" ", "").lower()

    # remove extension
    file = re.sub(r'\.[asf]+', '', file)
    while file.endswith("asf") or file.endswith("."):
        file = file.removesuffix(".").removesuffix("asf")

    # typos
    file = re.sub(r'^m[a-zA-Z]*[0-9]+', 'M4208', file)
    file = re.sub(r'_[main]+([_]+)?', '_main_', file)

    if camera in CAMERA_CODES.keys():
        file = re.sub(r'_ch[0-9]+([_]+)?', f"_{CAMERA_CODES[camera]}_", file)

    if year and month and day:
        try:
            mm = str(month).rjust(2, "0")
            dd = str(int(day) + 1).rjust(2, "0")
            file = re.sub(r'_201706[0-9]{2}', f"_{year}{mm}{dd}", file)
        except:
            pass

    return file

def fmt_entry_filename(x:pd.Series, name_db:pd.DataFrame) -> str:
    '''
    Format video file name from Google Forms entry submission *x*

    Include database of all names (*name_db*)
    '''

    # camera
    c = CAMERA_CODES[x["camera"]]

    # date
    date = f"{x["year"]}{x["month"]:02d}{x["day"]+1:02d}"

    # time
    def fmt_time(t:str) -> str:
        if not pd.notna(t): return t

        try:
            t = int(t)
            if t == 240000:
                t = 235959
            t = str(t)
        except:
            t = str(t)
                
        fields = t.split(":")
        for i in range(len(fields)):
            fields[i] = "".join([d for d in fields[i] if d.isnumeric()]).rjust(2, "0")
        return "".join(fields).rjust(6, "0")

    st = fmt_time(x["Video Start Time"])
    s = f"{date}{st}"

    et = fmt_time(x["Video End Time"])
    e = f"{date}{et}"

    # valid from filename
    file = clean_filename(x["Video_File_Name"], year=x["year"], month=x["month"], day=x["day"], camera=x["camera"])
    if re.fullmatch(FILENAME_REGEX, file):
        fields = file.split("_")

        if not pd.notna(st):
            s = fields[-2]

        if not pd.notna(et):
            e = fields[-1]

        if int(fields[-2]) < int(fields[-1]):
            s = fields[-2]
            e = fields[-1]

    file = f"M4208_{c}_main_{s}_{e}"

    # valid
    if re.fullmatch(FILENAME_REGEX, file):
        return file

    # from database
    if s.endswith("nan") and re.fullmatch(DATETIME_RE, e):
        query = name_db[(name_db["camera"] == c) & (name_db["end"] == e)]
    elif e.endswith("nan") and re.fullmatch(DATETIME_RE, s):
        query = name_db[(name_db["camera"] == c) & (name_db["start"] == s)]
    elif int(s) >= int(e):
        query = name_db[(name_db["camera"] == c) & ((name_db["start"] == s) | (name_db["end"] == e))]

    if len(query) == 1:
        return query["video_index"].values[0]
    
    # invalid
    return np.nan

def fmt_action_time(x:pd.Series, col:str) -> pd.Timestamp:
    '''
    Convert entry *col* in Series *x* from string to Timestamp
    '''
    
    timecode = str(x[col])

    # mm:ss
    if timecode.count(":") == 1:
        mm, ss = timecode.split(":")
        return x["video_start_time"] + pd.Timedelta(minutes=float(mm), seconds=float(ss))

    # hh:mm:ss
    if timecode.count(":") == 2:
        hh, mm, ss = timecode.split(":")
        return pd.to_datetime(x["date"].strftime('%Y%m%d') + hh.rjust(2, "0") + mm.rjust(2, "0") + ss.rjust(2, "0"))

    # hhmmss
    return pd.to_datetime(x["date"].strftime('%Y%m%d') + timecode.rjust(6, "0"))

