# Owl Analytics Final Project

**Student:** Sikander Cheema  
**Repository link:** Replace this line with the URL of your private GitHub repository.

## Scenario
This project represents a first week at Owl Analytics. Team 1 collects cryptocurrency market data from Binance, Team 2 cleans a deliberately damaged copy with pandas, and Team 3 analyses the complete cleaned dataset with PySpark and Spark SQL.

## Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run Team 1
```powershell
python part1_build_dataset.py
```
Creates `data/clean/clean_market_data.csv`, `results/api_download.log`, and `results/runtime_comparison.csv`. Internet access is required. The script performs both serial and threaded downloads, so it makes 20 API requests in total while benchmarking.

## Create the messy dataset
```powershell
python scripts/mess_my_data.py --input data/clean/clean_market_data.csv --output data/messy/messy_market_data.csv
```

## Run Team 2
```powershell
python part2_clean_with_pandas.py
```
Creates the cleaned full dataset, a quality report and a balanced pandas sample summary.

## Run Team 3
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

## Important submission step
Create a private GitHub repository from the instructor template, copy these completed files into it, replace the repository link above, run the pipeline to generate your own current outputs, commit the files, and share the private repository with the instructor address stated in the assignment brief. Review and personalise the report and reflection so they truthfully describe your own work and results.
