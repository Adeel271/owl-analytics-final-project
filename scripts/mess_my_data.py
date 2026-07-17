"""Create a reproducibly corrupted copy of the Team 1 dataset."""
import argparse, random
from pathlib import Path
import pandas as pd
p=argparse.ArgumentParser(); p.add_argument('--input',default='data/clean/clean_market_data.csv'); p.add_argument('--output',default='data/messy/messy_market_data.csv'); a=p.parse_args()
rng=random.Random(42); df=pd.read_csv(a.input)
# remove 20 records and duplicate 10
remove=rng.sample(list(df.index),20); df=df.drop(remove).reset_index(drop=True); df=pd.concat([df,df.sample(10,random_state=42)],ignore_index=True)
for col in ['open','high','low','close','volume','quote_volume','trade_count','open_time','close_time']:
    for i in rng.sample(range(len(df)),35): df.loc[i,col]=None
for col in ['open','high','low','close','volume','quote_volume','trade_count']:
    for i in rng.sample(range(len(df)),20): df.loc[i,col]=rng.choice(['unknown','error',''])
for col in ['open_time','close_time']:
    for i in rng.sample(range(len(df)),20): df.loc[i,col]='not_a_date'
for i in rng.sample(range(len(df)),80):
    s=str(df.loc[i,'symbol']); df.loc[i,'symbol']=rng.choice([s.lower(),f' {s} ',s.replace('USDT','/USDT')])
for i in rng.sample(range(len(df)),30): df.loc[i,'volume']=-abs(float(df.loc[i,'volume'])) if str(df.loc[i,'volume']).replace('.','',1).isdigit() else -1
Path(a.output).parent.mkdir(parents=True,exist_ok=True); df.to_csv(a.output,index=False); print(f'Saved {a.output}: {len(df)} rows')
