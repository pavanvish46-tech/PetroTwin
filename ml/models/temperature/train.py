from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from ml.data.processing.feature_engineering import build_features,predictor_columns
from ml.data.processing.split import temporal_split

TARGET="temperature_24h_target_c"
EXCLUDE={"reservoir_temperature_c","oil_production_bopd","water_production_bwpd","energy_consumption_kwh","steam_oil_ratio"}

def train(input_csv="ml/data/processed/cleaned.csv",artifact="ml/artifacts/temperature_model.joblib"):
    df=build_features(pd.read_csv(input_csv)); train_df,val_df,test_df,val_start,test_start=temporal_split(df)
    cols=[c for c in predictor_columns(df) if c not in EXCLUDE]
    candidates={
        "ExtraTreesRegressor":ExtraTreesRegressor(n_estimators=300,min_samples_leaf=3,max_features=.85,random_state=26121,n_jobs=-1),
        "RandomForestRegressor":RandomForestRegressor(n_estimators=280,min_samples_leaf=3,max_features=.80,random_state=26121,n_jobs=-1),
        "HistGradientBoostingRegressor":HistGradientBoostingRegressor(max_iter=350,learning_rate=.045,max_leaf_nodes=31,l2_regularization=.5,random_state=26121)
    }
    val_scores={}; test_scores={}; models={}
    for name,model in candidates.items():
        pipe=Pipeline([("imputer",SimpleImputer(strategy="median")),("model",model)])
        pipe.fit(train_df[cols],train_df[TARGET])
        vp=pipe.predict(val_df[cols]); tp=pipe.predict(test_df[cols])
        val_scores[name]={"MAE":float(mean_absolute_error(val_df[TARGET],vp)),"RMSE":float(np.sqrt(mean_squared_error(val_df[TARGET],vp))),"R2":float(r2_score(val_df[TARGET],vp))}
        test_scores[name]={"MAE":float(mean_absolute_error(test_df[TARGET],tp)),"RMSE":float(np.sqrt(mean_squared_error(test_df[TARGET],tp))),"R2":float(r2_score(test_df[TARGET],tp))}
        models[name]=pipe
    best=min(val_scores,key=lambda x:val_scores[x]["RMSE"])
    Path(artifact).parent.mkdir(parents=True,exist_ok=True); joblib.dump(models[best],artifact)
    Path(artifact).with_suffix(".json").write_text(json.dumps({"target":TARGET,"selected_model":best,"features":cols,"validation_scores":val_scores,"test_scores":test_scores,"validation_start":str(val_start.date()),"test_start":str(test_start.date()),"selection_rule":"lowest validation RMSE"},indent=2))
    print("Selected:",best); print("Validation:",val_scores[best]); print("Test:",test_scores[best])
    return test_scores

if __name__=="__main__": train()
