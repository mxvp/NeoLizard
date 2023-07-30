import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
import plotly.express as px


import pandas as pd
import streamlit as st
import plotly.express as px

# Load the CSV file
file_path = "/home/mxvp/Documents/NeoLizard/testing_area/output2/predictions.csv"  # Replace with the actual path to your CSV file
df = pd.read_csv(file_path)

# Sidebar to select the columns to display
st.sidebar.title("Select Columns")
selected_columns = st.sidebar.multiselect(
    "Choose columns to display:",
    df.columns.tolist(),
    default=['sequence_name','pos','peptide','n_flank','c_flank','sample_name','affinity','best_allele','affinity_percentile','processing_score','presentation_score','presentation_percentile'],
)

# Filter the data to show only the selected columns
selected_data = df[selected_columns]

# Show the selected columns as a table
st.subheader("Selected Data")
st.dataframe(selected_data)

# Plot the selected columns
st.subheader("Plots")
for column in selected_columns:
    if column != "peptide":  # Exclude non-numeric columns from plotting
        fig = px.histogram(df, x=column, nbins=20, title=f"Distribution of {column}")
        st.plotly_chart(fig)

# Add interactive elements
st.sidebar.title("Interactive Elements")
peptides = df["peptide"]
selected_peptide = st.sidebar.selectbox("Select a peptide:", peptides)

# Filter data for the selected sample
peptide_data = df[df["peptide"] == selected_peptide][selected_columns]

# Show data for the selected sample
st.subheader(f"Data for {selected_peptide}")
st.dataframe(peptide_data)


# Show a pie chart for the selected peptide
pie_column = st.sidebar.selectbox("Select a column for pie chart:", selected_columns)
if pie_column != "sample_name" and pie_column != selected_peptide:
    pie_fig = px.pie(df, names=pie_column, title=f"Pie Chart for {pie_column}")
    st.plotly_chart(pie_fig)

# Show a scatter plot for the selected sample
scatter_columns = st.sidebar.selectbox("Select columns for scatter plot:", selected_columns)
if scatter_columns != "sample_name" and scatter_columns != selected_peptide:
    scatter_fig = px.scatter(df, x=scatter_columns, y=scatter_columns, title=f"{scatter_columns} vs {selected_peptide}")
    st.plotly_chart(scatter_fig)
