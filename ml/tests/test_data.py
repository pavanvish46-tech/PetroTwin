import pandas as pd
from ml.data.validation.quality import validate_schema

def test_dataset_schema():
    df=pd.read_csv("ml/data/synthetic/master_synthetic.csv")
    assert validate_schema(df)
    assert len(df)>0
