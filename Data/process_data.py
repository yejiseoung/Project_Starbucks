import sys
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine
import json
import os
import math

def split_values(all_values):
    """ Function to get each value depending on event type from transcript.value column,
    and create each column of offer_id, reward, and amount that has boolean values (0,1)
    """
    # initialize lists
    value_lists = [], [], []
    for val in all_values:
        keys = val.keys()

        # getting the 'offer id' and 'offer_id'.
        if 'offer id' in keys:
            value_lists[0].append(val['offer id'])
        else: 
            if 'offer_id' in keys: value_lists[0].append(val['offer_id'])
            else: value_lists[0].append(np.nan)
        
        # getting 'reward'
        if 'reward' in keys:
            value_lists[1].append(val['reward'])
        else:
            value_lists[1].append(np.nan)
        
        # getting 'amount'
        if 'amount' in keys:
            value_lists[2].append(val['amount'])
        else:
            value_lists[2].append(np.nan)

        lst_offer = value_lists[0]
        lst_reward = value_lists[1]
        lst_amount = value_lists[2]

    return lst_offer, lst_reward, lst_amount



def load_data(portfolio_filepath, profile_filepath, transcript_filepath):
    """ Function to load 3 datasets (portfolio, profile, transcript)
    INPUTS:
        portfolio_filepath (str): Path to the "portfolio.json" file
        profile_filepath (str): Path to the "profile.json" file
        transcript_filepath (str): Path to the "transcript.json" file
    OUTPUTS:
        df (DataFrame): A dataframe of consisting of three files above
    """
    portfolio = pd.read_json(portfolio_filepath, orient='records', lines=True)
    profile = pd.read_json(profile_filepath, orient='record', lines=True)
    transcript = pd.read_json(transcript_filepath, orient='records', lines=True)

    # unzip the columns of transcript value to get {offer_id, reward, amount}
    transcript['offer_id'], transcript['reward'], transcript['amount'] = split_values(transcript['value'])

    transcript.drop('value', axis=1, inplace=True)

    # Create a column which indicates "offer_id"
    portfolio['offer_number'] = ['offer_' + str(portfolio.index[i]) for i in range(10)]

    # create columns which has each channel's info with boolean values (0,1) 
    portfolio['email'] = [1 if 'email' in portfolio['channels'][i] else 0 for i in range(10)]
    portfolio['mobile'] = [1 if 'mobile' in portfolio['channels'][i] else 0 for i in range(10)]
    portfolio['social'] = [1 if 'social' in portfolio['channels'][i] else 0 for i in range(10)]
    portfolio['web'] = [1 if 'web' in portfolio['channels'][i] else 0 for i in range(10)]

    # drop channels column
    portfolio.drop('channels', axis=1, inplace=True)

    portfolio = portfolio.rename(columns={'id':'offer_id', 'reward':'reward_amount'})
    profile = profile.rename(columns={'id':'customer_id'})
    transcript = transcript.rename(columns={'person':'customer_id'})

    df = transcript.merge(profile, how='left', on='customer_id')
    df = df.merge(portfolio, how='left', on='offer_id')
    return df



def clean_data(df):
    """ Function to clean df data
    INPUT:
        df (DataFrame): A dataframe of df
    OUTPUT:
        df (DataFrame): A cleaned df
    """

    # Create age_group column and the value of 118 will be 'NaN' in the age_group.
    age_bins = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 105]
    age_labels = ['10s', '20s', '30s', '40s', '50s', '60s', '70s', '80s', '90s', '100s']

    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)

    # replace missing values with "unknown"
    df['age_group'] = df['age_group'].cat.add_categories('unknown').fillna('unknown')

    # replace 118 values with NaN
    df['age'] = df['age'].replace(118, 'NaN')


    # Create income_group column
    income_bins = [25000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 1250000]
    income_labels = ['30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K', '110K', '120K']

    df['income_group'] = pd.cut(df['income'], bins=income_bins, labels=income_labels, right=False)

    # replace missing values with "unknown"
    df['income_group'] = df['income_group'].cat.add_categories('unknown').fillna('unknown')

    # extract became_year from became_member_on
    df['became_date'] = pd.to_datetime(df['became_member_on'], format='%Y%m%d')
    df['became_year'] = df['became_date'].dt.year

    # drop became_member_on
    df.drop('became_member_on', axis=1, inplace=True)

    return df






def save_data(df, database_filename):
    """ Function to save the data in sql file
    INPUT:
        df (DataFrame): A dataframe of three datasets
        database_filename (str): Path to save sql database
    """
    engine = create_engine('sqlite:///{}'.format(database_filename))
    df.to_sql('starbucks', engine, if_exists='replace', index=False)


def main():
    if len(sys.argv) == 5:
        portfolio_filepath, profile_filepath, transcript_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n   PORTFOLIO: {}\n     PROFILE: {}\n    TRANSCRIPT: {}'.format(
            portfolio_filepath, profile_filepath, transcript_filepath))

        df = load_data(portfolio_filepath, profile_filepath, transcript_filepath)

        print('Cleaning data...')
        df = clean_data(df)

        print('Saving data...\n     DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)

        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the portfolio, profile, and transcript '\
            'datasets as the first to third argument respectively, as'\
            'well as the file path of the database to save the cleaned data '\
            'to as the fourth argument. \n\nExample: python process_data.py '\
            'portfolio.json profile.json transcript.json'\
            'starbucks.db')

if __name__ == '__main__':
    main()





