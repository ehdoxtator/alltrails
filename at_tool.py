import json
import logging

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s: %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_SUMMARY = {'calories': None, 'duration': None, 'timeTotal': None, 'updatedAt': None,
                   'timeMoving': None, 'paceAverage': None, 'speedAverage': None, 'distanceTotal': None,
                   'elevationGain': None, 'elevationLoss': None}


def get_tsv(tsv_file):
    """get_tsv: fetches the data in the tab-separated values (.tsv) file
    :param tsv_file:  name of the .tsv file. Doesn't have to have .tsv in the extension
    """
    logger.info(f"Loading data from {tsv_file}...")
    df = pd.read_csv(tsv_file, sep='\t')
    return df


def clean(df):
    """
    clean: cleans the dataframe per the following rules:
    1. Normalize column case ('This_is_dAta' = 'this_is_data')
    Note: this is not terribly robust-- invariant characters, default value fills, etc don't exist.
    :param df: dataframe to clean
    :return: cleaned dataframe
    """

    # Normalize casing
    logger.info("Cleaning dataframe...")
    new_cols = dict(zip([col for col in df.columns.tolist() if col.lower() != col],
                        [col.lower() for col in df.columns.tolist() if col.lower() != col]))
    df.rename(columns=new_cols, inplace=True)

    return df


def validate(df, join_column):
    """validate: validates the following:
    1. join_column cannot be None
    2. join_column must be a column value in df.columns
    :param df: dataframe to validate
    :param join_column: column to dataframe joins
    :return: dataframe
    """

    logger.info('Validating dataframe...')
    if join_column is None:
        raise ValueError('Join column cannot be None.')

    if join_column not in df.columns.tolist():
        raise ValueError(f'Join column {join_column} not in dataframe.')

    # If a join column is specified, check to make sure there are no nulls
    if df[join_column].isnull().sum() > 0:
        raise ValueError('Cleaning error: data frame has a null value in a join column.')

    return df


def join(clean_dfs, join_column):
    """
    join: joins dataframes on a common column
    :param clean_dfs: a dict of dataframes to join
    :param join_column: the column to use for joining
    :return:
    """

    # Spin through the joinable dfs...
    logger.info(f"Joining {len(clean_dfs.keys())} dataframes... ")
    for idx, df_name in enumerate(clean_dfs.keys()):
        # ... make sure the join column is present...
        if join_column not in clean_dfs[df_name].columns.tolist():
            raise ValueError(f'Required join column \'{join_column}\' not in dataframe \'{df_name}\'')
        # ... if this is the first DF in the dict, just copy it
        if idx == 0:
            joined_df = clean_dfs[df_name].copy()
        # ... and successive dicts, join to the result joined_df
        else:
            joined_df = pd.merge(joined_df, clean_dfs[df_name], on=join_column)
    logger.info(f"Dataframes joined. After joining, shape is {joined_df.shape}")

    return joined_df


def get_summary(joined_df):
    """
    get_summary: extracts the json-formatted info from the recording_summary column, and appends
    the json nodes as pandas columns to the joined dataframe
    :param joined_df: dataframe containing the recording summary column
    :return: dataframe with recording summary information appended to each row, with clean column names
    """
    logger.info(f'Extracting summary data from {joined_df.shape[0]} rows...')

    no_count = 0

    # Pull the recording summary info as a dict from the DF...
    result = joined_df['recording_summary'].to_dict()

    # ...spin through the dict (index, json string)...
    for key, value in result.items():
        # ...if it is a string, load it as json...
        if isinstance(value, str):
            result[key] = json.loads(value)
        # ...otherwise, throw an error and defualt the summary data
        else:
            logger.debug(f'Found no recording summary data for key {key}. Using defaults.')
            result[key] = DEFAULT_SUMMARY
            no_count += 1

    logger.info(f"Summary retrieved. {no_count} rows without summary data.")

    # Reformat the data back into a data frame using from_dict.
    dcols = {key: [] for key in result[0].keys()}
    for row in result.values():
        for col in dcols.keys():
            dcols[col].append(row.get(col, 0))

    summary_df = pd.DataFrame.from_dict(dcols, orient='columns')

    full_df = pd.concat([joined_df, summary_df], axis='columns')

    logger.info(f"After adding summary info, shape is {full_df.shape}")

    return clean(full_df)


def get_time_diff(full_df):
    """
    get_time_diff: calculates the difference between signup and posting dates
    :param full_df:
    :return: df, with the columns date_signup, date_start, and delta_start_signup
    """
    full_df['date_signup'] = pd.to_datetime(full_df['signup_date'])
    full_df['date_start'] = pd.to_datetime(full_df['start_date'])
    full_df['delta_start_signup'] = full_df['date_start'] - full_df['date_signup']

    return full_df


def filter_df(df, null_column):
    """
    filter_df: filters out any dataframe rows with a null delta_start_signup
    :param df: dataframe to filter
    :param null_column:
    :return: dataframe where null column value is not null
    """
    if null_column not in df.columns.tolist():
        raise ValueError(f'null_column \'{null_column}\' not found. Cannot filter.')

    logger.info('Filtering out invalid rows...')

    df = df[~df[null_column].isnull()]

    logger.info(f'After filtering, shape is: {df.shape}')

    return df


def write_csv(df, outfile):
    """
    write_csv: writes the contents of a df to the local storage as a CSV
    :param df: dataframe to write
    :param outfile: path & name of output file
    """

    logger.info(f'Writing dataframe to {outfile}...')
    df.to_csv(outfile)