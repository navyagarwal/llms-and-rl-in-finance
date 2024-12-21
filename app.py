import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import streamlit as st

def extract_category(text):
    if isinstance(text, str):
        match = re.search(r'(Neutral|Rise|Fall)', text, re.IGNORECASE)
        if match:
            return match.group(1).capitalize()
    return "Neutral"

st.title("LLMs for Finance: Report Generator")

tabs = st.tabs(["Single File Analysis", "Multiple File Comparison"])

with tabs[0]:
    st.header("Single File Analysis")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"], key="single_file")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Data")
        st.write(data.head())

        data['actual'] = data['answer'].apply(extract_category)
        data['predicted'] = data['untrained_prediction'].apply(extract_category)

        st.subheader("Processed Data with Extracted Categories")
        st.write(data[['answer', 'untrained_prediction', 'actual', 'predicted']].head())

        cm = confusion_matrix(data['actual'], data['predicted'], labels=['Neutral', 'Rise', 'Fall'])

        st.subheader("Confusion Matrix")
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Neutral', 'Rise', 'Fall'], yticklabels=['Neutral', 'Rise', 'Fall'])
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        st.pyplot(plt)

        report = classification_report(data['actual'], data['predicted'], target_names=['Neutral', 'Rise', 'Fall'], output_dict=True)

        st.subheader("Classification Report")
        st.write(pd.DataFrame(report).transpose())

with tabs[1]:
    st.header("Multiple File Comparison")

    uploaded_files = st.file_uploader("Upload multiple CSV files", type=["csv"], accept_multiple_files=True, key="multiple_files")

    if uploaded_files:
        comparison_data = []

        for uploaded_file in uploaded_files:
            data = pd.read_csv(uploaded_file)

            data['actual'] = data['answer'].apply(extract_category)
            data['predicted'] = data['untrained_prediction'].apply(extract_category)

            cm = confusion_matrix(data['actual'], data['predicted'], labels=['Neutral', 'Rise', 'Fall'])

            report = classification_report(data['actual'], data['predicted'], target_names=['Neutral', 'Rise', 'Fall'], output_dict=True)

            overall_accuracy = report.pop('accuracy')

            report_df = pd.DataFrame(report).transpose()

            report_df.loc['accuracy', ['precision', 'recall', 'f1-score']] = [None, None, overall_accuracy]

            comparison_data.append({
                'file_name': uploaded_file.name,
                'confusion_matrix': cm,
                'classification_report': report_df
            })

        st.markdown("<h2 style='text-align: center;'>Confusion Matrices</h2>", unsafe_allow_html=True)

        num_files = len(comparison_data)
        cols = st.columns(num_files)

        for idx, comparison in enumerate(comparison_data):
            with cols[idx]:
                st.write(f"**{comparison['file_name']}**")

                plt.figure(figsize=(5, 4))
                sns.heatmap(comparison['confusion_matrix'], annot=True, fmt='d', cmap='Blues',
                            xticklabels=['Neutral', 'Rise', 'Fall'], yticklabels=['Neutral', 'Rise', 'Fall'])
                plt.xlabel('Predicted')
                plt.ylabel('Actual')
                plt.title(f"Confusion Matrix - {comparison['file_name']}")
                st.pyplot(plt)


        st.markdown("<h2 style='text-align: center;'>Classification Reports</h2>", unsafe_allow_html=True)

        cols = st.columns(num_files)

        for idx, comparison in enumerate(comparison_data):
            with cols[idx]:
                st.write(f"**{comparison['file_name']}**")
                st.write(comparison['classification_report'])
