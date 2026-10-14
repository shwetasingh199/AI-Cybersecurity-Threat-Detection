"""Prediction, rule-based triage and alert severity."""
import numpy as np
import pandas as pd

def run_detection(df: pd.DataFrame, feature_columns: list[str], classifier=None, anomaly_model=None):
    X = df[feature_columns].replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True)).fillna(0)
    out = df.copy()
    if classifier is not None:
        pack = classifier
        model = pack["model"] if isinstance(pack, dict) else pack
        encoder = pack.get("encoder") if isinstance(pack, dict) else None
        pred = model.predict(X)
        out["predicted_class"] = encoder.inverse_transform(pred) if encoder is not None else pred.astype(str)
        if hasattr(model, "predict_proba"):
            out["model_confidence"] = model.predict_proba(X).max(axis=1)
        else:
            out["model_confidence"] = np.nan
    else:
        out["predicted_class"] = "unclassified"
        out["model_confidence"] = np.nan

    if anomaly_model is not None:
        pack = anomaly_model
        model = pack["model"] if isinstance(pack, dict) else pack
        out["anomaly_flag"] = model.predict(X) == -1
        # Lower decision_function values are more anomalous. This is a relative score, not a probability.
        scores = model.decision_function(X)
        out["anomaly_score"] = -scores
    else:
        out["anomaly_flag"] = False
        out["anomaly_score"] = 0.0

    # Transparent triage rules complement—not replace—the ML models.
    failed = out["failed_logins"] if "failed_logins" in out else pd.Series(0, index=out.index)
    conns = out["connection_count"] if "connection_count" in out else pd.Series(0, index=out.index)
    syn = out["syn_error_rate"] if "syn_error_rate" in out else pd.Series(0, index=out.index)
    out["rule_flags"] = [
        ", ".join(name for name, yes in [
            ("repeated_login_failures", f >= 4),
            ("connection_burst", c >= 30),
            ("high_syn_error_rate", s >= 0.65)
        ] if yes) or "none"
        for f, c, s in zip(failed, conns, syn)
    ]
    out["alert"] = out["anomaly_flag"] | (out["rule_flags"] != "none") | (
        out["predicted_class"].astype(str).str.lower().ne("normal") &
        out["predicted_class"].astype(str).str.lower().ne("unclassified")
    )
    out["severity"] = np.select(
        [
            out["rule_flags"].str.contains("repeated_login_failures|connection_burst", regex=True) & out["anomaly_flag"],
            out["rule_flags"].str.contains("repeated_login_failures|connection_burst", regex=True),
            out["anomaly_flag"]
        ],
        ["HIGH", "MEDIUM", "MEDIUM"],
        default="LOW"
    )
    out.loc[~out["alert"], "severity"] = "INFO"
    return out.sort_values(["alert", "anomaly_score"], ascending=[False, False]).reset_index(drop=True)
