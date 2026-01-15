# Hyperparameter Selection
- Dataset: Multivariate sensor time-series data
- Characteristics:
  - High noise
  - Temporal dependency
  - Class imbalance (Failure < 5%)

Therefore:
- Optimizer: Adam
- Batch size: 32
- Learning rate: 0.001

Rationale:
Small batch size preserves anomaly patterns,
and Adam provides stable convergence under noisy gradients.

threshold = 99th percentile of reconstruction error

The dataset is structured tabular sensor data with severe class imbalance.
Since failures are rare events, the problem is treated as an anomaly-centric task
rather than a conventional classification problem.

AI-based anomaly detection integrates multiple unsupervised models
(Isolation Forest and LOF) to generate a unified anomaly flag (ai_anomaly),
which complements rule-based anomaly detection.