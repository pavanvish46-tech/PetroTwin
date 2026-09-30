from ml.models.production.train import train as train_production
from ml.models.temperature.train import train as train_temperature
from ml.models.failure.train import train as train_failure
from ml.models.anomaly.train import train as train_anomaly

if __name__=="__main__":
    print("=== PRODUCTION ===")
    train_production()

    print("\n=== TEMPERATURE ===")
    train_temperature()

    print("\n=== FAILURE ===")
    train_failure()

    print("\n=== ANOMALY ===")
    train_anomaly()
