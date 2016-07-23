###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: data_cleaning.py
# Description: start of cleaning process, may not hold full pipeline
# Usage: tbd
# Creation Date: 7/20/16
# Last Revision: 7/21/16
# Change Log:
#      7/20/16: Rough file to store cleaning commands. May turn into part of
#               pipeline in the future. Currently makes df from mongdodb
#      7/21/16: started in on feature engineering in dataframe
###--------------------------------------------------------------------------###

# Import Section
from pymongo import MongoClient
import pandas as pd

# Function Section
def get_df(db_name='fitness_blogs_w_comments', coll_name='blogs'):
    """
    DESCR: makes a dataframe from a given mongodb, assume mongo running
    INPUT: db_name and colletion name
    OUTUT: dataframe of database collection
    """
    # Make a mongo db clinet connection
    client = MongoClient()          # Make Connection mongo
    db = client[db_name]            # specify db
    coll = db[coll_name]            # specify collection

    # Make a cursor object for all documents in collection
    test = coll.find()              # make a cursor object

    # Genreate a list ann DF from the cursor object
    df = pd.DataFrame(list(test))   # create dataframe from cursor
    return df


def num_authors(posts):
    """
    DESCR: counter authors in a list of posts
    INPUT: posts - list of post
    OUTPUT: int of authors
    """
    return len(set([post['author']['ID'] for post in posts]))


def clean_df(df):
    """
    DESCR: cleans Dataframe in preperation for machine learning algorithms
    INPUT: messy Dataframe
    OUTPUT: clean DF
    """
    # Get rid of stuff that just has no chance of being useful
    worthless = ['_id', 'visible', 'is_private', 'is_following']
    df.drop(worthless, axis=1, inplace=True)

    # New Features Section
    #Feature for length of domain portion
    df['url_length'] = df['URL'].apply(lambda x: len(x.split('.')[0]) - 8)

    #Is it someting.wordpress.com or just something.com
    df['wordpress_in_url'] = df['URL'].apply(lambda x: 'wordpress.com' in x)

    #chars in blog name
    df['len_blog_name'] = df['name'].apply(lambda x: len(x))

    #words in blog name
    df['words_in_blog_name'] = df['name'].apply(lambda x: len(x.split()))
    df.drop('name', axis=1, inplace=True)

    # Check if single author
    df['single_author'] = df['post_list'].apply(lambda x: num_authors(x) == 1)

    # Stuff from post list
    df['num_posts'] = df['post_list'].apply(lambda x: len(x))
    df['start_date'] = df['post_list'].apply(lambda x: min([date_convert_w_error(post['modified']) for post in x]))
    df['most_recent_date'] = df['post_list'].apply(lambda x: max([date_convert_w_error(post['modified']) for post in x]))


    # Drop non blogs ie more than oe author
    df = df[df['single_author']]


    return df


def date_convert_w_error(date_string):
    """
    DESCR: to use in lambda date conversion to avoid wierd poor formatting errors that make pandas throw a fit, random date is then returned, this should only be used to avoid very uncommon errors.
    INPUT: date in string or unicode format
    OUTPUT: pandas date object
    """
    try:
        return pd.to_datetime(date_string)
    except:
        print "used error section"
        return pd.to_datetime('2015-01-04 10:10:10')


def filter_irrelevant_blogs(df, limit=0.3):
    key_words = ['running', 'run', 'train', 'fitness', 'lifting', 'soccer', 'football', 'baseball', 'basketball', 'ball', 'endurance', 'exercise', 'track', 'field', 'bike', 'bicycle']


if __name__ == '__main__':
    df = get_df()
    df = clean_df(df)
