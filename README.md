# SentinelAI — AI-Powered Cybersecurity Threat Detection

A beginner-friendly, GitHub-ready security analytics project with a Streamlit SOC-style dashboard. It uses labelled network-flow-like records, a Random Forest classifier, Isolation Forest anomaly detection, transparent triage rules, visual summaries, and downloadable alert queues.

> **Important:** The default dataset is synthetic and exists only to demonstrate the workflow. This is not a production intrusion-detection system, and model output is not proof that a real incident occurred.

## Features

- **SOC-style dashboard:** records, alerts, severity counts, charts, investigation view.
- **Synthetic traffic generator:** run immediately without downloading a dataset.
- **CSV upload:** load your own numeric network-flow dataset.
- **Preprocessing:** normalizes column names, converts numeric values, handles missing/infinite values.
- **Feature engineering:** total bytes and connections-per-second when source columns exist.
- **Supervised ML:** Random Forest classifier if a `label` column has at least two classes.
- **Unsupervised ML:** Isolation Forest anomaly flag and relative anomaly score.
- **Explainable triage rules:** repeated login failures, connection bursts, high SYN-error rate.
- **Evaluation:** accuracy, weighted precision/recall/F1 and per-class report.
- **Exports:** cleaned data and alert queue as CSV.

## Problem statement

Security teams receive large volumes of network telemetry and authentication events. Manual review alone can be slow, so analytics pipelines help prioritize unusual activity for investigation. This project demonstrates a small educational version of that pipeline: prepare telemetry-like data, train models, score records, apply triage rules, and present a review queue.

## Industry relevance

Related concepts are used in security information and event management (SIEM), network intrusion detection, fraud analytics, endpoint detection, and anomaly monitoring. Real deployments additionally require validated data sources, threat-intelligence enrichment, identity and asset context, alert deduplication, analyst feedback, access controls, monitoring, and rigorous testing.

## Architecture

```text
CSV / Synthetic telemetry
          |
          v
Column normalization + missing-value handling
          |
          v
Feature engineering
          |
          +--------------------+
          |                    |
          v                    v
Random Forest classifier   Isolation Forest
(labelled data)            (outlier scoring)
          |                    |
          +---------+----------+
                    v
      Rule-based triage + severity
                    |
                    v
       Streamlit SOC dashboard
                    |
           CSV alert export
```

## Tech stack

- Python 3.10 or 3.11
- Pandas, NumPy
- scikit-learn
- Matplotlib, Seaborn
- Streamlit
- Joblib

No GPU is required.

## Folder structure

```text
AI-Cybersecurity-Threat-Detection/
├── app/
│   └── dashboard.py
├── data/
│   └── .gitkeep
├── docs/
│   └── PROJECT_NOTES.md
├── images/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── notebooks/
│   └── .gitkeep
├── outputs/
│   └── .gitkeep
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── detection.py
│   ├── features.py
│   ├── modeling.py
│   └── visuals.py
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Installation

### Windows (PowerShell)

```powershell
cd AI-Cybersecurity-Threat-Detection
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
cd AI-Cybersecurity-Threat-Detection
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app/dashboard.py
```

Alternative launcher:

```bash
python main.py
```

The browser should open a local dashboard. Choose **Synthetic demo dataset**, set the number of records, and click **Train models and run detection**. The first run trains models and writes local model files into `models/`.

## Uploading a dataset

Use a CSV with numeric feature columns. If a `label` column is present and contains at least two classes, the app trains a supervised classifier and calculates test metrics. Example supported feature names include:

- `duration`
- `src_bytes`
- `dst_bytes`
- `failed_logins`
- `connection_count`
- `protocol_num`
- `service_num`
- `syn_error_rate`
- `dst_host_same_src_rate`
- `packet_rate`

Other numeric column names are also accepted. For an external dataset, map its target column to `label` and encode non-numeric features appropriately before upload. Do not upload confidential or personally identifiable logs to a public repository.

### Public dataset ideas

For a more rigorous experiment, explore official dataset pages and their licences/documentation before use:

- UNSW-NB15: https://research.unsw.edu.au/projects/unsw-nb15-dataset
- CIC-IDS2017: https://www.unb.ca/cic/datasets/ids-2017.html
- KDD Cup 1999: https://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html

Dataset schemas and label names differ. Preprocessing and feature mapping may be required. Keep original datasets out of Git if large or licence-restricted; document download instructions instead.

## How the detection logic works

1. **Classifier:** predicts a class learned from labelled records (for example `normal`, `dos`, `brute_force`, or `scan`).
2. **Isolation Forest:** estimates whether a record is unusual relative to the batch. `anomaly_score` is a relative score, not a calibrated probability.
3. **Rules:** flags repeated login failures, high connection counts, and high SYN-error rates when those columns exist.
4. **Severity:** combines selected rule signals and anomaly flags to prioritize review. It is a demo heuristic, not a formal risk score.

## Metrics and honest reporting

Use a held-out test split and report accuracy, precision, recall, and F1. For security work, also inspect per-class recall, false positives, false negatives, class imbalance, and performance on a time-separated or external test set. A high score on synthetic data does not demonstrate real-world security effectiveness.

## Screenshot checklist

Save your own screenshots after running the app:

```text
images/
├── 01_dashboard_overview.png
├── 02_dataset_preview.png
├── 03_model_metrics.png
├── 04_alert_queue.png
└── 05_investigation_record.png
```

Embed them here after capturing:

```markdown
![Dashboard overview](images/01_dashboard_overview.png)
![Model metrics](images/03_model_metrics.png)
![Alert queue](images/04_alert_queue.png)
```

Do not add fabricated screenshots or claim performance numbers before running the experiment.

## GitHub publishing

```bash
git init
git add .
git commit -m "Initial commit: add SentinelAI threat detection dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/AI-Cybersecurity-Threat-Detection.git
git push -u origin main
```

Suggested repository description:

> Dataset-driven AI cybersecurity lab with Random Forest classification, Isolation Forest anomaly detection, explainable triage rules, and a Streamlit SOC dashboard.

Suggested topics: `cybersecurity`, `machine-learning`, `anomaly-detection`, `intrusion-detection`, `python`, `scikit-learn`, `streamlit`, `security-analytics`.

## Limitations and next steps

- The default data is synthetic and not representative of all real network environments.
- The demo scores a batch, not a live packet stream.
- Isolation Forest scores are not probabilities.
- The triage rules are illustrative and need tuning and validation.
- Production systems need authenticated telemetry ingestion, access controls, secure logging, alert deduplication, analyst feedback, drift monitoring, deployment hardening, and documented incident-response procedures.

Potential extensions: add a CICIDS/UNSW dataset adapter, time-based evaluation, threshold tuning, SHAP-style explanations, unit tests, model versioning, and a Docker deployment.
