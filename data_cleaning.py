###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: data_cleaning.py
# Description: start of cleaning process, may not hold full pipeline
# Usage: python data_cleaning.py <df pickle name>
# Creation Date: 7/20/16
# Last Revision: 7/23/16
# Change Log:
#      7/20/16: Rough file to store cleaning commands.
#               May turn into part of pipeline in the future.
#               Currently makes raw df directly from mongdodb
#      7/21/16: started in on feature engineering in dataframe
#      7/23/16: aded function to filter out irrelevant blogs
#               moved some functions and constants to helper file
#               can now from from command line to load, clean and resave as pkl
###--------------------------------------------------------------------------###

# Import Section
from __future__ import division
from pymongo import MongoClient
import pandas as pd
from helpers import FITNESS_KEY_WORDS as KEY_WORDS
from helpers import date_convert_w_error
from helpers import DF_BLOGS_UNCHANGED_PICKLE
import sys


# Constant Section
PROPER_USAGE        = 'python data_cleaning.py <df pickle name - optional>'


# Main Function Section
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


def filter_irrelevant_blogs(df, limit=0.3):
    """
    DESCR: Given a dataframe, filter out all of the irrelevant blogs
    INPUT: df - df that needs filtering
    OUTPUT: tuple - dataframe has been filtered and the nuber dropped
    """
    # Mask the dataframe with bollean of relevant blogs
    return df[df['post_list'].apply(relevant_blog, limit=limit)]


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


# Support Function Section
def num_authors(posts):
    """
    DESCR: counter authors in a list of posts
    INPUT: posts - list of post
    OUTPUT: int of authors
    """
    return len(set([post['author']['ID'] for post in posts]))


def relevant_blog(post_list, limit, key_words=KEY_WORDS):
    """
    DESCR: given a list of posts and threshold for percent of post that hold
           the given words return whether a blog is relevant or not
    INPUT:
        post_list - list of post, where each post has a 'content' key
        limit - float, percent of documents that must contain keywords
        key_words - list of words to determine relevance
    OUTPUT:
        True if percent above limit otherwise false
    """
    # Define total number of posts
    total = len(post_list) + 1          # Don't need any divide by zero errors
    relevant = 0                        # initialize number relevant

    # Look through every post and decides its relevance
    for post in post_list:
        if any(word in post['content'].lower() for word in key_words):
            relevant += 1

    # Return decision
    if relevant / total >= limit:
        return True
    else:
        return False


if __name__ == '__main__':
    # Get Name to save pickled data frame as
    if len(sys.argv) == 2:
        save_name = sys.argv[1]
    elif len(sys.argv) == 1:
        save_name = DF_BLOGS_UNCHANGED_PICKLE
    else:
        print "ERROR usage: {}".format(PROPER_USAGE)
        sys.exit(-1)

    # Build dataframe from mongo database
    print "Retrievin Data from mongo....."
    df = get_df(db_name='fitness_blogs_w_comments', coll_name='blogs')
    print "   Raw Data Frame has {} blogs".format(df.shape[0])

    # Filter blogs for relevance to topic by word list
    df = filter_irrelevant_blogs(df, limit=0.6)
    print "   After filtering for relevance dataframe contains {} blogs".format(df.shape[0])

    # Clean up blog information, and toss multiple author 'non-blogs'
    df = clean_df(df)
    print "   After cleaning dataframe contains {} blogs".format(df.shape[0])

    # Pickle dataframe for later use
    df.to_pickle(save_name)
    print "   Dataframe pickled to file name: {}".format(save_name)
