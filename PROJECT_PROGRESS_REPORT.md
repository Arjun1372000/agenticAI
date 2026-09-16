# Predictive Maintenance & Agentic Bearing Diagnostics

## Project Progress Report — Phase 1

### 1. Project Goal

The project aims to develop an **agentic predictive-maintenance system for industrial rotating equipment**, primarily focused on bearing health monitoring.

The intended final system will take vibration telemetry from industrial bearings, analyze degradation and fault signatures, estimate Remaining Useful Life (RUL), and use an AI agent to orchestrate diagnostic tools and produce actionable maintenance recommendations.

The eventual architecture is:

```text
Industrial Bearing
        ↓
Vibration Telemetry
        ↓
Signal Processing / Feature Extraction
        ↓
Health & Fault Diagnostics
        ↓
RUL Estimation
        ↓
MCP Tools
        ↓
Agentic AI
        ↓
Maintenance Recommendation
        ↓
Maintenance Engineer
```

The **maintenance/condition-monitoring engineer** is the primary end user. The dashboard is intended to answer:

1. Which bearing requires attention?
2. What evidence indicates degradation?
3. How severe is the condition?
4. What is the estimated remaining useful life?
5. What maintenance action should be considered?

---

# 2. Dataset

The project uses the NASA/IMS bearing run-to-failure dataset obtained from Kaggle.

The local dataset is intentionally excluded from Git because of its size.

Current local structure:

```text
bearing-dataset/
│
├── 1st_test/
│   └── 1st_test/
│
├── 2nd_test/
│   └── 2nd_test/
│
└── 3rd_test/
    └── 4th_test/
        └── txt/
```

Verified local dataset contents:

| Experiment | Files | Channels / Recording |
| ---------- | ----: | -------------------: |
| Test 1     | 2,156 |           20,480 × 8 |
| Test 2     |   984 |           20,480 × 4 |
| Test 3     | 6,324 |           20,480 × 4 |

The recordings are timestamp-named vibration files.

Each recording represents a short vibration measurement, allowing the dataset to be treated as a sequence of observations over an experiment's lifetime.

---

# 3. Initial EDA

The original `EDA.ipynb` is being retained as an **experimentation and research notebook**.

It is not part of the production application pipeline.

The notebook currently focuses primarily on **Test 2** and explores:

* healthy versus degraded vibration behaviour
* individual bearing behaviour
* statistical vibration features
* FFT/frequency-domain analysis
* feature extraction across the complete Test-2 run
* RUL generation from timestamps

The notebook established the initial analytical foundation that is now being converted into reusable Python modules.

The production system does **not** import or depend on `EDA.ipynb`.

---

# 4. Production Project Structure

The project has been reorganized so experimental work and application code remain separate.

Current structure:

```text
agenticAI/
│
├── bearing-dataset/                 # local raw dataset, Git ignored
│
├── data/
│   └── processed/
│       └── test2_features.csv
│
├── models/
│
├── notebooks/
│
├── scripts/
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_observations.py
│   ├── build_test2_features.py
│   └── test_rul.py
│
├── src/
│   └── predictive_maintenance/
│       ├── __init__.py
│       ├── data.py
│       ├── features.py
│       ├── observations.py
│       ├── build_features.py
│       ├── rul.py
│       └── api.py
│
├── tests/
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── EDA.ipynb
├── pyproject.toml
├── README.md
└── .gitignore
```

The Python project uses a modern `src/` layout with `pyproject.toml`.

The package is installed in editable mode during development:

```powershell
python -m pip install -e .
```

This means the application can import:

```python
from predictive_maintenance import ...
```

without manually setting `PYTHONPATH`.

---

# 5. Data Layer

A reusable `data.py` module has been created.

Its responsibilities are deliberately limited to **raw dataset access**.

It currently supports all three experiments and stores experiment-specific metadata using `TestConfig`.

The loader verifies:

* dataset path
* file existence
* file structure
* channel count
* numeric values
* timestamp format

Verified results:

```text
Test 1 → 2156 files → 20480 × 8
Test 2 →  984 files → 20480 × 4
Test 3 → 6324 files → 20480 × 4
```

The unusual Test-3 path is explicitly handled:

```text
bearing-dataset/
└── 3rd_test/
    └── 4th_test/
        └── txt/
```

This prevents Test 3 from being hardcoded or ignored later.

---

# 6. Feature Extraction

A production `features.py` module has been created.

It contains a reusable:

```python
extract_features(signal)
```

function.

Four vibration features are currently extracted:

### RMS

Root Mean Square vibration amplitude.

### Kurtosis

Pearson kurtosis is used, matching the existing EDA implementation.

### Peak-to-Peak

Difference between the maximum and minimum vibration values.

### Crest Factor

Peak absolute amplitude divided by RMS.

The returned representation is a `VibrationFeatures` object containing:

```text
rms
kurtosis
peak_to_peak
crest_factor
```

The implementation was independently tested using a 20,480-sample signal.

---

# 7. Raw File Verification

A real Test-2 file was successfully loaded:

```text
2004.02.12.10.32.39
```

Verified structure:

```text
Shape: (20480, 4)
```

Example values:

```text
       0      1      2      3
0 -0.049 -0.071 -0.132 -0.010
1 -0.042 -0.073 -0.007 -0.105
2  0.015  0.000  0.007  0.000
...
```

All four columns were successfully interpreted as numeric vibration channels.

---

# 8. Feature Dataset

The production feature-building pipeline has now been executed on **all 984 Test-2 recordings**.

Pipeline:

```text
Raw Test-2 recording
        ↓
Load 20,480 × 4 vibration matrix
        ↓
Process each bearing
        ↓
Extract 4 features per bearing
        ↓
Create one timestamped observation
```

The resulting file is:

```text
data/processed/test2_features.csv
```

Verified output:

```text
Rows:    984
Columns: 17
```

The 17 columns consist of:

```text
Timestamp

B1_RMS
B1_Kurtosis
B1_Peak2Peak
B1_CrestFactor

B2_RMS
B2_Kurtosis
B2_Peak2Peak
B2_CrestFactor

B3_RMS
B3_Kurtosis
B3_Peak2Peak
B3_CrestFactor

B4_RMS
B4_Kurtosis
B4_Peak2Peak
B4_CrestFactor
```

Therefore:

```text
984 recordings
×
4 bearings
×
4 features
```

have now been transformed into a compact time-series feature representation.

---

# 9. Bearing Observation Layer

An `observations.py` module was added to provide a bearing-oriented representation.

Instead of forcing downstream components to work with the wide table:

```text
B1_RMS
B1_Kurtosis
B1_Peak2Peak
...
```

the system can request a specific bearing and obtain:

```text
Timestamp
bearing_id
rms
kurtosis
peak_to_peak
crest_factor
```

For Bearing 1:

```text
Shape: (984, 6)
```

This representation is intended to simplify:

* API responses
* dashboard visualizations
* bearing-specific analysis
* future ML models
* MCP tools

---

# 10. RUL Target

A reusable `rul.py` module has now been created.

The current Test-2 RUL definition is:

```text
RUL = time remaining until the final observation
```

The final Test-2 timestamp is:

```text
2004-02-19 06:22:39
```

The first observation has:

```text
RUL = 163.833333 hours
```

The final observation has:

```text
RUL = 0 hours
```

The resulting target contains:

```text
count    984
mean      81.916667
std       47.366772
min        0
25%       40.958333
50%       81.916667
75%      122.875000
max      163.833333
```

This is currently interpreted as **time-to-end-of-run under the experimental sequence**, rather than an absolute physical lifetime prediction.

No ML RUL model has been trained yet.

---

# 11. Backend API

A FastAPI backend has been implemented.

The initial API exposes the processed Test-2 data to the frontend.

Current endpoints include:

```text
GET /api/bearings/{bearing_id}/latest
GET /api/bearings/{bearing_id}/history
```

Examples:

```text
/api/bearings/1/latest
```

and:

```text
/api/bearings/1/history?limit=10
```

The API was successfully started with:

```powershell
uvicorn predictive_maintenance.api:app --reload
```

The endpoints were verified successfully.

FastAPI also provides automatic API documentation through:

```text
http://127.0.0.1:8000/docs
```

---

# 12. Web Application

The frontend has been separated into its own directory:

```text
frontend/
├── index.html
├── app.js
└── styles.css
```

The original dashboard used dummy/generated JavaScript telemetry.

That has now been replaced with API-driven data.

Current frontend flow:

```text
FastAPI
    ↓
GET /api/bearings/1/latest
GET /api/bearings/1/history
    ↓
JavaScript
    ↓
Dashboard
```

The dashboard currently displays:

* Bearing selection
* latest RMS
* latest kurtosis
* latest peak-to-peak
* latest crest factor
* historical feature trends
* latest timestamp
* dataset information

The dashboard is now consuming **real processed NASA IMS vibration data**, rather than generated telemetry.

The visual design has also been changed from a dark interface to a lighter **blue/green industrial monitoring theme**.

---

# 13. Current Architecture

The implemented architecture is currently:

```text
NASA IMS Bearing Dataset
          │
          ▼
       data.py
          │
          ▼
   Raw vibration matrix
          │
          ▼
      features.py
          │
          ▼
  Feature extraction
          │
          ▼
 build_features.py
          │
          ▼
test2_features.csv
          │
          ├──────────────┐
          ▼              ▼
   observations.py      rul.py
          │
          ▼
       FastAPI
          │
          ▼
       Frontend
          │
          ▼
  Bearing monitoring UI
```

This is the current **working vertical slice**.

---

# 14. What Has NOT Been Implemented Yet

The following are intentionally still future work:

```text
Health/degradation scoring
        ↓
RUL ML model
        ↓
Frequency-domain diagnostic module
        ↓
Fault classification
        ↓
Test 1 / Test 3 modeling
        ↓
MCP tools
        ↓
Agentic orchestration
        ↓
Agent reasoning
        ↓
Maintenance recommendations
```

These should be implemented on top of the current architecture rather than inside the notebook.

---

# 15. Important Design Decisions

### EDA remains experimental

`EDA.ipynb` is not part of the production execution path.

### Raw data is excluded from Git

The local `bearing-dataset/` directory remains outside version control because of dataset size.

### Test 2 is the initial development experiment

Test 2 is used first because the existing EDA was built around it and it provides a complete run-to-failure sequence suitable for developing the initial pipeline.

### All three experiments are supported at the data layer

The production loader already understands Test 1, Test 2, and Test 3.

### Models should use chronological evaluation

The project involves degradation over time, so random train/test splitting should be avoided for the primary RUL evaluation.

### LLM/agent comes after deterministic diagnostics

The intended architecture is:

```text
Signal processing
      ↓
ML / engineering diagnostics
      ↓
structured results
      ↓
Agent
```

rather than asking an LLM to directly infer engineering measurements from raw vibration.

---

# 16. Current Milestone

### Completed

```text
✓ Project packaging setup
✓ src/ package structure
✓ Dataset loader
✓ Test 1/2/3 dataset recognition
✓ Raw file validation
✓ Vibration feature extraction
✓ Test-2 feature extraction
✓ 984-record processed feature dataset
✓ Bearing-level observation representation
✓ RUL target generation
✓ FastAPI backend
✓ Real API data retrieval
✓ Frontend/backend integration
✓ Removal of dummy telemetry
✓ Initial monitoring dashboard
```

### Current position

```text
              PROJECT PROGRESS

Data ingestion        ####################  Complete
Feature extraction    ####################  Complete
Telemetry API         ####################  Complete
Dashboard integration ####################  Complete

Health modeling       ....................  Not started
RUL model             ....................  Not started
Fault diagnosis       ....................  Not started
MCP                   ....................  Not started
Agent                 ....................  Not started
```

These percentages describe **implementation progress by component**, not overall project quality.

---

# 17. Next Development Stage

The immediate next objective is to create a **health/degradation assessment** from the existing feature time series.

The intended path is:

```text
test2_features.csv
        ↓
Healthy baseline
        ↓
Feature deviation over time
        ↓
Degradation / anomaly score
        ↓
Healthy / Degraded / Critical
        ↓
FastAPI
        ↓
Dashboard
```

After that, the RUL model will be trained and evaluated.

The eventual project goal remains:

```text
REAL INDUSTRIAL TELEMETRY
          ↓
SIGNAL + FEATURE ANALYSIS
          ↓
FAULT / HEALTH DIAGNOSTICS
          ↓
RUL ESTIMATION
          ↓
MCP TOOLS
          ↓
AGENTIC AI
          ↓
EXPLAINABLE MAINTENANCE DECISION
```

The key achievement so far is that the project has moved from an exploratory notebook and mocked dashboard toward a real software pipeline in which **actual bearing vibration data is processed by Python and delivered to the web application through an API**.
