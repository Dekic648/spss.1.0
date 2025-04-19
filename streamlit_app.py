
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
        if col.lower() in ["age", "gender", "country"]:
            col_types["segments"].append(col)
        elif "likert" in col.lower():
            col_types["likert"].append(col)
        elif "rating" in col.lower() or "nps" in col.lower():
            col_types["rating"].append(col)
        elif "matrix" in col.lower():
            col_types["matrix"].append(col)
        elif "mcq" in col.lower():
            col_types["mcq"].append(col)
        elif "checkbox" in col.lower():
            col_types["checkbox"].append(col)
        elif "rank" in col.lower():
            col_types["ranking"].append(col)
        elif "sd_" in col.lower():
            col_types["semantic"].append(col)
        elif "explain" in col.lower() or "open_ended" in col.lower():
            col_types["open_ended"].append(col)
    return col_types

def plot_average_bar(df, cols, title, segment=None):
    st.subheader(title)
    if segment:
        grouped = df.groupby(segment)[cols].mean()
        fig, ax = plt.subplots(figsize=(10, 4))
        grouped.plot(kind='bar', ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f')
        ax.set_ylabel("Average Score")
        ax.set_title(f"{title} by {segment}")
    else:
        avg_scores = df[cols].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 4))
        avg_scores.plot(kind='bar', ax=ax)
        ax.bar_label(ax.containers[0], fmt='%.2f')
        ax.set_ylabel("Average Score")
        ax.set_title(title)
    st.pyplot(fig)

def plot_mcq_grouped(df, mcq_cols, segment):
    st.subheader("Multiple Choice (Single Answer) - Grouped Counts")
    if segment:
        grouped = df.groupby(segment)[mcq_cols].apply(lambda x: x.notna().sum())
        fig, ax = plt.subplots(figsize=(10, 4))
        grouped.unstack().plot(kind='bar', ax=ax)
        for container in ax.containers:
            ax.bar_label(container)
        ax.set_ylabel("Count")
        ax.set_title(f"MCQ Selections by {segment}")
        st.pyplot(fig)
    else:
        total_counts = df[mcq_cols].notna().sum()
        fig, ax = plt.subplots(figsize=(8, 3))
        total_counts.plot(kind='bar', ax=ax)
        ax.bar_label(ax.containers[0])
        ax.set_ylabel("Selections")
        ax.set_title("Total MCQ Selections")
        st.pyplot(fig)

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
            plot_mcq_grouped(df, mcq_group_cols, segment)

    st.subheader("Raw Data Preview")
    st.dataframe(df.head(20))
