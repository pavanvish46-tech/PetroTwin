import pandas as pd

def temporal_split(df,test_fraction=.20,val_fraction=.20):
    x=df.copy()
    x["date"]=pd.to_datetime(x["date"])
    dates=sorted(x["date"].dropna().unique())
    if len(dates) < 10:
        raise ValueError("Not enough dates for temporal split")
    test_start=dates[max(1,int(len(dates)*(1-test_fraction)))] if int(len(dates)*(1-test_fraction)) < len(dates) else dates[-1]
    val_start=dates[max(1,int(len(dates)*(1-test_fraction-val_fraction)))]
    train=x[x["date"] < val_start].copy()
    val=x[(x["date"] >= val_start) & (x["date"] < test_start)].copy()
    test=x[x["date"] >= test_start].copy()
    return train,val,test,val_start,test_start
