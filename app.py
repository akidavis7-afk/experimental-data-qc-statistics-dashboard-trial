from __future__ import annotations

import io
from pathlib import Path
from time import perf_counter

import pandas as pd
import streamlit as st
import yaml

from src.core import analyze

MAX_ROWS = 200_000
MAX_UPLOAD_MB = 25


@st.cache_data(show_spinner=False, max_entries=20)
def load_uploaded_table(file_bytes: bytes, filename: str) -> pd.DataFrame:
    buffer = io.BytesIO(file_bytes)
    if Path(filename).suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(buffer)
    return pd.read_csv(buffer)


@st.cache_data(show_spinner=False, max_entries=20)
def analyze_cached(
    file_bytes: bytes,
    filename: str,
    group_column: str,
    value_columns: tuple[str, ...],
    replicate_column: str | None,
    id_columns: tuple[str, ...],
) -> dict:
    frame = load_uploaded_table(file_bytes, filename)
    return analyze(frame, group_column, list(value_columns), replicate_column, list(id_columns))


with open("configs/default.yaml", encoding="utf-8") as handle:
    cfg = yaml.safe_load(handle) or {}

st.set_page_config(page_title=cfg.get("app_title", "Experimental Data QC & Statistics Dashboard"), layout="wide")
st.title(cfg.get("app_title", "Experimental Data QC & Statistics Dashboard"))
st.caption("Routine experimental-table QC and first-pass statistics. Confirm that each test matches the study design.")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    if len(file_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
        st.error(f"The uploaded file exceeds {MAX_UPLOAD_MB} MB.")
    else:
        try:
            frame = load_uploaded_table(file_bytes, uploaded_file.name)
            if len(frame) > MAX_ROWS:
                st.error(f"The table contains more than {MAX_ROWS:,} rows.")
            elif frame.empty:
                st.error("The uploaded table is empty.")
            else:
                st.subheader("Data preview")
                st.dataframe(frame.head(100), use_container_width=True, hide_index=True)

                columns = list(frame.columns)
                numeric_columns = [column for column in columns if pd.api.types.is_numeric_dtype(frame[column])]
                default_group = cfg.get("group_column")
                default_group_index = columns.index(default_group) if default_group in columns else 0
                default_values = [column for column in cfg.get("value_columns", []) if column in numeric_columns]

                with st.form("statistics_form"):
                    group_column = st.selectbox("Group column", columns, index=default_group_index)
                    value_columns = st.multiselect(
                        "Numeric value columns",
                        numeric_columns,
                        default=default_values,
                    )
                    replicate_options = ["<none>", *columns]
                    configured_replicate = cfg.get("replicate_column")
                    replicate_index = (
                        replicate_options.index(configured_replicate)
                        if configured_replicate in replicate_options
                        else 0
                    )
                    replicate_selection = st.selectbox(
                        "Replicate column (optional)",
                        replicate_options,
                        index=replicate_index,
                    )
                    default_ids = [column for column in cfg.get("id_columns", []) if column in columns]
                    id_columns = st.multiselect("Identifier columns (optional)", columns, default=default_ids)
                    submitted = st.form_submit_button("Run QC and statistics", type="primary")

                if submitted:
                    if not value_columns:
                        st.error("Select at least one numeric value column.")
                    else:
                        replicate_column = None if replicate_selection == "<none>" else replicate_selection
                        started = perf_counter()
                        with st.spinner("Running QC and statistical summaries..."):
                            result = analyze_cached(
                                file_bytes,
                                uploaded_file.name,
                                group_column,
                                tuple(value_columns),
                                replicate_column,
                                tuple(id_columns),
                            )
                        st.session_state["statistics_result"] = result
                        st.session_state["statistics_elapsed"] = perf_counter() - started
        except Exception as exc:
            st.exception(exc)

result = st.session_state.get("statistics_result")
if result:
    st.success(f"Analysis completed in {st.session_state.get('statistics_elapsed', 0.0):.2f} seconds.")
    for title, key in [
        ("QC findings", "qc"),
        ("Descriptive summary", "summary"),
        ("Statistical tests", "tests"),
    ]:
        st.subheader(title)
        st.dataframe(result[key], use_container_width=True, hide_index=True)

    st.download_button(
        "Download annotated data",
        result["annotated"].to_csv(index=False).encode("utf-8"),
        "annotated_data.csv",
        "text/csv",
    )
