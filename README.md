# CSV Data Analyzer

A simple command-line tool written in Python for analyzing CSV datasets.

## Features

- Dataset overview (shape, column types, missing values)
- Preview of first N rows
- Basic statistics (mean, min, max, std, quartiles)
- Optional single-column analysis
- Optional export of statistics to CSV

---

## Tech Stack

- Python 3.9+
- pandas
- argparse

---

## Installation

Install dependencies:

python3 -m pip install -r requirements.txt

---

## Usage

Run:

python analyzer.py data.csv

Only statistics:

python analyzer.py data.csv --stats-only

Analyze specific column:

python analyzer.py data.csv --column score

Export statistics:

python analyzer.py data.csv --stats-only --export stats.csv

---

## Project Structure

csv-data-analyzer/
│
├── analyzer.py
├── data.csv
├── requirements.txt
└── README.md
## Example

python analyzer.py data.csv --stats-only

Output:
- Overview of dataset
- Descriptive statistics table for numeric columns
