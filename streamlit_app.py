
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
        "radio": [],
        "checkbox": [],
        "ranking": [],
        "semantic": [],
        "open_ended": []
    }
    for col in df.columns:
        cl = col.lower()
        if "segment_" in cl:
            col_types["segments"].append(col)
        elif "likert_" in cl:
            col_types["likert"].append(col)
        elif "rating_" in cl or "nps_" in cl:
            col_types["rating"].append(col)
        elif "matrix_" in cl:
            col_types["matrix"].append(col)
        elif "rb_" in cl:
            col_types["radio"].append(col)
        elif "checkbox_" in cl:
            col_types["checkbox"].append(col)
        elif "rank_" in cl:
            col_types["ranking"].append(col)
        elif "sd_" in cl:
            col_types["semantic"].append(col)
        elif "open_ended_" in cl or "comment_" in cl or "feedback_" in cl:
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

def plot_grouped_checkbox(df, cols, segment):
    group_key = "_".join(cols[0].split("_")[:3])
    st.subheader(f"Checkbox – {group_key} (%)")
    if segment:
        grouped = df.groupby(segment)[cols].apply(lambda x: x.notna().sum())
        total_per_group = df.groupby(segment).size()
        percent_df = grouped.div(total_per_group, axis=0) * 100
        fig, ax = plt.subplots(figsize=(10, 4))
        percent_df.plot(kind='bar', ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%')
        ax.set_ylabel("Percentage Selected")
        ax.set_title(f"{group_key} – % of respondents per group")
        st.pyplot(fig)
    else:
        total_counts = df[cols].notna().sum()
        percent = (total_counts / len(df)) * 100
        fig, ax = plt.subplots(figsize=(8, 3))
        percent.plot(kind='bar', ax=ax)
        ax.bar_label(ax.containers[0], fmt='%.1f%%')
        ax.set_ylabel("Percentage Selected")
        ax.set_title(f"{group_key} – Overall Selection %")
        st.pyplot(fig)

def plot_grouped_radio(df, cols, segment):
    group_key = "_".join(cols[0].split("_")[:2])
    st.subheader(f"Radio Button – {group_key} (%)")
    if segment:
        grouped = df.groupby(segment)[cols].apply(lambda x: x.notna().sum())
        total_per_group = df.groupby(segment).size()
        percent_df = grouped.div(total_per_group, axis=0) * 100
        fig, ax = plt.subplots(figsize=(10, 4))
        percent_df.plot(kind='bar', ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%')
        ax.set_ylabel("Percentage Selected")
        ax.set_title(f"{group_key} – Radio Button Selection by Segment")
        st.pyplot(fig)
    else:
        total_counts = df[cols].notna().sum()
        percent = (total_counts / len(df)) * 100
        fig, ax = plt.subplots(figsize=(8, 3))
        percent.plot(kind='bar', ax=ax)
        ax.bar_label(ax.containers[0], fmt='%.1f%%')
        ax.set_ylabel("Percentage Selected")
        ax.set_title(f"{group_key} – Radio Button Overall %")
        st.pyplot(fig)

def plot_ranking(df, cols):
    st.subheader("📊 Ranking – Average Rank (Lower = Better)")
    numeric_df = df[cols].apply(pd.to_numeric, errors='coerce')
    avg_ranks = numeric_df.mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 4))
    avg_ranks.plot(kind='barh', ax=ax)
    ax.bar_label(ax.containers[0], fmt='%.2f')
    ax.set_xlabel("Average Rank")
    st.pyplot(fig)

def show_open_ended(df, cols):
    st.subheader("💬 Open-Ended Response Preview")
    for col in cols:
        st.markdown(f"**{col}**")
        responses = df[col].dropna().astype(str)
        for text in responses[responses.str.strip() != ""].head(5):
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
        plot_average_bar(df, col_types["likert"], "Likert Scale Responses", segment)

    if col_types["rating"]:
        plot_average_bar(df, col_types["rating"], "Rating Scale Responses", segment)

    if col_types["matrix"]:
        plot_average_bar(df, col_types["matrix"], "Matrix Question Responses", segment)

    if col_types["ranking"]:
        plot_ranking(df, col_types["ranking"])

    if col_types["semantic"]:
        plot_average_bar(df, col_types["semantic"], "Semantic Differential Averages", segment)

    if col_types["radio"]:
        prefixes = set("_".join(col.split("_")[:2]) for col in col_types["radio"])
        for prefix in prefixes:
            group = [col for col in col_types["radio"] if col.startswith(prefix)]
            plot_grouped_radio(df, group, segment)

    if col_types["checkbox"]:
        prefixes = set("_".join(col.split("_")[:3]) for col in col_types["checkbox"])
        for prefix in prefixes:
            group = [col for col in col_types["checkbox"] if col.startswith(prefix)]
            plot_grouped_checkbox(df, group, segment)

    if col_types["open_ended"]:
        show_open_ended(df, col_types["open_ended"])

    st.subheader("📋 Raw Data Preview")
    st.dataframe(df.head(20))
