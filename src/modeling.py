"""Supervised classifier and unsupervised anomaly model."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer
from src.config import MODEL_DIR, RANDOM_STATE

def train_models(df: pd.DataFrame, feature_columns: list[str], target_col: str = "label"):
    X = df[feature_columns].replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True)).fillna(0)
    y_text = df[target_col].astype(str).str.lower() if target_col in df.columns else None
    if y_text is not None and y_text.nunique() >= 2:
        encoder = LabelEncoder()
        y = encoder.fit_transform(y_text)
        stratify = y if min(pd.Series(y).value_counts()) >= 2 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=stratify
        )
        classifier = RandomForestClassifier(
            n_estimators=180, max_depth=None, min_samples_leaf=2,
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
        )
        classifier.fit(X_train, y_train)
        pred = classifier.predict(X_test)
        metrics = {
            "accuracy": float(accuracy_score(y_test, pred)),
            "precision_weighted": float(precision_score(y_test, pred, average="weighted", zero_division=0)),
            "recall_weighted": float(recall_score(y_test, pred, average="weighted", zero_division=0)),
            "f1_weighted": float(f1_score(y_test, pred, average="weighted", zero_division=0)),
            "classification_report": classification_report(
                y_test, pred, labels=np.arange(len(encoder.classes_)),
                target_names=encoder.classes_, output_dict=True, zero_division=0
            ),
            "classes": encoder.classes_.tolist(),
            "test_rows": int(len(y_test))
        }
        joblib.dump({"model": classifier, "encoder": encoder, "features": feature_columns},
                    MODEL_DIR / "classifier.joblib")
    else:
        classifier = None
        metrics = {"note": "No usable label column with at least two classes; supervised metrics skipped."}

    anomaly = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", IsolationForest(n_estimators=180, contamination=0.08, random_state=RANDOM_STATE))
    ])
    anomaly.fit(X)
    joblib.dump({"model": anomaly, "features": feature_columns}, MODEL_DIR / "anomaly_detector.joblib")
    return classifier, anomaly, metrics

def load_model(path: Path):
    return joblib.load(path)
