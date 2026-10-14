"""Feature validation and small, transparent derived-feature helpers."""
import pandas as pd

def add_derived_features(df: pd.DataFrame, feature_columns: list[str]) -> tuple[pd.DataFrame, list[str]]:
    out = df.copy()
    columns = list(feature_columns)
    if "src_bytes" in out and "dst_bytes" in out:
        out["total_bytes"] = out["src_bytes"].fillna(0) + out["dst_bytes"].fillna(0)
        columns.append("total_bytes")
    if "connection_count" in out and "duration" in out:
        out["connections_per_second"] = out["connection_count"] / (out["duration"].fillna(0) + 1.0)
        columns.append("connections_per_second")
    return out, columns
