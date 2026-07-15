# Experimental Data QC & Statistics Dashboard

A configurable workflow for plate assays, qPCR, growth curves and treatment comparisons.

[Click here to view the Live Interactive Web App Demo](https://experimental-data-qc-statistics-dashboard-trial-ebwmuzn8xcbhl2.streamlit.app/)

## Features

- CSV/XLSX input
- Schema, missing-value and duplicate checks
- Replicate summaries and coefficient of variation
- IQR outlier flags
- Descriptive statistics
- Two-group Welch t-test or multi-group one-way ANOVA
- Benjamini-Hochberg correction
- Downloadable QC, summary and test tables

## Local setup (Windows CMD)

```cmd
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python cli.py --input examples/assay.csv --config configs/default.yaml --output outputs
streamlit run app.py
```

Open `http://localhost:8501`.

## Docker

```cmd
docker build -t experimental-qc-stats .
docker run --rm -p 8501:8501 experimental-qc-stats
```

Statistical tests must match the study design; this app does not replace experimental-design review.

## Streamlit performance

The app uses a submit form, `st.cache_data`, immutable upload bytes, and session-state result persistence. This prevents the analysis from running again when a widget changes. The sequence-comparison apps also use a direct linear comparison for closely related equal-length sequences and reserve global alignment for likely indels or larger differences.
