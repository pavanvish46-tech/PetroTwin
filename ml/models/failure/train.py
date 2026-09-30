from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support,roc_auc_score,average_precision_score
from ml.data.processing.feature_engineering import build_features,predictor_columns
from ml.data.processing.split import temporal_split

TARGET="failure_next_7d"

def train(input_csv="ml/data/processed/cleaned.csv",artifact="ml/artifacts/failure_model.joblib"):
    df=build_features(pd.read_csv(input_csv)); train_df,val_df,test_df,val_start,test_start=temporal_split(df)
    cols=[c for c in predictor_columns(df) if c!=TARGET]
    candidates={
        "LogisticRegression":LogisticRegression(max_iter=1000,class_weight="balanced",C=.5,random_state=26122),
        "RandomForestClassifier":RandomForestClassifier(n_estimators=300,min_samples_leaf=4,class_weight="balanced_subsample",random_state=26122,n_jobs=-1,max_features=.75),
        "ExtraTreesClassifier":ExtraTreesClassifier(n_estimators=300,min_samples_leaf=4,class_weight="balanced",random_state=26122,n_jobs=-1,max_features=.80),
        "HistGradientBoostingClassifier":HistGradientBoostingClassifier(max_iter=300,learning_rate=.045,max_leaf_nodes=25,l2_regularization=.7,random_state=26122)
    }
    val_scores={}; test_scores={}; models={}; thresholds={}
    for name,model in candidates.items():
        steps=[("imputer",SimpleImputer(strategy="median"))]
        if name=="LogisticRegression": steps.append(("scaler",StandardScaler()))
        steps.append(("model",model))
        pipe=Pipeline(steps)
        pipe.fit(train_df[cols],train_df[TARGET])
        vp=pipe.predict_proba(val_df[cols])[:,1]
        # Choose threshold on validation only; maximize F1 while requiring >= 0.45 recall.
        best_t=.50; best_f1=-1
        for t in np.arange(.15,.71,.01):
            pred=(vp>=t).astype(int)
            p,r,f,_=precision_recall_fscore_support(val_df[TARGET],pred,average="binary",zero_division=0)
            if r>=.45 and f>best_f1: best_t=float(t); best_f1=float(f)
        tp=pipe.predict_proba(test_df[cols])[:,1]
        pred=(tp>=best_t).astype(int)
        p,r,f,_=precision_recall_fscore_support(test_df[TARGET],pred,average="binary",zero_division=0)
        val_pred=(vp>=best_t).astype(int); vp_,vr_,vf_,_=precision_recall_fscore_support(val_df[TARGET],val_pred,average="binary",zero_division=0)
        val_scores[name]={"precision":float(vp_),"recall":float(vr_),"f1":float(vf_),"roc_auc":float(roc_auc_score(val_df[TARGET],vp)),"pr_auc":float(average_precision_score(val_df[TARGET],vp))}
        test_scores[name]={"precision":float(p),"recall":float(r),"f1":float(f),"roc_auc":float(roc_auc_score(test_df[TARGET],tp)),"pr_auc":float(average_precision_score(test_df[TARGET],tp))}
        models[name]=pipe; thresholds[name]=best_t
    best=max(val_scores,key=lambda x:val_scores[x]["pr_auc"])
    Path(artifact).parent.mkdir(parents=True,exist_ok=True); joblib.dump(models[best],artifact)
    Path(artifact).with_suffix(".json").write_text(json.dumps({"target":TARGET,"selected_model":best,"features":cols,"threshold":thresholds[best],"validation_scores":val_scores,"test_scores":test_scores,"validation_start":str(val_start.date()),"test_start":str(test_start.date()),"selection_rule":"highest validation PR-AUC"},indent=2))
    print("Selected:",best); print("Threshold:",thresholds[best]); print("Validation:",val_scores[best]); print("Test:",test_scores[best])
    return test_scores

if __name__=="__main__": train()
