import streamlit as st
import pandas as pd
import plotly.express as px
st. set_page_config(layout="wide") 
if st.session_state["predictions"] == None:
    st.header("Please run the pipeline first!")

elif st.session_state["predictions"] != None:
# Load the CSV file
    file_path = st.session_state["predictions"]
    st.header("SEQUENCE LOOKUP")
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
    
    amount = df["peptide"].count()
    for column in selected_columns:
        if column != "sequence_name":
            value = sequence_data[column].iloc[0]
            if amount > 1:
                if pd.api.types.is_numeric_dtype(df[column]) and column!="pos":
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
    

    st.subheader("Legend")
    st.caption("**Affinity (nM)**: *Lower values indicate stronger binders. Commonly-used threshold for peptides with a reasonable chance of being immunogenic is 500 nM.*")
    st.caption("**Affinity percentile**: *the percentile of the affinity prediction among a large number of random peptides tested on that allele (range 0 - 100). Lower is stronger. Two percent is a commonly-used threshold.*")
    st.caption("**Antigen processing and presentation scores**: *range from 0 to 1 with higher values indicating more favorable processing or presentation.*")