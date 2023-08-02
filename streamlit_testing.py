import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(layout="wide") 
st.sidebar.image('./resources/logo.png')


file_path = "/Users/mvp/Documents/biolizard/Project/NeoLizard/data/TCGA_prad/predictions.csv"
df = pd.read_csv(file_path)
selected_columns = [
    "sequence_name",
    "pos",
    "peptide",
    "n_flank",
    "c_flank",
    "affinity",
    "best_allele",
    "affinity_percentile",
    "processing_score",
    "presentation_score",
    "presentation_percentile",
]
# Filter the data to show only the selected columns
selected_data = df[selected_columns]
# Show the selected columns as a table
st.header("RESULTS")
st.subheader("Prediction Data")
st.dataframe(selected_data)

# Create a histogram for each column (except "peptide", "sequence_name", "sample_name")
st.subheader("Histograms")

# Check if there are more than 1 different lengths in the "peptide" column
unique_lengths = df["peptide"].str.len().nunique()

if unique_lengths > 1:
    df["peptide_length"] = df["peptide"].str.len()
else:
    df["peptide_length"] = 0

# Create a checkbox for enabling/disabling the overlay for peptide lengths
show_overlay_histograms_column = st.checkbox(f"Enable Overlay Histograms for Peptide Lengths")
for i, column in enumerate(selected_columns):
    if column not in ["peptide", "sequence_name", "sample_name"]:
        fig = px.histogram(
            df,
            x=column,
            color="peptide_length" if show_overlay_histograms_column else None,
            title=f"Distribution of {column}",
            labels={column: column, "peptide_length": "Peptide Length"},
            barmode="overlay" if show_overlay_histograms_column and unique_lengths > 1 else "relative",
            text_auto=True
        )
        st.plotly_chart(fig)

# Add interactive elements
st.subheader("Sequence Lookup")
sequences = df["sequence_name"]
selected_sequence = st.selectbox("Select a sequence:", sequences)
# Filter data for the selected sample
sequence_data = df[df["sequence_name"] == selected_sequence][selected_columns]
# Show data for the selected sample
st.subheader(f"Data for {selected_sequence}")

for column in selected_columns:
    if column != "sequence_name":
        value = sequence_data[column].iloc[0]
        if unique_lengths > 1:
            if pd.api.types.is_numeric_dtype(df[column]):
                average = df[column].mean()
                percentage_difference = (value - average) / average * 100
                if percentage_difference > 0:
                    st.write(f"{column}: {value} ({abs(percentage_difference):.2f}% {':red[above]' if 'percentile' in column else ' :green[above]'} average)")
                else:
                    st.write(f"{column}: {value} ({abs(percentage_difference):.2f}% {':green[below]' if 'percentile' in column else ' :red[below]'} average)")
            else:
                st.write(f"{column}: {value}")
        else:
            st.write(f"{column}: {value}")
