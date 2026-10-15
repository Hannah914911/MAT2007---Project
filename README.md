# MAT2007---Project
# Sex Differences in Smoking Prevalence Decline, 1980–2012

Python analysis of whether daily smoking prevalence declined faster among
females than males across 187 countries, done in Python in Visual Studio Code. Project for MAT2007 – Introduction
to Programming, Maastricht Science Programme.

## Research question
Has smoking prevalence declined faster among females than among males
between 1980 and 2012, in 187 countries?

## Dataset
"Global Smoking Prevalence and Cigarette Consumption 1980–2012" from the
Institute for Health Metrics and Evaluation (IHME), based on Ng et al. (2014).

- Source: https://ghdx.healthdata.org/download-access/login; you need to create an account or access the CSV file via this repository
- File name: `Smoking prevalence and cigarette consumption.csv`
- Columns used in this project: `Entity`, `Year`, `Daily smoking prevalence - male (IHME, GHDx (2012))`, `Daily smoking prevalence - female (IHME, GHDx (2012))`; renamed to: `country`, `year`, `male`, `female`

## Report
The full written report is available here: [MAT2007___Report___Hannah_Toetemeier.pdf](MAT2007___Report___Hannah_Toetemeier.pdf)

## Package Requirements
- pandas, numpy, matplotlib, scipy, seaborn
- install if not present already

## How to run
1. Save the CSV and Python files.
2. Set `file_path` at the top of `smoking_script.py` to the location of the CSV.
3. Run the code.

## What the script does
1. Loads and cleans the data (renames columns, removes the "World" row)
2. Computes yearly mean prevalence per sex with SD, SE, and 95% CI
3. Computes relative decline (% change from each sex's 1980 mean)
4. Fits a linear regression per country and sex (relative slope)
5. Runs two one-sample t-tests (slope vs. 0) and a paired t-test (female vs. male slopes)
6. Saves three figures

## Output
Figures are saved to the `smoking_output` folder:
- `prevalence_over_time.png`
- `relative_decline.png`
- `slope_distribution_by_sex.png`

Other test results and key information are printed to the terminal.

## Key results
Prevalence declined significantly for both sexes (p < 0.001), but the paired
t-test showed no significant difference between female and male decline rates
(t(186) = -0.31, p = 0.76).

## Author
Hannah T. – Maastricht Science Programme
