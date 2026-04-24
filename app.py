
# # import streamlit as st
# # import pandas as pd
# # import os

# # from core.agent import agent_run
# # from core.evaluator import evaluate
# # from storage.file_store import save_eval, load_all, load_eval

# # st.set_page_config(layout="wide")

# # # ---------------- NAV STATE ----------------
# # pages = ["Upload", "All Evaluations", "Dataset View"]

# # if "menu" not in st.session_state:
# #     st.session_state["menu"] = "Upload"

# # if "selected_dataset" not in st.session_state:
# #     st.session_state["selected_dataset"] = None

# # menu = st.sidebar.radio(
# #     "Navigation",
# #     pages,
# #     index=pages.index(st.session_state["menu"])
# # )

# # if menu != st.session_state["menu"]:
# #     st.session_state["menu"] = menu

# # # =========================================================
# # # ---------------- UPLOAD ----------------
# # # =========================================================
# # if menu == "Upload":
# #     st.title("🚀 LLM Evaluator")

# #     uploaded = st.file_uploader("Upload CSV (input, ground_truth)", type=["csv"])
# #     human_mode = st.checkbox("Human Review Mode")

# #     if uploaded:
# #         df = pd.read_csv(uploaded)
# #         st.subheader("Preview")
# #         st.dataframe(df)

# #         if st.button("Run Evaluation"):
# #             results = []
# #             progress = st.progress(0)

# #             for i, row in df.iterrows():
# #                 query = row["input"]
# #                 gt = row["ground_truth"]

# #                 agent_output = agent_run(query)

# #                 if "error" in agent_output:
# #                     final_answer = agent_output["error"]
# #                     sql = ""
# #                     raw_result = ""
# #                 else:
# #                     final_answer = agent_output.get("final_answer", "")
# #                     sql = agent_output.get("sql", "")
# #                     raw_result = agent_output.get("raw_result", "")

# #                 if human_mode:
# #                     results.append({
# #                         "query": query,
# #                         "gt": gt,
# #                         "sql": sql,
# #                         "raw_result": str(raw_result),
# #                         "output": final_answer,
# #                         "status": "pending_human"
# #                     })
# #                 else:
# #                     scores = evaluate(query, gt, final_answer)

# #                     results.append({
# #                         "query": query,
# #                         "gt": gt,
# #                         "sql": sql,
# #                         "raw_result": str(raw_result),
# #                         "output": final_answer,
# #                         **scores
# #                     })

# #                 progress.progress((i + 1) / len(df))

# #             eid = save_eval(results)
# #             st.success(f"Saved dataset: {eid}")

# # # =========================================================
# # # ---------------- ALL EVALUATIONS ----------------
# # # =========================================================
# # elif menu == "All Evaluations":
# #     st.title("📊 Evaluation Dashboard")

# #     files = load_all()

# #     dataset_metrics = []
# #     timeline = []

# #     for f in files:
# #         data = load_eval(f)
# #         df = pd.DataFrame(data["results"])

# #         is_human = "status" in df.columns

# #         metrics = {
# #             "dataset": f,
# #             "type": "🧑 Human" if is_human else "🤖 LLM",
# #             "timestamp": data["timestamp"]
# #         }

# #         for col in ["correctness", "relevance", "hallucination", "pii"]:
# #             metrics[col] = df[col].mean() if col in df else None

# #         dataset_metrics.append(metrics)

# #         if data["timestamp"]:
# #             timeline.append(metrics)

# #     df_metrics = pd.DataFrame(dataset_metrics)

# #     # -------- KPIs --------
# #     st.subheader("🚀 Global KPIs")

# #     def safe_mean(col):
# #         return round(df_metrics[col].dropna().mean(), 2) if col in df_metrics else 0

# #     cols = st.columns(4)
# #     cols[0].metric("Correctness", safe_mean("correctness"))
# #     cols[1].metric("Relevance", safe_mean("relevance"))
# #     cols[2].metric("Hallucination", safe_mean("hallucination"))
# #     cols[3].metric("PII", safe_mean("pii"))

# #     st.markdown("---")

# #     # -------- BAR CHARTS --------
# #     st.markdown("### 📊 Dataset Comparison")

# #     metrics_list = ["correctness", "relevance", "hallucination", "pii"]

# #     for i in range(0, len(metrics_list), 2):
# #         col1, col2 = st.columns(2)

# #         m1 = metrics_list[i]
# #         if m1 in df_metrics:
# #             with col1:
# #                 st.markdown(f"#### {m1.capitalize()}")
# #                 st.bar_chart(df_metrics.set_index("dataset")[m1].dropna())

# #         if i + 1 < len(metrics_list):
# #             m2 = metrics_list[i + 1]
# #             if m2 in df_metrics:
# #                 with col2:
# #                     st.markdown(f"#### {m2.capitalize()}")
# #                     st.bar_chart(df_metrics.set_index("dataset")[m2].dropna())

# #     st.markdown("---")

# #     # -------- LINE CHARTS --------
# #     st.markdown("### 📈 Trends Over Time")

# #     if timeline:
# #         tdf = pd.DataFrame(timeline)
# #         tdf["time"] = pd.to_datetime(tdf["timestamp"], unit="s")
# #         tdf = tdf.sort_values("time")

# #         for i in range(0, len(metrics_list), 2):
# #             col1, col2 = st.columns(2)

# #             m1 = metrics_list[i]
# #             if m1 in tdf:
# #                 with col1:
# #                     st.markdown(f"#### {m1.capitalize()} Trend")
# #                     st.line_chart(tdf.set_index("time")[m1])

# #             if i + 1 < len(metrics_list):
# #                 m2 = metrics_list[i + 1]
# #                 if m2 in tdf:
# #                     with col2:
# #                         st.markdown(f"#### {m2.capitalize()} Trend")
# #                         st.line_chart(tdf.set_index("time")[m2])

# #     st.markdown("---")

# #     # -------- DATASETS --------
# #     st.markdown("### 📁 Datasets")

# #     for _, row in df_metrics.iterrows():
# #         col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

# #         col1.markdown(f"**{row['dataset']}**  \n{row['type']}")

# #         if col2.button("View", key=f"v_{row['dataset']}"):
# #             st.session_state["selected_dataset"] = row["dataset"]
# #             st.session_state["menu"] = "Dataset View"
# #             st.rerun()

# #         if col3.button("Delete", key=f"d_{row['dataset']}"):
# #             os.remove(f"data/{row['dataset']}")
# #             st.rerun()

# #         col4.metric("Score", row["correctness"] if row["correctness"] else 0)

# # # =========================================================
# # # ---------------- DATASET VIEW ----------------
# # # =========================================================
# # elif menu == "Dataset View":
# #     st.title("📄 Dataset Evaluation")

# #     if st.button("⬅ Back"):
# #         st.session_state["menu"] = "All Evaluations"
# #         st.rerun()

# #     selected = st.session_state["selected_dataset"]

# #     if not selected:
# #         st.warning("Select dataset")
# #     else:
# #         data = load_eval(selected)
# #         df = pd.DataFrame(data["results"])

# #         st.subheader(selected)

# #         metrics_list = ["correctness", "relevance", "hallucination", "pii"]

# #         # KPIs
# #         cols = st.columns(4)
# #         for i, m in enumerate(metrics_list):
# #             if m in df:
# #                 cols[i].metric(m.capitalize(), round(df[m].mean(), 2))

# #         st.markdown("---")

# #         # -------- GROUPED BAR --------
# #         st.markdown("### 📊 Overall Metrics")

# #         summary = {m: df[m].mean() for m in metrics_list if m in df}
# #         summary_df = pd.DataFrame.from_dict(summary, orient="index", columns=["score"])

# #         st.bar_chart(summary_df)

# #         st.markdown("---")

# #         # -------- LIST VIEW --------
# #         st.markdown("### 📋 Detailed Results")

# #         for i, row in df.iterrows():
# #             expanded = row.get("correctness", 1) == 0

# #             with st.expander(f"🔎 Query {i+1}", expanded=expanded):

# #                 st.markdown(f"**🧾 Query:**  \n{row.get('query', '')}")
# #                 st.markdown(f"**📌 Ground Truth:**  \n{row.get('gt', '')}")
# #                 st.markdown(f"**🤖 Model Output:**  \n{row.get('output', '')}")

# #                 if "sql" in row:
# #                     st.markdown(f"**🗄️ SQL:**  \n`{row.get('sql', '')}`")

# #                 if "raw_result" in row:
# #                     st.markdown(f"**📊 Raw Result:**  \n{row.get('raw_result', '')}")

# #                 st.markdown("---")

# #                 cols = st.columns(4)

# #                 def icon(v):
# #                     return "🟢" if v == 1 else "🔴"

# #                 metrics = {
# #                     "Correctness": row.get("correctness"),
# #                     "Relevance": row.get("relevance"),
# #                     "Hallucination": row.get("hallucination"),
# #                     "PII": row.get("pii")
# #                 }

# #                 for idx, (k, v) in enumerate(metrics.items()):
# #                     if v is not None:
# #                         cols[idx].metric(k, f"{icon(v)} {v}")

# #                 if "correctness_reason" in row:
# #                     st.markdown(f"**🧠 Reason:** {row['correctness_reason']}")

# import streamlit as st
# import pandas as pd
# import os

# from core.agent import agent_run
# from core.evaluator import evaluate
# from storage.file_store import save_eval, load_all, load_eval

# st.set_page_config(layout="wide")

# # ---------------- NAV STATE ----------------
# pages = ["Upload", "All Evaluations", "Dataset View"]

# if "menu" not in st.session_state:
#     st.session_state["menu"] = "Upload"

# if "selected_dataset" not in st.session_state:
#     st.session_state["selected_dataset"] = None

# menu = st.sidebar.radio(
#     "Navigation",
#     pages,
#     index=pages.index(st.session_state["menu"])
# )

# if menu != st.session_state["menu"]:
#     st.session_state["menu"] = menu

# # =========================================================
# # ---------------- UPLOAD ----------------
# # =========================================================
# if menu == "Upload":
#     st.title("🚀 LLM Evaluator")

#     uploaded = st.file_uploader("Upload CSV (input, ground_truth)", type=["csv"])
#     human_mode = st.checkbox("Human Review Mode")

#     if uploaded:
#         df = pd.read_csv(uploaded)
#         st.subheader("Preview")
#         st.dataframe(df)

#         if st.button("Run Evaluation"):
#             results = []
#             progress = st.progress(0)

#             for i, row in df.iterrows():
#                 query = row["input"]
#                 gt = row["ground_truth"]

#                 agent_output = agent_run(query)

#                 if "error" in agent_output:
#                     final_answer = agent_output["error"]
#                     sql = ""
#                     raw_result = ""
#                 else:
#                     final_answer = agent_output.get("final_answer", "")
#                     sql = agent_output.get("sql", "")
#                     raw_result = agent_output.get("raw_result", "")

#                 if human_mode:
#                     results.append({
#                         "query": query,
#                         "gt": gt,
#                         "sql": sql,
#                         "raw_result": str(raw_result),
#                         "output": final_answer,
#                         "status": "pending_human"
#                     })
#                 else:
#                     scores = evaluate(query, gt, final_answer)

#                     results.append({
#                         "query": query,
#                         "gt": gt,
#                         "sql": sql,
#                         "raw_result": str(raw_result),
#                         "output": final_answer,
#                         **scores
#                     })

#                 progress.progress((i + 1) / len(df))

#             eid = save_eval(results)
#             st.success(f"Saved dataset: {eid}")

# # =========================================================
# # ---------------- ALL EVALUATIONS ----------------
# # =========================================================
# elif menu == "All Evaluations":
#     st.title("📊 Evaluation Dashboard")

#     files = load_all()

#     dataset_metrics = []
#     timeline = []

#     for f in files:
#         data = load_eval(f)
#         df = pd.DataFrame(data["results"])

#         is_human = "status" in df.columns

#         metrics = {
#             "dataset": f,
#             "type": "🧑 Human" if is_human else "🤖 LLM",
#             "timestamp": data["timestamp"]
#         }

#         for col in ["correctness", "relevance", "hallucination", "pii"]:
#             metrics[col] = df[col].mean() if col in df else None

#         dataset_metrics.append(metrics)

#         if data["timestamp"]:
#             timeline.append(metrics)

#     df_metrics = pd.DataFrame(dataset_metrics)

#     st.subheader("🚀 Global KPIs")

#     def safe_mean(col):
#         return round(df_metrics[col].dropna().mean(), 2) if col in df_metrics else 0

#     cols = st.columns(4)
#     cols[0].metric("Correctness", safe_mean("correctness"))
#     cols[1].metric("Relevance", safe_mean("relevance"))
#     cols[2].metric("Hallucination", safe_mean("hallucination"))
#     cols[3].metric("PII", safe_mean("pii"))

#     st.markdown("---")

#     st.markdown("### 📊 Dataset Comparison")

#     metrics_list = ["correctness", "relevance", "hallucination", "pii"]

#     for i in range(0, len(metrics_list), 2):
#         col1, col2 = st.columns(2)

#         m1 = metrics_list[i]
#         if m1 in df_metrics:
#             with col1:
#                 st.bar_chart(df_metrics.set_index("dataset")[m1].dropna())

#         if i + 1 < len(metrics_list):
#             m2 = metrics_list[i + 1]
#             if m2 in df_metrics:
#                 with col2:
#                     st.bar_chart(df_metrics.set_index("dataset")[m2].dropna())

#     st.markdown("---")

#     st.markdown("### 📁 Datasets")

#     for _, row in df_metrics.iterrows():
#         col1, col2, col3 = st.columns([5, 1, 1])

#         col1.markdown(f"**{row['dataset']}** ({row['type']})")

#         if col2.button("View", key=f"v_{row['dataset']}"):
#             st.session_state["selected_dataset"] = row["dataset"]
#             st.session_state["menu"] = "Dataset View"
#             st.rerun()

#         if col3.button("Delete", key=f"d_{row['dataset']}"):
#             os.remove(f"data/{row['dataset']}")
#             st.rerun()

# # =========================================================
# # ---------------- DATASET VIEW ----------------
# # =========================================================
# elif menu == "Dataset View":
#     st.title("📄 Dataset Evaluation")

#     if st.button("⬅ Back"):
#         st.session_state["menu"] = "All Evaluations"
#         st.rerun()

#     selected = st.session_state["selected_dataset"]

#     if not selected:
#         st.warning("Select dataset")
#     else:
#         data = load_eval(selected)
#         df = pd.DataFrame(data["results"])

#         st.subheader(selected)

#         metrics_list = ["correctness", "relevance", "hallucination", "pii"]

#         # KPIs
#         cols = st.columns(4)
#         for i, m in enumerate(metrics_list):
#             if m in df:
#                 cols[i].metric(m.capitalize(), round(df[m].mean(), 2))

#         st.markdown("---")

#         # GROUPED BAR
#         summary = {m: df[m].mean() for m in metrics_list if m in df}
#         st.bar_chart(pd.DataFrame.from_dict(summary, orient="index"))

#         st.markdown("---")

#         # LIST VIEW
#         st.markdown("### 📋 Detailed Results")

#         for i, row in df.iterrows():
#             expanded = row.get("correctness", 1) == 0

#             with st.expander(f"🔎 Query {i+1}", expanded=expanded):

#                 st.markdown(f"**🧾 Query:** {row.get('query', '')}")
#                 st.markdown(f"**📌 Ground Truth:** {row.get('gt', '')}")
#                 st.markdown(f"**🤖 Output:** {row.get('output', '')}")

#                 st.markdown("---")

#                 cols = st.columns(4)
#                 metrics = ["correctness", "relevance", "hallucination", "pii"]

#                 for idx, m in enumerate(metrics):
#                     val = row.get(m)
#                     if val is not None:
#                         icon = "🟢" if val == 1 else "🔴"
#                         cols[idx].metric(m.capitalize(), f"{icon} {val}")

#                 # 🔥 SHOW ALL REASONS
#                 st.markdown("### 🧠 Evaluation Reasons")

#                 if row.get("correctness_reason"):
#                     st.markdown(f"**Correctness:** {row['correctness_reason']}")

#                 if row.get("relevance_reason"):
#                     st.markdown(f"**Relevance:** {row['relevance_reason']}")

#                 if row.get("hallucination_reason"):
#                     st.markdown(f"**Hallucination:** {row['hallucination_reason']}")

#                 if row.get("pii_reason"):
#                     st.markdown(f"**PII:** {row['pii_reason']}")

#         # =========================================================
#         # 🔥 FAILURE ANALYTICS
#         # =========================================================

#         st.markdown("---")
#         st.markdown("## 🔍 Failure Insights")

#         failure_data = []

#         for _, row in df.iterrows():
#             for metric in ["correctness", "relevance", "hallucination", "pii"]:
#                 score = row.get(metric)

#                 if score == 0 or (metric == "hallucination" and score == 1):
#                     failure_data.append({
#                         "metric": metric,
#                         "reason": row.get(f"{metric}_reason", "unknown"),
#                         "query": row.get("query", "")
#                     })

#         if failure_data:
#             fdf = pd.DataFrame(failure_data)

#             st.markdown("### 📊 Failures by Metric")
#             st.bar_chart(fdf["metric"].value_counts())

#             st.markdown("### 🧠 Top Failure Reasons")
#             st.bar_chart(fdf["reason"].value_counts().head(10))

#             st.markdown("### 🔎 Sample Failures")

#             for _, row in fdf.head(5).iterrows():
#                 with st.expander(f"❌ {row['metric']} issue"):
#                     st.write(f"**Query:** {row['query']}")
#                     st.write(f"**Reason:** {row['reason']}")

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
            st.success(f"Saved dataset: {eid}")

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