import streamlit as st
import pandas as pd
import plotly.express as px
st. set_page_config(layout="wide") 

if st.session_state["predictions"] == None:
    st.header("Please run the pipeline first!")

elif st.session_state["predictions"] != None:
    # Load the CSV file
    file_path = st.session_state["predictions"]
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

    # Create a histogram and box plot for each column (except "peptide", "sequence_name", and "sample_name")
    st.subheader("Histograms and Box Plots")

    # Check if there are more than 1 different lengths in the "peptide" column
    unique_lengths = df["peptide"].str.len().nunique()

    if unique_lengths > 1:
        df["peptide_length"] = df["peptide"].str.len()
    else:
        df["peptide_length"] = 0

    # Create a checkbox for enabling/disabling the overlay for peptide lengths
    show_overlay_histograms_column = st.checkbox(f"Enable Overlay Histograms for Peptide Lengths")
    log_axes = st.checkbox(f"Enable logarithmic axis for relevant figures")

    num_plots_per_row = 2
    num_rows = (len(selected_columns) + num_plots_per_row - 1) // num_plots_per_row

    # Initialize the col1 and col2 variables
    col1, col2 = st.columns(num_plots_per_row)

    for i, column in enumerate(selected_columns):
        if column not in ["peptide", "sequence_name", "sample_name", "best_allele","n_flank", "c_flank"]:
            fig_histogram = px.histogram(
                df,
                x=column,
                color="peptide_length" if show_overlay_histograms_column else None,
                title=f"Distribution of {column}",
                labels={column: column, "peptide_length": "Peptide Length"},
                barmode="overlay" if show_overlay_histograms_column and unique_lengths > 1 else "relative",
                text_auto=True
            )
            fig_boxplot = px.box(df, y=column, title=f"Box Plot for {column}")
            fig_boxplot.update_layout(yaxis_type="log" if column in ["presentation_percentile", "affinity_percentile", "affinity","pos"] and log_axes else "linear")
            if i % num_plots_per_row == 0:
                col1, col2 = st.columns(num_plots_per_row)
            col1.plotly_chart(fig_histogram, use_container_width=True)
            col2.plotly_chart(fig_boxplot, use_container_width=True)

    # Add the histograms for "n_flank", "c_flank", and "best_allele" at the end
    order =['L','R','L']
    x=0
    for column in ["n_flank", "c_flank", "best_allele"]:
        fig_histogram = px.histogram(
            df,
            x=column,
            color="peptide_length" if show_overlay_histograms_column else None,
            title=f"Distribution of {column}",
            labels={column: column, "peptide_length": "Peptide Length"},
            barmode="overlay" if show_overlay_histograms_column and unique_lengths > 1 else "relative",
            text_auto=True
        )
        if order[x]=='L':
            col1.plotly_chart(fig_histogram, use_container_width=True)
        else:
            col2.plotly_chart(fig_histogram, use_container_width=True)
        x+=1

    st.subheader("Legend")
    st.caption("**Affinity (nM)**: *Lower values indicate stronger binders. Commonly-used threshold for peptides with a reasonable chance of being immunogenic is 500 nM.*")
    st.caption("**Affinity percentile**: *the percentile of the affinity prediction among a large number of random peptides tested on that allele (range 0 - 100). Lower is stronger. Two percent is a commonly-used threshold.*")
    st.caption("**Antigen processing and presentation scores**: *range from 0 to 1 with higher values indicating more favorable processing or presentation.*")