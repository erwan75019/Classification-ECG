from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


TRAINING_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = TRAINING_DIR / "artifacts"
DATA_DIR = TRAINING_DIR / "data" / "raw"

TRAIN_URL = DATA_DIR / "ECG200_TRAIN.tsv"
TEST_URL = DATA_DIR / "ECG200_TEST.tsv"

SCALER_PATH = ARTIFACTS_DIR / "scaler.save"


def load_data():
    train_df = pd.read_csv(TRAIN_URL, sep="\t")
    test_df = pd.read_csv(TEST_URL, sep="\t")

    train_df = train_df.dropna()
    test_df = test_df.dropna()

    X_train = train_df.iloc[:, 1:].values.astype(np.float32)
    y_train = train_df.iloc[:, 0].values

    X_test = test_df.iloc[:, 1:].values.astype(np.float32)
    y_test = test_df.iloc[:, 0].values

    y_train = (y_train == 1).astype(int)
    y_test = (y_test == 1).astype(int)

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)

    print(f"Scaler sauvegardé dans : {SCALER_PATH}")

    return X_train, X_test, y_train, y_test


def reshape_for_sequence_models(X):
    return X.reshape((X.shape[0], X.shape[1], 1))
