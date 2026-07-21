"""Team 2: clean the deliberately messy market dataset with pandas.
Run: python part2_clean_with_pandas.py
"""
from pathlib import Path
import pandas as pd

# Loads the aquireud data sets with possible missing values, duplicates, and invalid data types. Cleans the data and saves a cleaned version to a new CSV file. Also generates a data quality report and a balanced sample of the cleaned data.

INPUT=Path('data/messy/messy_market_data.csv'); OUTPUT=Path('data/clean/cleaned_market_data.csv'); 

# Generate a data quality report and a balanced sample of the cleaned data.

QUALITY=Path('results/data_quality_report.txt'); SAMPLE=Path('results/pandas_sample_results.csv')

# Define the expected numeric columns and the expected symbols for validation.

NUMERIC=['open','high','low','close','volume','quote_volume','trade_count','taker_buy_base_volume','taker_buy_quote_volume']

# Define the expected symbols for validation.

EXPECTED={'BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','AVAXUSDT','LINKUSDT','DOTUSDT'}

# Define the main function to load, clean, and save the data, as well as generate the data quality report and balanced sample.

def main():
    df=pd.read_csv(INPUT); before_rows=len(df); before_missing=df.isna().sum(); before_dupes=int(df.duplicated().sum())
    print(f'Loaded {INPUT}\nRows: {df.shape[0]}\nColumns: {df.shape[1]}'); print(df.head(10)); print(df.dtypes)

# Print the number of missing values per column before cleaning, and identify the most affected column.

    print('\nMissing values:\n',before_missing.sort_values(ascending=False)); 
    print('Most affected column:',before_missing.idxmax())

# Convert the expected numeric columns to numeric data types, coercing errors to NaN.

    for c in NUMERIC: df[c]=pd.to_numeric(df[c],errors='coerce')

    # Convert the 'open_time' and 'close_time' columns to datetime, coercing errors to NaT, and standardize the 'symbol' column by converting to uppercase, stripping whitespace, and removing special characters.

    df['open_time']=pd.to_datetime(df['open_time'],errors='coerce',utc=True); 
    df['close_time']=pd.to_datetime(df['close_time'],errors='coerce',utc=True)
    df['symbol']=df['symbol'].astype('string').str.upper().str.strip().str.replace('/','',regex=False).str.replace('-','',regex=False)

    invalid_symbols=~df['symbol'].isin(EXPECTED); df.loc[invalid_symbols,'symbol']=pd.NA
    invalid_numeric=int(df[NUMERIC].isna().any(axis=1).sum()); invalid_dates=int(df[['open_time','close_time']].isna().any(axis=1).sum()); 
    negative_volume=int((df['volume']<0).fillna(False).sum())
    df.loc[df['volume']<0,'volume']=pd.NA

    df=df.drop_duplicates().dropna(subset=['symbol','interval','open_time','close_time']+NUMERIC)
    df=df[(df[['open','high','low','close','volume','quote_volume']]>=0).all(axis=1) & (df['high']>=df['low']) & (df['trade_count']>=0)]
    df['trade_count']=df['trade_count'].round().astype('int64')

    df['price_range']=df['high']-df['low']; df['price_change']=df['close']-df['open']; df['percent_change']=(df['price_change']/df['open'])*100
    df['candle_direction']=df['price_change'].map(lambda x:'up' if x>0 else ('down' if x<0 else 'flat'))

    df=df.sort_values(['symbol','open_time']).reset_index(drop=True); OUTPUT.parent.mkdir(parents=True,exist_ok=True); df.to_csv(OUTPUT,index=False)
    balanced=(df.groupby('symbol',group_keys=False).apply(lambda g:g.sample(min(5,len(g)),random_state=42),include_groups=True).reset_index(drop=True))


    summary=balanced.groupby('symbol').agg(records=('symbol','size'),average_close=('close','mean'),average_volume=('volume','mean'),average_percent_change=('percent_change','mean')).reset_index(); summary.to_csv(SAMPLE,index=False)
    report=f"""DATA QUALITY REPORT\nInput rows: {before_rows}\nInput columns: {len(pd.read_csv(INPUT,nrows=1).columns)}\nDuplicate rows detected: {before_dupes}\nRows with invalid numeric values: {invalid_numeric}\nRows with invalid timestamps: {invalid_dates}\nNegative volume values detected: {negative_volume}\nMissing values before cleaning:\n{before_missing.to_string()}\n\nOutput rows: {len(df)}\nRows removed: {before_rows-len(df)}\nRemaining duplicate rows: {df.duplicated().sum()}\nRemaining missing values: {int(df.isna().sum().sum())}\nUnique cleaned symbols: {df.symbol.nunique()}\nOutput file: {OUTPUT}\nBalanced pandas sample rows: {len(balanced)}\nSample result file: {SAMPLE}\n"""
    QUALITY.write_text(report,encoding='utf-8'); print(report); print('Cleaning completed successfully')
if __name__=='__main__': main()
