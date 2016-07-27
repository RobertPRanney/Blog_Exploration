###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: data_cleaning.py
# Description: takes a dataframe of posts and prepares it so that it can be used
#              to fit models to decide on blog factors that contribute to
#              success.
# Usage: python data_cleaning.py 
# Creation Date: 7/20/16
# Last Revision: 7/26/16
# Change Log:
#      7/20/16: Rough file to store cleaning commands.
#               May turn into part of pipeline in the future.
#               Currently makes raw df directly from mongdodb
#      7/21/16: started in on feature engineering in dataframe
#      7/23/16: aded function to filter out irrelevant blogs
#               moved some functions and constants to helper file
#               can now from from command line to load, clean and resave as pkl
#      7/24/16: freezes when trying to run on whole data set on aws. Rewritten
#               to iterate through mongo cursor object and append documents one
#               at a time to dataframe
#               Ok still won;t run on aws, runs out of memory, not sure how a
#               1.5G mongo blows up to 15G in df, probably my bad usage. Rather
#               than be smart run this one a large (30-60G) instance
#      7/26/16: Last time through. Going to do final feature engineering so that
#               hopefully this will be ready to start using to fit models.
#               saves a df with posts and one without posts
###--------------------------------------------------------------------------###

# Import Section
from __future__ import division
from pymongo import MongoClient
import pandas as pd
import numpy as np
import sys
from helpers import FITNESS_KEY_WORDS as KEY_WORDS
from helpers import date_convert_w_error


# Constant Section
PROPER_USAGE            = 'python data_cleaning.py <df pickle name - optional>'
PERCENT_RELEVANT        = 0.7       # Percent blogs that need to be on topic
BLOG_DF_W_POSTS_PICKLE  = 'pickled_dfs/blog_df_w_posts.pkl'
BLOG_DF_WO_POSTS_PICKLE = 'pickled_dfs/blog_df_wo_posts.pkl'


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
    doc_gen = coll.find()           # make a cursor object

    # initlaizze the dataframe from first row
    first = doc_gen.next()
    df = pd.DataFrame([first])

    # Continue building datframe one at a time from cursor object
    try:
        blog_num = 0
        while doc_gen.alive:
            print "Retrieveing num: {}".format(blog_num)
            new_row = doc_gen.next()
            df = df.append([new_row])
            blog_num += 1
    except:
        print "Cursor empty"

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
    worthless = ['_id', 'visible', 'is_private', 'is_following', 'logo', 'meta']
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
    df['blog_life_in_days'] = (df['most_recent_date'] - df['start_date']).apply(lambda x: x.days)


    # Create likes hist, comments hist, avg and std in post gaps
    df['likts_history'] = df['post_list'].apply(lambda x: posts_to_likes(x))
    df['comment_history'] = df['post_list'].apply(lambda x: post_to_comments(x))
    df['average_gap'] = df['post_list'].apply(lambda x: avg_and_stddev_days_between_posts(x)[0])
    df['std_dev_gap'] = df['post_list'].apply(lambda x: avg_and_stddev_days_between_posts(x)[1])

    # Drop non blogs ie more than one author
    df = df[df['single_author']]

    return df


# Support Function Section
def num_authors(posts):
    """
    DESCR: counter authors in a list of posts
    INPUT: posts - list of post
    OUTPUT: int of authors
    """
    # Very pretty one liner, but not robust enough, put in try except to handle a cases that throw errors, will probably throw out a few too many blogs
    try:
        num = len(set([post['author']['ID'] for post in posts]))
    except:
        return 2 # this will throw malformed blog away

    return num


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


def posts_to_likes(post_list):
    """
    DESCR: turns a list of posts into a list of likes
    INPUT: list of posts
    OUPUT: list of like counts
    """
    likes = []
    for post in post_list:
        try:
            likes.append(post['like_count'])
        except:
            pass
    likes.reverse()             # posts pulled newest to oldest
    return likes


def post_to_comments(post_list):
    """
    DESCR: turns a list of posts into a list of comments
    INPUT: list of posts
    OUPUT: list of comment counts
    """
    num_comments = []
    for post in post_list:
        try:
            num_comments.append(post['discussion']['comment_count'])
        except:
            pass
    num_comments.reverse()          # post pulled newest to oldest
    return num_comments


def avg_and_stddev_days_between_posts(post_list):
    """
    DESCR: calculates average time between posts and standard deviation
    INPUT: lists of posts
    OUPUT: tuple (avg, std)
    """
    dates = [date_convert_w_error(post['modified']) for post in post_list]
    dates.reverse()
    diffs = [next_one - current for current, next_one in zip(dates[:-1], dates[1:])]
    diffs = [delta.days for delta in diffs]

    return (np.mean(diffs), np.std(diffs))


if __name__ == '__main__':
    # Build dataframe from mongo database
    print "Retrievin Data from mongo....."
    df = get_df(db_name='fitness_blogs_w_comments', coll_name='blogs')
    print "   Raw Data Frame has {} blogs".format(df.shape[0])

    # Filter blogs for relevance to topic by word list
    df = filter_irrelevant_blogs(df, limit=PERCENT_RELEVANT)
    print "   After filtering for relevance dataframe contains {} blogs".format(df.shape[0])

    # Clean up blog information, and toss multiple author 'non-blogs'
    df = clean_df(df)
    print "   After cleaning dataframe contains {} blogs".format(df.shape[0])

    # Pickle dataframe for later use
    df.to_pickle(BLOG_DF_W_POSTS_PICKLE)
    df.drop('post_list', axis=1, inplace=True)
    df.to_pickle(BLOG_DF_WO_POSTS_PICKLE)
    print "   Dataframe with posts pickled to file name: {}".format(BLOG_DF_W_POSTS_PICKLE)
