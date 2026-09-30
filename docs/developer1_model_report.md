# Developer 1 — ML + Digital Twin Model Report

## Dataset status
- 5,400 synthetic time-series records
- 30 synthetic wells
- 180 CSS cycles
- Date range: 2025-01-01 to 2025-06-29
- Failure target rate: ~12.8%
- All records are explicitly marked synthetic.

Recommended SIH wording:
> Physics-informed synthetic prototype dataset calibrated using publicly available field and SRP information.

Do not present these records as actual Baghewala measurements.

## Validation design
The model pipeline uses chronological train/validation/test partitions. Candidate models are selected using validation performance; the final test set is used only for reporting.

Temporal features are leakage-safe: lags and rolling statistics are calculated from observations strictly before the prediction row.

## Final test metrics
### Production — next 24h
Selected model: HistGradientBoostingRegressor
- MAE: 0.817 BOPD
- RMSE: 1.024 BOPD
- R²: 0.686

### Reservoir temperature — next 24h
Selected model: ExtraTreesRegressor
- MAE: 0.339 °C
- RMSE: 0.430 °C
- R²: 0.877

### Failure — next 7d
Selected model: LogisticRegression
- Threshold: 0.61
- Precision: 0.262
- Recall: 0.746
- F1: 0.388
- ROC-AUC: 0.709
- PR-AUC: 0.316

The failure model is configured for a recall-oriented decision threshold because missed failure precursors are operationally important in the prototype. The probability is decision support, not a guaranteed failure prediction.

## Feature engineering
The pipeline now includes:
- 1/3/7-day lag features
- 3/7-day leakage-safe rolling means
- 7-day production rolling standard deviation
- production decline rate
- 24h temperature change
- rod-load change
- steam heat index
- pump displacement index
- mechanical stress index
- mechanical stress persistence
- physics-informed failure-risk prior

Feature audit result:
- Leakage detected: false
- Predictor count: 80
- Lag features: 28
- Rolling features: 7

## Digital Twin
The prototype couples:
1. CSS thermal response
2. Temperature → viscosity → mobility
3. Reservoir inflow
4. SRP pump fillage
5. Rod load and pump efficiency
6. Production
7. SOR, energy and failure-risk response

## Optimization
The optimizer performs a constrained scenario sweep over coupled CSS + SRP controls. It returns three decision-support strategies:
- Maximum Production
- Balanced
- Maximum Efficiency

The strategies are deliberately trade-off based rather than claiming one universal optimum.

The optimizer also couples SPM changes to VFD frequency so energy changes with SRP speed.

## Safety / operational boundary
This is a prototype decision-support system. It does not directly control field equipment. Recommendations require human/engineer approval.
