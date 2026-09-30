from ml.data.processing.cleaning import clean_dataset

clean_dataset(
    "ml/data/synthetic/master_synthetic.csv",
    "ml/data/processed/cleaned.csv"
)

print("Cleaned data:")
print("ml/data/processed/cleaned.csv")
