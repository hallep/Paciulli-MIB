# Mother-Infant Behavior (MIB) Study
Statistical analyses done for the Paciulli Lab's MIB study at North Carolina State University

This work was completed by Halle Pearce, acting in the role of statistical consultant as part of ST 542 Statistical Practice


## Description
The goal of the Mother-Infant Behavior (MIB) project is to describe the perinatal (‘around time of birth’) behavior of a captive mother-infant aye-aye pair at the Duke Lemur Center (DLC) in Durham, North Carolina

This sub-project specifically focuses on describing the behavior of mother aye-aye, Medusa, the day before (June 6), the day of (June 7), and the day after (June 8) giving birth to her daughter, Agatha, in 2017

This is approached through two main aims:
1. To identify enriched maternal behaviors for each day
2. To identify differences in behavior across the three days

All raw data, intermediate files, final outputs, and scripts are included in this repository:
* Raw data (de-identified) is located in `data/raw`
* Cleaned and processed data are in `data/cleaned` and `data/budgets`, respectively
* Results from statistical tests are in `analysis/aim1` and `analysis/aim2`
* Main figures are in `analysis/figures`
* Supplementary information are in `analysis/supplement`
* Tables S4-S9 are in `analysis/tables_S4_S9.xlsx`
* Code used to generate outputs are in `scripts` 

## Usage
To re-run analyses:

```
git clone https://github.com/hallep/Paciulli-MIB.git
cd Paciulli-MIB
conda create -f mib.yaml
./run-analyses.sh
```

### Dependencies
This project uses Python (v3.14.7) and R (v4.5.3).

Python packages:
* pandas (v3.1.1)
* NumPy (v2.5.4)
* Matplotlib (v3.11.2)
* scikit-posthocs (v0.17.1)

R packages:
* this.path (v2.8.0)

All dependencies can be installed through Conda:
```
conda create -f mib.yaml
```

Other software and package versions may work but are untested

### Analyses
All analyses can be run using `run.sh`

Individual steps can be run using the files in `scripts`:

* Data cleaning
```
python scripts/00-clean-data.py
```

* Statistical analyses
```
Rscript scripts/01-aim1.R
Rscript scripts/02-aim2.R
```

* Figures
```
python scripts/03-figure1.py
python scripts/04-figure23.py
python scripts/05-figure4.py
python scripts/06-supplementary.py
```

### Updating Inputs
To apply analyses to new data, update values:
* `scripts/mib/utils/constants.py`
    * Data sources: `XLSX_FILES`, `DATA_TABS`, `CODE_TABS`, `DAYS`
    * Formatting (for figures): `BEHAVIORS`, `DAY_PALETTE`, `PAIR_PALETTE`
* `scripts/01-aim1.R`: `DATES`
* `scripts/02-aim2.R`: `DATES`
