'''
Various Constants
* Dates
* Spreadsheets
* Actions
* Comparisons
'''

from mib.external import Path, calendar, combinations, datetime

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
''' Repository directory path '''

# Data sources
XLSX_FILES = {
    (2017, 6, 6) : f"{PROJECT_DIR}/data/raw/AR_Mother_June_6.xlsx",
    (2017, 6, 7) : f"{PROJECT_DIR}/data/raw/AR_Mother_June_7.xlsx",
    (2017, 6, 8) : f"{PROJECT_DIR}/data/raw/AR_Mother_June_8.xlsx",
}
'''
Paths to XLSX files 

Keys: (year, month, day)
'''

DATA_TABS = {
    (2017, 6, 6) : ["Center", "Nest Box X", "Nest Box Z"],
    (2017, 6, 7) : ["Center", "Nest Box X", "Nest Box Z"],
    (2017, 6, 8) : ["Center", "Nest Box X", "Nest Box Z"],
}
''' 
Worksheet names corresponding to observations from
Center, Nest Box X, and Nest Box Z cameras

Keys: (year, month, day)
'''

CODE_TABS = {
    (2017, 6, 6) : ["Sheet5", "Sheet6", "Sheet7"],
    (2017, 6, 7) : ["C Coder %", "X Coder %", "Z Coder %"],
    (2017, 6, 8) : ["C Coder %", "X Coder %", "Z Coder %"]
}
''' 
Worksheet names corresponding to coding for
Center, Nest Box X, and Nest Box Z videos

Keys: (year, month, day)
'''

# Of interest
DAYS = [(2017, 6, 6), (2017, 6, 7), (2017, 6, 8)]
''' Days of interest, formatted as (year, month, day) tuples '''

DATETIMES = [datetime(year=y, month=m, day=d) for y, m, d in DAYS]
''' Days of interest, as datetime objects '''

DATE_STRINGS = [dt.strftime("%Y%m%d") for dt in DATETIMES]
''' Days of interest, formatted as 'YYYYMMDD' strings '''

# Days
DAY_SETS = [f"{calendar.month_abbr[m]}{d}" for _, m, d in DAYS]
''' Days of interest, formatted as {month abbreviation}{day} '''

DAY_PALETTE = {
    "Jun6" : ("#0099CC", "June 6"),
    "Jun7" : ("#FF6600", "June 7"),
    "Jun8" : ("#00CC00", "June 8"),
    "agg" : ("#545454", "Aggregate")
}
''' Colors and labels for each day in DAY_SETS, as well as 'agg' '''

# Comparisons
PAIR_SETS = [f"{d1}.v.{d2}" for d1, d2 in combinations(DAY_SETS, 2)]
''' Comparisons of interest, formatted as {day1}.v.{day2} '''

PAIR_PALETTE = {
    "Jun6.v.Jun7" : ("#990099", "June 6 v. June 7"),
    "Jun7.v.Jun8" : ("#E6B500", "June 7 v. June 8"),
    "Jun6.v.Jun8" : ("#00CC99", "June 6 v. June 8")
}
''' Colors and labels for each comparison in 'PAIR_SETS' '''

# Actions
BEHAVIORS = {
    "Carrying (mother)" : "Carrying",
    "Constructing Nest" : "Constructing\nNest",
    "Drinking" : "Drinking",
    "Feeding (mother)" : "Feeding",
    "Foot allo-grooming" : "Foot allo-\ngrooming",
    "Foot auto-grooming" : "Foot auto-\ngrooming",
    "Foraging (mother)" : "Foraging",
    "Hand allo-grooming" : "Hand allo-\ngrooming",
    "Mouth allo-grooming" : "Mouth allo-\ngrooming",
    "Hand auto-grooming" : "Hand auto-\ngrooming",
    "Mouth auto-grooming" : "Mouth auto-\ngrooming",
    "Moving (inside nest box)" : "Moving",
    "Nursing (infant)" : "Nursing",
    "Observing" : "Observing",
    "Playing" : "Playing",
    "Resting" : "Resting",
    "Sleeping" : "Sleeping",
    "Travelling (moving outside nest box)" : "Traveling"
}
''' Biological behavioral categories of interest 

Keys: action from Google Form

Values: Formatted action labels
'''

# File naming
CAMERA_CODES = {
    "Center" : "ch1",
    "Nest Box X" : "ch2",
    "Nest Box Z" : "ch3"
}
''' Filename codes for cameras '''

CAMERA_RE = r'ch[1-3]'

YEAR_RE = r'20[0-2][0-9]'
MONTH_RE = r'0[1-9]|1[0-2]'
DAY_RE = r'0[1-9]|[1-2][0-9]|3[0-1]'
DATE_RE = fr'({YEAR_RE})({MONTH_RE})({DAY_RE})'

TIME_RE = r'([0-1][0-9]|2[0-3])[0-5][0-9][0-5][0-9]'
DATETIME_RE = rf'({DATE_RE})({TIME_RE})'

FILENAME_REGEX = rf'M4208_{CAMERA_RE}_main_{DATETIME_RE}_{DATETIME_RE}'
