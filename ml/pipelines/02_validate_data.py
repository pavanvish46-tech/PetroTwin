import json
from pathlib import Path
import pandas as pd

from ml.data.validation.quality import (
    validate_schema,
    quality_report
)

input_file="ml/data/synthetic/master_synthetic.csv"

df=pd.read_csv(input_file)

validate_schema(df)

report=quality_report(df)

output=Path("ml/data/validation")
output.mkdir(parents=True,exist_ok=True)

(output/"quality_report.json").write_text(
    json.dumps(report,indent=2)
)

print(json.dumps(report,indent=2))
