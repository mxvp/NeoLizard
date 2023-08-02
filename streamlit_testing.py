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
file_path = "/Users/mvp/Documents/biolizard/Project/NeoLizard/data/TCGA_prad/predictions.csv"  
df = pd.read_csv(file_path)

selected_columns =['sequence_name','pos','peptide','n_flank','c_flank','affinity','best_allele','affinity_percentile','processing_score','presentation_score','presentation_percentile']

# Filter the data to show only the selected columns
selected_data = df[selected_columns]

# Show the selected columns as a table
st.subheader("Prediction Data")
st.dataframe(selected_data)

# Plot the selected columns
st.subheader("Plots")
for column in selected_columns:
    if column not in ["peptide","sequence_name","sample_name"]:  
        fig = px.histogram(df, x=column, title=f"Distribution of {column}")
        st.plotly_chart(fig)


# Add interactive elements
st.subheader("Sequence Lookup")
sequences = df["sequence_name"]
selected_sequence = st.selectbox("Select a sequence:", sequences)

# Filter data for the selected sample
sequence_data = df[df["sequence_name"] == selected_sequence][selected_columns]

# Show data for the selected sample
st.subheader(f"Data for {selected_sequence}")
st.dataframe(sequence_data)
