import config
import os
import pathlib
import pandas as pd
from datetime import datetime
from datetime import timedelta
from mail_generator import html_format
from mail_generator import mail_setup

csv_filepath = "eventfile.csv"

column_name_src = config.col_name_source   # Name of the column contain filter values
filter_name_src = config.col_name_src_filterval  # column value to be filtered
column_name_grp = config.col_name_grp            # Column name of Error values
column_name_grp_filterval = config.col_name_grp_filterval # Error to be filtered
time_dilation = config.timeframe     # Timeframe consideration
required_col = config.required_col
current_time = datetime.strptime("2025-07-10 06:57:24", "%Y-%m-%d %H:%M:%S") # during prod we can use actual curr datetime
df = pd.read_csv(csv_filepath)
print("Type of the time input in csv",type(df["TimeCreated"][0]))
df_empty = pd.DataFrame()
def timeframe_filter():
    """
    Function used to filter the timeframe column with 'n' hours interval
    :return: filtered dataframe
    """
    try:
        # Ensure 'TimeCreated' is actual as in datetime format
        df['TimeCreated'] = pd.to_datetime(df['TimeCreated'], errors='coerce')
        df['TimeCreated'] = df['TimeCreated'].dt.floor('S')     # Removing microseconds in the ps
        df['TimeCreated'] = df['TimeCreated'].dt.tz_localize(None)

        initial_time = current_time - timedelta(hours=8)  # Time dilation calculation
        print("Type after conversion",type(df["TimeCreated"][0]))
        print("Initial Time",initial_time)
        recent_df = df[(df['TimeCreated'] >= initial_time) & (df['TimeCreated'] <= current_time)]    # Filter within 'x' hours period
        print("Time dilation 1", recent_df["TimeCreated"].iloc[0])
        print("Time dilation 2", recent_df["TimeCreated"].iloc[-1])
        return recent_df
    except Exception as e:
        print("Exception occured while calling timeframe filter function", e)
        return df_empty


def source_filter(time_filtered):
    """
    Function used to filter the dataframe which is the output of timeframe filter fn. filter with certain column val
    :return: filtered dataframe (only with specific col values)
    """
    allowed_src_value = [filter_name_src]
    try:
        src_filtered_df = time_filtered[time_filtered["Source"].isin(allowed_src_value)]  # Filtering only specific column value (ent col)
        # print("Filtered df inside src col", src_filtered_df)
        return src_filtered_df

    except Exception as e:
        print("Exception occured while source filter function", e)
        return df_empty

def grp_filter(src_filtered):
    """
    Function used to filter the df returned from source filter function. filters the ERROR values
    :param src_filtered: dataframe
    :return: filtered dataframe (Only required column values)
    """
    allowed_grp = [column_name_grp_filterval]
    try:
        print("Inside Grp filter")
        grp_filtered_df = src_filtered[src_filtered[column_name_grp].isin(allowed_grp)]
        # print(grp_filtered_df["Grp"])
        if len(grp_filtered_df) !=0:
            grp_filtered_df = grp_filtered_df[required_col]  # Only required column will be taken
            return grp_filtered_df
        else:
            return df_empty

    except Exception as e:
        print("Exception occured while calling grp filter function", e)
        return df_empty

if __name__ == "__main__":
    time_filtered_df = timeframe_filter()
    if len(time_filtered_df)>0:
        source_filtered_df = source_filter(time_filtered_df)
        if len(source_filtered_df) >0:
            final_filtered_df = grp_filter(source_filtered_df)
            if len(final_filtered_df) !=0:
                html_body = html_format(final_filtered_df, "User")
                print(html_body)
                status = mail_setup(html_body)


