
import streamlit as st
import pandas as pd
import os

from core.agent import agent_run
from core.evaluator import evaluate
from storage.file_store import save_eval, load_all, load_eval

st.set_page_config(layout="wide")

# ---------------- NAV ----------------
pages = ["Upload", "All Evaluations", "Dataset View", "Failed Queries"]

if "menu" not in st.session_state:
    st.session_state["menu"] = "Upload"

if "selected_dataset" not in st.session_state:
    st.session_state["selected_dataset"] = None

menu = st.sidebar.radio("Navigation", pages, index=pages.index(st.session_state["menu"]))

if menu != st.session_state["menu"]:
    st.session_state["menu"] = menu

# =========================================================
# ---------------- UPLOAD ----------------
# =========================================================
if menu == "Upload":
    st.title("🚀 LLM Evaluator")
    st.write("**csv must contain input and ground_truth**")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    human_mode = st.checkbox("Human Review Mode")

    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df)

        if st.button("Run Evaluation"):
            results = []
            progress = st.progress(0)

            for i, row in df.iterrows():
                query = row["input"]
                gt = row["ground_truth"]

                agent_output = agent_run(query)

                final_answer = agent_output.get("final_answer", "")
                sql = agent_output.get("sql", "")
                raw_result = agent_output.get("raw_result", "")

                if human_mode:
                    results.append({
                        "query": query,
                        "gt": gt,
                        "output": final_answer,
                        "status": "pending_human"
                    })
                else:
                    scores = evaluate(query, gt, final_answer)

                    results.append({
                        "query": query,
                        "gt": gt,
                        "output": final_answer,
                        **scores
                    })

                progress.progress((i + 1) / len(df))

            eid = save_eval(results)

# 🔥 set the selected dataset immediately
            st.session_state["selected_dataset"] = eid
            st.session_state["menu"] = "Dataset View"

            st.success(f"Saved dataset: {eid}")
            st.rerun()
            

# =========================================================
# ---------------- ALL EVALUATIONS ----------------
# =========================================================
elif menu == "All Evaluations":
    st.title("📊 Evaluation Dashboard")

    files = load_all()

    dataset_metrics = []
    timeline = []
    total_failed_queries = 0

    for f in files:
        data = load_eval(f)
        df = pd.DataFrame(data["results"])

        metric_cols = [c for c in ["correctness", "relevance", "hallucination", "pii"] if c in df.columns]

        metrics = {"dataset": f, "timestamp": data["timestamp"]}

        for m in ["correctness", "relevance", "hallucination", "pii"]:
            metrics[m] = df[m].mean() if m in df else None

        # overall score (based on correctness + relevance only)
        if "correctness" in df.columns and "relevance" in df.columns:
            overall_score = df[["correctness", "relevance"]].mean().mean()
            failed_q = df[(df["correctness"] < 0.5) | (df["relevance"] < 0.5)]
            total_failed_queries += len(failed_q)
        else:
            overall_score = None
            failed_q = pd.DataFrame()

        metrics["overall_score"] = overall_score
        metrics["failed"] = overall_score is not None and overall_score < 0.5

        dataset_metrics.append(metrics)

        if data["timestamp"]:
            timeline.append({
                "time": pd.to_datetime(data["timestamp"], unit="s"),
                "correctness": metrics["correctness"],
                "relevance": metrics["relevance"],
                "hallucination": metrics["hallucination"],
                "pii": metrics["pii"],
                "failures": len(failed_q)
            })

    df_metrics = pd.DataFrame(dataset_metrics)
    timeline_df = pd.DataFrame(timeline)

    # =====================================================
    # 🔥 GLOBAL KPIs (FIXED)
    # =====================================================
    st.markdown("## 🚀 Global KPIs")

    def safe_avg(col):
        return round(df_metrics[col].dropna().mean(), 2) if col in df_metrics else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Correctness", safe_avg("correctness"))
    col2.metric("Relevance", safe_avg("relevance"))
    col3.metric("Hallucination", safe_avg("hallucination"))

    col4, col5, col6 = st.columns(3)
    col4.metric("PII", safe_avg("pii"))
    col5.metric("❌ Failed Queries", total_failed_queries)
    col6.metric("🚨 Failed Datasets", df_metrics["failed"].sum() if "failed" in df_metrics else 0)

    st.markdown("---")

    # =====================================================
    # 📊 DATASET COMPARISON
    # =====================================================
    st.markdown("### 📊 Dataset Comparison")

    metrics_list = ["correctness", "relevance", "hallucination", "pii"]

    for i in range(0, len(metrics_list), 2):
        col1, col2 = st.columns(2)

        m1 = metrics_list[i]
        if m1 in df_metrics:
            with col1:
                st.markdown(f"#### {m1}")
                st.bar_chart(df_metrics.set_index("dataset")[m1].dropna())

        if i + 1 < len(metrics_list):
            m2 = metrics_list[i + 1]
            if m2 in df_metrics:
                with col2:
                    st.markdown(f"#### {m2}")
                    st.bar_chart(df_metrics.set_index("dataset")[m2].dropna())

    st.markdown("---")

    # =====================================================
    # 📈 METRIC TRENDS
    # =====================================================
    st.markdown("### 📈 Metric Trends Over Time")

    if not timeline_df.empty:
        for i in range(0, len(metrics_list), 2):
            col1, col2 = st.columns(2)

            m1 = metrics_list[i]
            if m1 in timeline_df:
                with col1:
                    st.markdown(f"#### {m1}")
                    st.line_chart(timeline_df.set_index("time")[m1])

            if i + 1 < len(metrics_list):
                m2 = metrics_list[i + 1]
                if m2 in timeline_df:
                    with col2:
                        st.markdown(f"#### {m2}")
                        st.line_chart(timeline_df.set_index("time")[m2])

    st.markdown("---")

    # =====================================================
    # 📉 FAILURE TREND
    # =====================================================
    st.markdown("### 📉 Failures Over Time")

    if not timeline_df.empty:
        st.line_chart(timeline_df.set_index("time")["failures"])

    st.markdown("---")

    # =====================================================
    # 🔍 FILTER
    # =====================================================
    show_failed_only = st.checkbox("Show only failed datasets")

    st.markdown("### 📁 Datasets")

    for _, row in df_metrics.iterrows():

        data = load_eval(row["dataset"])
        df = pd.DataFrame(data["results"])

        # ---- detect human dataset ----
        is_human = "status" in df.columns

        # ---- failed logic ----
        is_failed = row["failed"]

        if show_failed_only and not is_failed:
            continue

        # ---- background styling ----
        bg = ""
        if is_failed:
            bg = "background-color: rgba(255,0,0,0.1); padding:10px; border-radius:8px;"

        st.markdown(f"<div style='{bg}'>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([5, 1, 1])

        # ---- tags ----
        type_tag = "🧑 HUMAN" if is_human else "🤖 LLM"
        status_tag = "🔴 FAILED" if is_failed else "🟢 OK"

        score_display = (
            f"{round(row['overall_score'],2)}"
            if row["overall_score"] is not None else "N/A"
        )

        col1.markdown(
            f"**{row['dataset']}** — {type_tag} — {status_tag} — Score: {score_display}"
        )

        # ---- view ----
        if col2.button("View", key=f"view_{row['dataset']}"):
            st.session_state["selected_dataset"] = row["dataset"]
            st.session_state["menu"] = "Dataset View"
            st.rerun()

        # ---- delete ----
        if col3.button("Delete", key=f"delete_{row['dataset']}"):
            os.remove(f"data/{row['dataset']}")
            st.success("Dataset deleted")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
# =========================================================
# ---------------- DATASET VIEW ----------------
# =========================================================
elif menu == "Dataset View":
    st.title("📄 Dataset Evaluation")

    if st.button("⬅ Back"):
        st.session_state["menu"] = "All Evaluations"
        st.rerun()

    data = load_eval(st.session_state["selected_dataset"])
    df = pd.DataFrame(data["results"])

    metric_cols = [c for c in ["correctness", "relevance", "hallucination", "pii"] if c in df.columns]

    # KPIs RESTORED
    if metric_cols:
        cols = st.columns(len(metric_cols))
        for i, m in enumerate(metric_cols):
            cols[i].metric(m.capitalize(), round(df[m].mean(), 2))

    # Failed queries KPI
    if "correctness" in df.columns and "relevance" in df.columns:
        failed = df[(df["correctness"] < 0.5) | (df["relevance"] < 0.5)]
        st.metric("❌ Failed Queries", len(failed))

    st.markdown("---")

    # BAR CHART RESTORED
    if metric_cols:
        summary = {m: df[m].mean() for m in metric_cols}
        st.bar_chart(pd.DataFrame.from_dict(summary, orient="index"))

    st.markdown("---")

    for i, row in df.iterrows():
        with st.expander(f"Query {i+1}"):

            st.write("Query:", row.get("query"))
            st.write("GT:", row.get("gt"))
            st.write("Output:", row.get("output"))

            for m in metric_cols:
                st.write(f"{m}:", row.get(m))

            st.write("Reasons:")
            st.write("Correctness:", row.get("correctness_reason"))
            st.write("Relevance:", row.get("relevance_reason"))
            st.write("Hallucination:", row.get("hallucination_reason"))
            st.write("PII:", row.get("pii_reason"))

# =========================================================
# ---------------- FAILED QUERIES ----------------
# =========================================================
elif menu == "Failed Queries":
    st.title("❌ Failed Queries")

    files = load_all()
    all_failed = []

    for f in files:
        data = load_eval(f)
        df = pd.DataFrame(data["results"])

        for _, row in df.iterrows():
            if row.get("correctness", 1) < 0.5 or row.get("relevance", 1) < 0.5:
                all_failed.append({
                    "dataset": f,
                    "query": row.get("query"),
                    "reason": row.get("correctness_reason")
                })

    if all_failed:
        for row in all_failed:
            with st.expander(f"❌ {row['dataset']}"):
                st.write("Query:", row["query"])
                st.write("Reason:", row["reason"])
    else:
        st.success("No failed queries 🎉")