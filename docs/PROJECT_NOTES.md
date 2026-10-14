# Project notes

## Safe and realistic scope
This project is a dataset-driven simulation. It does not sniff packets, scan networks, execute malware, or attack hosts. That makes it appropriate for a student portfolio without access to corporate systems.

## Demo attack patterns
- DoS-like: high connection counts, elevated packet rate, high SYN-error rate.
- Brute-force-like: repeated failed login attempts.
- Scan-like: unusual connection and destination/service patterns.

These are synthetic patterns for learning, not canonical definitions of these attacks.

## Suggested experiment record
For each dataset/model version, record:
- dataset name, version, licence and source URL
- number of rows and class distribution
- feature list and cleaning decisions
- train/test split approach
- accuracy, precision, recall, F1, per-class recall
- false-positive and false-negative examples
- known limitations

## Industry-grade follow-up checklist
- [ ] Add schema validation and unit tests.
- [ ] Evaluate on a public, labelled IDS dataset.
- [ ] Use time-based split when timestamps exist.
- [ ] Tune alert thresholds against false-positive cost.
- [ ] Add model/data version metadata.
- [ ] Add analyst disposition and alert deduplication.
- [ ] Add authentication and role-based access before any shared deployment.
- [ ] Never commit secrets, private logs, or sensitive telemetry.
