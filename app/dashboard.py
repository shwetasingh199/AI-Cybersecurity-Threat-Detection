from pathlib import Path
import sys
import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import make_demo_dataset, load_csv, prepare_dataset
from src.features import add_derived_features
from src.modeling import train_models
from src.detection import run_detection
from src.config import OUTPUT_DIR

st.set_page_config(page_title="SentinelAI | Threat Detection Lab", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.main {background-color:#0b1220;}
[data-testid="stMetric"] {background:#111c30;padding:14px;border:1px solid #27364e;border-radius:12px;}
div[data-testid="stDataFrame"] {border:1px solid #27364e;border-radius:10px;}
.small-note {color:#9caec7;font-size:0.9rem}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SentinelAI — AI-Powered Cybersecurity Threat Detection")
st.caption("A local, dataset-driven SOC simulation for learning and portfolio demonstration.")
st.warning("Educational prototype: the included traffic is synthetic. This is not a production IDS and must not be used as the sole security control.")

with st.sidebar:
    st.header("Control Center")
    source = st.radio("Data source", ["Synthetic demo dataset", "Upload CSV"])
    uploaded = st.file_uploader("Upload network-flow CSV", type=["csv"]) if source == "Upload CSV" else None
    n_rows = st.slider("Synthetic records", 500, 10000, 3000, step=500) if source == "Synthetic demo dataset" else None
    st.markdown("---")
    st.subheader("Detection controls")
    anomaly_enabled = st.checkbox("Enable Isolation Forest", value=True)
    st.caption("The model learns patterns from the loaded batch. For real deployments, validate on representative, labelled traffic.")

try:
    if source == "Upload CSV":
        if uploaded is None:
            st.info("Upload a CSV file to continue. For a quick walkthrough, select Synthetic demo dataset.")
            st.stop()
        raw = load_csv(uploaded)
    else:
        raw = make_demo_dataset(n_rows=n_rows)
    cleaned, numeric_features = prepare_dataset(raw)
    enriched, features = add_derived_features(cleaned, numeric_features)
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", f"{len(enriched):,}")
c2.metric("Numeric features", len(features))
c3.metric("Label classes", enriched["label"].nunique() if "label" in enriched else "N/A")
c4.metric("Missing values after cleaning", int(enriched[features].isna().sum().sum()))

with st.expander("Dataset preview", expanded=False):
    st.dataframe(enriched.head(20), use_container_width=True)
    st.download_button("Download cleaned dataset", enriched.to_csv(index=False).encode("utf-8"),
                       "cleaned_network_traffic.csv", "text/csv")

if st.button("🚀 Train models and run detection", type="primary", use_container_width=True):
    with st.spinner("Training models and scoring records..."):
        classifier, anomaly, metrics = train_models(enriched, features)
        clf_pack = {"model": classifier, "encoder": None, "features": features} if classifier is not None else None
        # Load the exact persisted encoder/model package so label decoding is preserved.
        from src.config import MODEL_DIR
        import joblib
        if classifier is not None:
            clf_pack = joblib.load(MODEL_DIR / "classifier.joblib")
        anomaly_pack = joblib.load(MODEL_DIR / "anomaly_detector.joblib") if anomaly_enabled else None
        detected = run_detection(enriched, features, clf_pack, anomaly_pack)
        st.session_state["detected"] = detected
        st.session_state["metrics"] = metrics
        st.session_state["features"] = features
        st.session_state["training_rows"] = len(enriched)

if "detected" not in st.session_state:
    st.info("Choose a data source, then click **Train models and run detection**.")
    st.markdown("### What this demo includes")
    st.write("- Supervised Random Forest classification when labels are available")
    st.write("- Isolation Forest anomaly scoring")
    st.write("- Transparent triage rules for repeated login failures, connection bursts and SYN-error spikes")
    st.write("- Alert table, risk metrics, charts, CSV export and a synthetic dataset")
    st.stop()

detected = st.session_state["detected"]
metrics = st.session_state["metrics"]
alerts = detected[detected["alert"]]
high = int((alerts["severity"] == "HIGH").sum())
med = int((alerts["severity"] == "MEDIUM").sum())

st.markdown("## Security Operations Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Alerts", f"{len(alerts):,}", f"{len(alerts)/max(len(detected),1):.1%} of records")
m2.metric("High severity", high)
m3.metric("Medium severity", med)
m4.metric("Anomalies", int(detected["anomaly_flag"].sum()))

left, right = st.columns(2)
with left:
    st.subheader("Alert severity distribution")
    counts = detected.loc[detected["alert"], "severity"].value_counts()
    if len(counts):
        fig, ax = plt.subplots(figsize=(6, 3.5))
        counts.reindex(["HIGH", "MEDIUM", "LOW", "INFO"], fill_value=0).plot(kind="bar", ax=ax)
        ax.set_ylabel("Records")
        ax.set_xlabel("Severity")
        ax.set_title("Triage queue")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No alerts for this batch.")
with right:
    st.subheader("Traffic behavior")
    plot_col = "connection_count" if "connection_count" in detected else features[0]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    normal = detected[~detected["alert"]]
    suspicious = detected[detected["alert"]]
    if len(normal):
        ax.hist(normal[plot_col], bins=30, alpha=0.65, label="No alert")
    if len(suspicious):
        ax.hist(suspicious[plot_col], bins=30, alpha=0.65, label="Alert")
    ax.set_xlabel(plot_col)
    ax.set_ylabel("Count")
    ax.legend()
    ax.set_title(f"{plot_col}: alert vs no alert")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Model evaluation")
if "accuracy" in metrics:
    a, b, c, d = st.columns(4)
    a.metric("Accuracy", f"{metrics['accuracy']:.3f}")
    b.metric("Weighted precision", f"{metrics['precision_weighted']:.3f}")
    c.metric("Weighted recall", f"{metrics['recall_weighted']:.3f}")
    d.metric("Weighted F1", f"{metrics['f1_weighted']:.3f}")
    with st.expander("Per-class report"):
        report = pd.DataFrame(metrics["classification_report"]).T
        st.dataframe(report.round(3), use_container_width=True)
else:
    st.info(metrics.get("note", "Supervised metrics unavailable."))

st.subheader("Alert triage queue")
severity_filter = st.multiselect("Show severity", ["HIGH", "MEDIUM", "LOW", "INFO"], default=["HIGH", "MEDIUM", "LOW"])
search = st.text_input("Filter by predicted class or rule", "")
view = alerts[alerts["severity"].isin(severity_filter)].copy()
if search:
    mask = view["predicted_class"].astype(str).str.contains(search, case=False, na=False) | view["rule_flags"].astype(str).str.contains(search, case=False, na=False)
    view = view[mask]
display_cols = [c for c in ["severity", "predicted_class", "model_confidence", "anomaly_flag", "anomaly_score", "rule_flags", "connection_count", "failed_logins", "syn_error_rate"] if c in view.columns]
st.dataframe(view[display_cols].head(500), use_container_width=True, height=350)
st.download_button("⬇️ Export alert queue (CSV)", view.to_csv(index=False).encode("utf-8"),
                   "sentinelai_alerts.csv", "text/csv")

st.subheader("Investigate one record")
if len(detected):
    selected = st.number_input("Row index in scored results", min_value=0, max_value=max(0, len(detected)-1), value=0, step=1)
    row = detected.iloc[int(selected)]
    st.json({k: (v.item() if hasattr(v, "item") else v) for k, v in row.to_dict().items()})

st.markdown("---")
st.markdown('<p class="small-note">Portfolio note: report the dataset source, class balance, split strategy, false-positive rate, and limitations. Never claim this demo protects a real network.</p>', unsafe_allow_html=True)
