# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 08:53:45 2024

@author: Safin.Lin
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io




def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df


def extract_station_number(file_name):
    station_number = file_name.split('_')[1]
    return station_number

def set_up_template_dataframe():
    date_range = pd.date_range(start="1800-01-01", end=pd.Timestamp.today(), freq='D').date
    df = pd.DataFrame(date_range, columns=['Date'])
    return df


def drop_columns(columns_name_list, df):
    df.drop(columns=columns_name_list, inplace=True)
    return df


def read_column_name(df):
    column_name = df.columns.tolist()
    return column_name

def turn_into_date(df):
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']]).dt.date
    
    # Move to the fourth column
    cols = list(df.columns)
    cols.insert(3, cols.pop(cols.index('Date')))
    df = df[cols]
    
    return df


def rename_column(df, rename_dict):
    df.rename(columns=rename_dict, inplace=True)
    

def drop_nan_row(df, column_list):
    df.dropna(subset=column_list, inplace=True)
    

def cumulative_column(df, column_str):
    column_name = 'Cumulative ' + column_str
    df[column_name] = df[column_str].cumsum()
    

def regression(df, x_column, y_column):
    slope, intercept = np.polyfit(df[x_column], df[y_column], 1)
    
    regression_line = slope * df[x_column] + intercept
    
    return slope, intercept, regression_line

# Initialize a set to keep track of uploaded filenames
uploaded_files = set()

st.title("""
Double Mass Curve App
#### Will plot the double mass curve and provide coefficient for you

""")

# File uploader
uploaded_file_1 = st.file_uploader("Upload first CSV file", type=["csv"])
uploaded_file_2 = st.file_uploader("Upload second CSV file", type=["csv"])

# Handle uploaded files
if uploaded_file_1 is not None:
    # Check for duplicates
    if uploaded_file_1.name in uploaded_files:
        st.warning(f"The file '{uploaded_file_1.name}' has already been uploaded.")
    else:
        uploaded_files.add(uploaded_file_1.name)
        df_1 = pd.read_csv(uploaded_file_1)
        st.write("First file uploaded successfully.")

if uploaded_file_2 is not None:
    # Check for duplicates
    if uploaded_file_2.name in uploaded_files:
        st.warning(f"The file '{uploaded_file_2.name}' has already been uploaded.")
    else:
        uploaded_files.add(uploaded_file_2.name)
        df_2 = pd.read_csv(uploaded_file_2)
        st.write("Second file uploaded successfully.")


if 'df_1' in locals() and 'df_2' in locals():
    station_1 = extract_station_number(uploaded_file_1.name)
    station_2 = extract_station_number(uploaded_file_2.name)

    # Read column names
    column_name_1 = read_column_name(df_1)
    column_name_2 = read_column_name(df_2)

    # Drop Useless column
    drop_columns([column_name_1[i] for i in [0, 1, 6, 7]], df_1)
    drop_columns([column_name_2[i] for i in [0, 1, 6, 7]], df_2)

    # Rename the column
    rename_1 = {'Rainfall amount (millimetres)': station_1}
    rename_2 = {'Rainfall amount (millimetres)': station_2}
    rename_column(df_1, rename_1)
    rename_column(df_2, rename_2)

    # Add Date Column
    df_1 = turn_into_date(df_1)
    df_2 = turn_into_date(df_2)

    # Combine two stations
    df_combined = df_1.merge(df_2[['Date', station_2]], how='inner', on=['Date'])

    # Drop year, month, day
    drop_list = ['Year', 'Day', 'Month']
    drop_columns(drop_list, df_combined)

    # Drop rows when there is NAN
    check_column = [station_1, station_2]
    drop_nan_row(df_combined, check_column)

    # Calculate Cumulative
    cumulative_column(df_combined, station_1)
    cumulative_column(df_combined, station_2)

    # Regression
    x_col = 'Cumulative ' + station_1
    y_col = 'Cumulative ' + station_2
    slope, intercept, regression_line = regression(df_combined, x_col, y_col)

    # ----------- Plot ---------- #
    plt.figure(figsize=(10, 8))
    plt.rcParams['font.family'] = 'Arial'

    plt.scatter(df_combined[x_col], df_combined[y_col], s=50)
    plt.plot(df_combined[x_col], regression_line, linewidth=2.5, color='orange')

    # Set x and y label
    plt.xlabel('Station ' + station_1, fontsize=16)
    plt.ylabel('Station ' + station_2, fontsize=16)

    # Change x-axis tick label size
    plt.tick_params(axis='x', labelsize=16)
    plt.tick_params(axis='y', labelsize=16)

    # Title
    plt.title('Station ' + station_1 + ' v.s ' + 'Station ' + station_2, fontsize=18, fontweight='bold')

    # Separator
    plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    # Text
    if intercept >= 0:
        regression_line_text = f'y = {slope:.3f}x + {intercept:.3f}'
    else:
        regression_line_text = f'y = {slope:.3f}x - {abs(intercept):.3f}'

    plt.text(20000, 5000, regression_line_text, fontsize=18)

    # Display the plot
    st.pyplot(plt)


    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()  # Close the plot to free memory

 # Center the download button using HTML
    st.download_button(
        label="Download Plot",
        data=buf,
        file_name=f'Station_{station_1}_vs_Station_{station_2}.png',
        mime='image/png'
    )

