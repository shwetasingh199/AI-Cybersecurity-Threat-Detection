"""Dataset loading and safe synthetic network-traffic generation for demos."""
from __future__ import annotations
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "duration", "src_bytes", "dst_bytes", "failed_logins",
    "connection_count", "protocol_num", "service_num", "syn_error_rate",
    "dst_host_same_src_rate", "packet_rate"
]

def make_demo_dataset(n_rows: int = 3000, seed: int = 42) -> pd.DataFrame:
    """Create deterministic, clearly labelled synthetic data; not real traffic."""
    rng = np.random.default_rng(seed)
    n_attack = max(1, int(n_rows * 0.22))
    n_normal = n_rows - n_attack

    normal = pd.DataFrame({
        "duration": rng.gamma(2.0, 3.0, n_normal),
        "src_bytes": rng.lognormal(5.0, 1.0, n_normal),
        "dst_bytes": rng.lognormal(5.2, 1.0, n_normal),
        "failed_logins": rng.poisson(0.12, n_normal),
        "connection_count": rng.poisson(8, n_normal),
        "protocol_num": rng.choice([0, 1, 2], n_normal, p=[0.70, 0.20, 0.10]),
        "service_num": rng.integers(0, 8, n_normal),
        "syn_error_rate": rng.beta(1.2, 18, n_normal),
        "dst_host_same_src_rate": rng.beta(2, 5, n_normal),
        "packet_rate": rng.gamma(2.0, 4.0, n_normal),
        "label": "normal"
    })
    attacks = pd.DataFrame({
        "duration": rng.gamma(1.2, 1.5, n_attack),
        "src_bytes": rng.lognormal(4.5, 1.5, n_attack),
        "dst_bytes": rng.lognormal(3.5, 1.3, n_attack),
        "failed_logins": rng.poisson(5.0, n_attack),
        "connection_count": rng.poisson(38, n_attack),
        "protocol_num": rng.choice([0, 1, 2], n_attack, p=[0.45, 0.40, 0.15]),
        "service_num": rng.integers(0, 8, n_attack),
        "syn_error_rate": rng.beta(5, 2, n_attack),
        "dst_host_same_src_rate": rng.beta(5, 2, n_attack),
        "packet_rate": rng.gamma(8, 7, n_attack),
        "label": rng.choice(["dos", "brute_force", "scan"], n_attack, p=[0.48, 0.30, 0.22])
    })
    df = pd.concat([normal, attacks], ignore_index=True)
    # Add a few missing values to make the cleaning step realistic.
    for col in ["src_bytes", "dst_bytes"]:
        idx = rng.choice(df.index, size=max(1, int(0.005 * len(df))), replace=False)
        df.loc[idx, col] = np.nan
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)

def load_csv(uploaded_file) -> pd.DataFrame:
    """Load a user CSV. Requires numeric features and optionally a label column."""
    df = pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def prepare_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    for col in df.columns:
        if col != "label":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    numeric = [c for c in df.columns if c != "label" and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric:
        raise ValueError("No numeric feature columns found. Please upload a CSV with numeric network features.")
    df[numeric] = df[numeric].replace([np.inf, -np.inf], np.nan)
    df[numeric] = df[numeric].fillna(df[numeric].median(numeric_only=True)).fillna(0)
    if "label" in df.columns:
        df["label"] = df["label"].fillna("unknown").astype(str).str.lower().str.strip()
    return df, numeric
