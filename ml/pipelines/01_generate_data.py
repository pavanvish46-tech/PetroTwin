from ml.data.generator.dataset_generator import generate_dataset
from pathlib import Path

df=generate_dataset()

output=Path("ml/data/synthetic")
output.mkdir(parents=True,exist_ok=True)

df.to_csv(
    output/"master_synthetic.csv",
    index=False
)

print(f"Generated {len(df):,} records")
print(f"Wells: {df.well_id.nunique()}")
print(f"Cycles: {df.cycle_id.nunique()}")
