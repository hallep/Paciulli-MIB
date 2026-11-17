#!/bin/bash

shopt -s expand_aliases
alias timestamp="date '+%Y-%m-%d %H:%M:%S'"

PROJECT_DIR="$(dirname "$(realpath ${BASH_SOURCE[0]})")"

echo "[$(timestamp)] Running MIB analyses"

echo -e "\n[$(timestamp)] Processing raw data"
echo "    CMD: python scripts/00-clean-data.py"
python "${PROJECT_DIR}/scripts/00-clean-data.py"

echo -e "\n[$(timestamp)] Running statistical tests for aim 1"
echo "    CMD: Rscript scripts/01-aim1.R"
Rscript "${PROJECT_DIR}/scripts/01-aim1.R"

echo -e "\n[$(timestamp)] Running statistical tests for aim 2"
echo "    CMD: Rscript scripts/02-aim2.R"
Rscript "${PROJECT_DIR}/scripts/02-aim2.R"

echo -e "\n[$(timestamp)] Generating time budget heatmap (Figure 1)"
echo "    CMD: python scripts/03-figure1.py"
python "${PROJECT_DIR}/scripts/03-figure1.py"

echo -e "\n[$(timestamp)] Generating volcano plots (Figures 2 and 3)"
echo "    CMD: python scripts/04-figure23.py"
python "${PROJECT_DIR}/scripts/04-figure23.py"

echo -e "\n[$(timestamp)] Generating time budget heatmap (Figure 4)"
echo "    CMD: python scripts/05-figure4.py"
python "${PROJECT_DIR}/scripts/05-figure4.py"

echo -e "\n[$(timestamp)] Extracting supplementary information"
echo "    CMD: python scripts/06-supplementary.py"
python "${PROJECT_DIR}/scripts/06-supplementary.py"

echo -e "\n[$(timestamp)] Done"
