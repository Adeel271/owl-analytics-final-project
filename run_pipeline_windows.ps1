python part1_build_dataset.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts/mess_my_data.py --input data/clean/clean_market_data.csv --output data/messy/messy_market_data.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python part2_clean_with_pandas.py
