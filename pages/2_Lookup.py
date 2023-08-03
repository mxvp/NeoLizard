import streamlit as st
import pandas as pd
import plotly.express as px
st. set_page_config(layout="wide") 
if st.session_state["predictions"] == None:
    st.header("Please run the pipeline first!")

elif st.session_state["predictions"] != None:
# Load the CSV file
    file_path = st.session_state["predictions"]
    st.header("Sequence Lookup")
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
    sequences = df["sequence_name"]
    selected_sequence = st.selectbox("Select a sequence:", sequences)
    # Filter data for the selected sample
    sequence_data = df[df["sequence_name"] == selected_sequence][selected_columns]
    # Show data for the selected sample
    st.subheader(f"Data for {selected_sequence}")
    
    unique_lengths = df["peptide"].str.len().nunique()
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
    