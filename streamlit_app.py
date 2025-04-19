
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="📥 Upload & Overview", layout="wide")
st.title("📥 Upload & Overview")

uploaded_file = st.file_uploader("Upload your survey CSV or Excel file", type=["csv", "xlsx"])

@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def detect_column_types(df):
    col_types = {
        "segments": [],
        "likert": [],
        "rating": [],
        "matrix": [],
        "mcq": [],
        "checkbox": [],
        "ranking": [],
        "semantic": [],
        "open_ended": []
    }
    for col in df.columns:
        cl = col.lower()
        if cl in ["age", "gender", "country"] or cl.startswith("segment_"):
            col_types["segments"].append(col)
        elif "likert" in cl:
            col_types["likert"].append(col)
        elif "rating" in cl or "nps" in cl:
            col_types["rating"].append(col)
        elif "matrix" in cl:
            col_types["matrix"].append(col)
        elif "mcq" in cl:
            col_types["mcq"].append(col)
        elif "checkbox" in cl:
            col_types["checkbox"].append(col)
        elif "rank" in cl:
            col_types["ranking"].append(col)
        elif "sd_" in cl:
            col_types["semantic"].append(col)
        elif "explain" in cl or "open_ended" in cl or "comment" in cl or "feedback" in cl:
            col_types["open_ended"].append(col)
    return col_types

def plot_average_bar(df, cols, title, segment=None):
    st.subheader(title)
    numeric_df = df[cols].apply(pd.to_numeric, errors='coerce')
    if segment:
        grouped = df[[segment]].join(numeric_df).groupby(segment).mean()
        fig, ax = plt.subplots(figsize=(10, 4))
        grouped.plot(kind='bar', ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f')
        ax.set_ylabel("Average Score")
        ax.set_title(f"{title} by {segment}")
    else:
        avg_scores = numeric_df.mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 4))
        avg_scores.plot(kind='bar', ax=ax)
        ax.bar_label(ax.containers[0], fmt='%.2f')
        ax.set_ylabel("Average Score")
        ax.set_title(title)
    st.pyplot(fig)

def plot_mcq_grouped_percent(df, mcq_cols, segment):
    st.subheader("Multiple Choice (Single Answer) – Grouped by Segment (%)")
    if segment:
        grouped = df.groupby(segment)[mcq_cols].apply(lambda x: x.notna().sum())
        total_per_group = df.groupby(segment).size()
        percent_df = grouped.div(total_per_group, axis=0) * 100
        fig, ax = plt.subplots(figsize=(10, 4))
        percent_df.plot(kind='bar', ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%')
        ax.set_ylabel("Percentage Selected")
        ax.set_title(f"MCQ Option Selection (% of group) by {segment}")
        st.pyplot(fig)
    else:
        total_counts = df[mcq_cols].notna().sum()
        total_respondents = len(df)
        percent = (total_counts / total_respondents) * 100
        fig, ax = plt.subplots(figsize=(8, 3))
        percent.plot(kind='bar', ax=ax)
        ax.bar_label(ax.containers[0], fmt='%.1f%%')
        ax.set_ylabel("Percentage Selected")
        ax.set_title("Total MCQ Selection % (All Respondents)")
        st.pyplot(fig)

def plot_ranking_avg(df, cols):
    st.subheader("📊 Average Rankings (Lower = Better)")
    numeric_df = df[cols].apply(pd.to_numeric, errors='coerce')
    avg_ranks = numeric_df.mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 4))
    avg_ranks.plot(kind='barh', ax=ax)
    ax.bar_label(ax.containers[0], fmt='%.2f')
    ax.set_xlabel("Average Rank")
    st.pyplot(fig)

def show_open_ended(df, cols):
    st.subheader("💬 Open-Ended Responses (Preview)")
    for col in cols:
        st.markdown(f"**{col}**")
        non_empty = df[col].dropna().astype(str)
        preview = non_empty[non_empty.str.strip() != ""].head(5)
        for i, text in enumerate(preview):
            st.markdown(f"- {text}")
        st.markdown("---")

if uploaded_file:
    df = load_data(uploaded_file)
    st.success("File uploaded successfully.")
    col_types = detect_column_types(df)

    segment = None
    if col_types["segments"]:
        segment = st.selectbox("Select a segment to group by:", ["(None)"] + col_types["segments"])
        if segment == "(None)":
            segment = None

    if col_types["likert"]:
        plot_average_bar(df, col_types["likert"], "Average Likert Scale Responses", segment)

    if col_types["rating"]:
        plot_average_bar(df, col_types["rating"], "Average Rating Scale Responses", segment)

    if col_types["matrix"]:
        plot_average_bar(df, col_types["matrix"], "Average Matrix Question Responses", segment)

    if col_types["mcq"]:
        mcq_prefixes = set("_".join(col.split("_")[:3]) for col in col_types["mcq"])
        for prefix in mcq_prefixes:
            mcq_group_cols = [col for col in col_types["mcq"] if col.startswith(prefix)]
            plot_mcq_grouped_percent(df, mcq_group_cols, segment)

    if col_types["ranking"]:
        plot_ranking_avg(df, col_types["ranking"])

    if col_types["open_ended"]:
        show_open_ended(df, col_types["open_ended"])

    st.subheader("Raw Data Preview")
    st.dataframe(df.head(20))
