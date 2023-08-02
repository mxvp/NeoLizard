import streamlit as st
import os
import logging
from lib.logger_config import configure_lib_logger, configure_logger
from lib.path_handler import PathHandler
from lib.cmd_runner import CommandRunner
from lib.qc import QCPipeline
from lib.m2a import MAFtoAVInputConverter
from lib.annovar_functions import AnnovarPipeline
from lib.cropping_flanks import CroppingFlanksPipeline
from lib.MHCflurry_prediction import MHCflurryPipeline
from lib.lizard import print_lizard
from lib.cutadapt import CutadaptPipeline
from lib.data_gathering import PipelineData
from lib.HLA import HLAPipeline
from lib.database_operations import DatabaseOperations
from contextlib import contextmanager
from io import StringIO
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


if st.session_state['predictions']!=None:
    # Load the CSV file
    file_path = st.session_state['predictions']
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