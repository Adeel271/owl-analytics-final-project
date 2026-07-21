# Owl Analytics Final Project

**Student:** Sikander Cheema  
**Repository link:** https://github.com/Adeel271/owl-analytics-final-project.git

## Scenario
This project represents the details of the project Owl Analyitcs. Role of all 3 different teams is as follows; 

Team 1 collects cryptocurrency market data from Binance
Team 2 cleans a deliberately damaged copy with pandas
Team 3 analyses the complete cleaned dataset with PySpark and Spark SQL.

## Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
This is to create a separate / individual virtual enviroment to run the project in. 
## Run Team 1
Following Python command can be utilized to run the part aloccated by Team #1. 


python part1_build_dataset.py

Creates `data/clean/clean_market_data.csv`, `results/api_download.log`, and `results/runtime_comparison.csv`. Internet access is required. The script performs both serial and threaded downloads, so it makes 20 API requests in total while benchmarking.

## Create the messy dataset

Line of code below deliberately messes up the data to prove data cleaning ability of the software which is later implented. 

python scripts/mess_my_data.py --input data/clean/clean_market_data.csv --output data/messy/messy_market_data.csv


## Run Team 2
Following Python command can be utilized to run the part aloccated by Team #2. 

python part2_clean_with_pandas.py

Creates the cleaned full dataset, a quality report and a balanced pandas sample summary.

## Run Team 3
Following Python command can be utilized to run the part aloccated by Team #3. 

Open `part3_spark_analytics.ipynb` in Google Colab. Upload the repository files or mount Google Drive, update the input path if necessary, and run all cells. The notebook creates `results/spark_market_summary.csv`.

## Reports
- [Report to Stelios](reports/report_to_stelios.md)
- [Reflection](reports/reflection.md)

## Submitted files
- `part1_build_dataset.py` — threaded Binance downloader, rate limiting, logging and benchmark
- `part2_clean_with_pandas.py` — pandas cleaning and 50-row sample analysis
- `part3_spark_analytics.ipynb` — full PySpark and Spark SQL analytics
- `scripts/mess_my_data.py` — reproducible corruption script
- `reports/report_to_stelios.md`
- `reports/reflection.md`
- `requirements.txt`
- generated files under `data/` and `results/` after running the pipeline


