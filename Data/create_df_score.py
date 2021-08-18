import sys
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine
import json
import os
import math
import process_data as p_data

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


def PB_score(n_received, n_viewed, n_completed):
    """
    This function calculate the PB (purchasing behavior) scores.
    
    INPUT
        n_received: (int) index of the offer received column
        n_viewed: (int) index of the offer viewed column
        n_completed: (int) index of offer completed column
    OUTPUT
        PB_score: (float) purchasing behavior score
    """
    score = 0
    
    if n_completed <= n_viewed: 
        PB_score = 10 * (n_received + 3 * n_viewed + 5 * n_completed) / (9 * n_received)
    else:
        PB_score = 10 * (n_received + 8 * n_viewed) / (9 * n_received)
    return np.round(PB_score, 2)


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


    # drop channels column
    portfolio.drop('channels', axis=1, inplace=True)

    portfolio = portfolio.rename(columns={'id':'offer_id', 'reward':'reward_amount'})
    profile = profile.rename(columns={'id':'customer_id'})
    transcript = transcript.rename(columns={'person':'customer_id'})

    df = transcript.merge(profile, how='left', on='customer_id')
    df = df.merge(portfolio, how='left', on='offer_id')
    return df



def clean_data(df, profile_filepath):
    """ Function to clean df data
    INPUT:
        df (DataFrame): A dataframe of df
    OUTPUT:
        df (DataFrame): A cleaned df
    """
    # create a dataframe that does not have 'transaction' info
    df_offer = df[df['event'] != 'transaction'].drop(['amount'], axis=1)

    # create dummy columns for event
    df_offer = pd.concat([df_offer, pd.get_dummies(df_offer['event'])], axis=1)

    # create a dataframe that has only transaction infro and compute the total spent amount
    df_transaction = df[df['event'] == 'transaction'].groupby('customer_id').agg({'amount':'sum'}).reset_index()

    profile = pd.read_json(profile_filepath, orient='record', lines=True)
    profile = profile.rename(columns={'id':'customer_id'})
    # Merge profile and df_transactions
    df_profile = profile.merge(df_transaction, how='left', on='customer_id')

    # Fill nan values with 0
    df_profile['amount'] = df_profile['amount'].fillna(0)

    # rename 'amount' to 'total_spent_amount'
    df_profile.rename(columns={'amount': 'total_spent_amount'}, inplace=True)
    
    # create a dataframe that have PB scores
    dct = {'offer received':'sum', 'offer viewed':'sum', 'offer completed':'sum'}
    df_score = df_offer.groupby(['customer_id', 'offer_number']).agg(dct)
    df_score['PB'] = [PB_score(df_score.iloc[i, 0], df_score.iloc[i, 1], df_score.iloc[i, 2]) for i in range(df_score.shape[0])]


    return df_score




def save_data(df_score):
    """ Function to save the data in sql file
    INPUT:
        df (DataFrame): A dataframe of three datasets
        database_filename (str): Path to save sql database
    """
    df_score.to_csv('df_score.csv')


def main():
    if len(sys.argv) == 5:
        portfolio_filepath, profile_filepath, transcript_filepath, csv_filepath = sys.argv[1:]

        print('Loading data...\n   PORTFOLIO: {}\n     PROFILE: {}\n    TRANSCRIPT: {}'.format(
            portfolio_filepath, profile_filepath, transcript_filepath))

        df = load_data(portfolio_filepath, profile_filepath, transcript_filepath)

        print('Cleaning data...')
        df_score = clean_data(df, profile_filepath)

        print('Saving data...\n     DATABASE: {}'.format(csv_filepath))
        save_data(df_score)

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





