import numpy as np

def residual_sigma(y_true,y_pred):
    residuals=np.asarray(y_true)-np.asarray(y_pred)
    return float(np.std(residuals,ddof=1))

def prediction_interval(prediction,sigma,z=1.96):
    return {
        "prediction":float(prediction),
        "lower_bound":float(prediction-z*sigma),
        "upper_bound":float(prediction+z*sigma)
    }
