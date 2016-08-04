###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: blog_modeling.py
# Description: start modeling on blogs
# Usage: python post_modeling.py <num_nmf_features>
# Creation Date: 7/24/16
# Last Revision: 7/24/16
# Change Log:
#      7/27/16: start
###--------------------------------------------------------------------------###

# Import Section
from __future__ import division
import numpy as np
import pandas as pd
import cPickle as pickle
from bs4 import BeautifulSoup
from collections import Counter

# Constants and Globals
BLOG_DF_W_POSTS_PICKLE      = 'pickled_dfs/blog_df_w_posts.pkl'
POST_TFIDF_PICKLE           = 'other_pickles/post_tfidf.pkl'
POST_NMF_PICKLE             = 'other_pickles/post_nmf.pkl'
BLOG_DF_POSTS_CATEGORIZED   = 'pickled_dfs/blog_df_posts_categorized.pkl'

# Function Section
def classify_one_post(post_obj):
    """
    DESCR: Takes single post obj/dct that has a content key. Classifies whats in
           in here to a single latent topic number
    INPUT: post object
    OUTPUT: int, topic number
    """
    content = BeautifulSoup(post_obj['content'], 'lxml').get_text()
    content = trained_tfidf.transform([content])
    weights = trained_nmf.transform(content)
    return np.argmax(weights)


def classify_all_posts_in_blog(post_list):
    """
    DESCR: Takes a post lst and classifies all the posts in the post list and
           then returns that list
    INPUT: list of posts
    OUTPUT: list of ints
    """
    global BLOG_PROCESSED
    print "Processing blog: {}".format(BLOG_PROCESSED)
    BLOG_PROCESSED += 1
    post_class = [classify_one_post(post) for post in post_list]
    return post_class


def calc_topic_percents(topic_list, ind=0):
    """
    DESC: return  the percent of a bog is in a given topic, 0 is first most
          common, 1 is second most common etc...
    INPUT: a list of topics [5,4,3,2...]
    OUTPUT: float, ie 0.55 are in the second most common topci
    """
    try:
        return Counter(topic_list).most_common()[ind][1] / len(topic_list)
    except:
        return 0.0


def add_final_features(df):
    """
    DESCR: Some last mintue featue engineerig for blogs, taking into account the
           newly classfied posts
    INPUT: df
    OUTPUT: df with a few extra columns
    """
    df['highest_like'] = df['likts_history'].apply(max)
    df['highest_comments'] = df['comment_history'].apply(max)
    df['number_topics'] = df['post_topics'].apply(lambda x: len(set(x)))
    df['most_common_topic'] = df['post_topics'].apply(lambda x: Counter(x).most_common()[0][0])
    df['highest_topic_percent'] = df['post_topics'].apply(lambda x: calc_topic_percents(x, 0))
    df['second_highest_percent'] = df['post_topics'].apply(lambda x: calc_topic_percents(x, 1))
    df['third_highest_percent'] = df['post_topics'].apply(lambda x: calc_topic_percents(x, 2))
    df['single_topic_blog'] = df['highest_topic_percent'] > 0.85


    return df


if __name__ == '__main__':
    #Global for reporting
    BLOG_PROCESSED = 0

    blog_df = pd.read_pickle( BLOG_DF_W_POSTS_PICKLE )
    trained_tfidf = pickle.load ( open(POST_TFIDF_PICKLE, 'rb') )
    trained_nmf = pickle.load( open(POST_NMF_PICKLE, 'rb') )

    #Steps to classify a pst
    # 1) use tfidf object to transfom the content into a vector
    # 2) use nmf object to transform vector into latent feature vector
    # 3) pick highest column value and assign it that index num
    blog_df['post_topics'] = blog_df['post_list'].apply(classify_all_posts_in_blog)



    # Get rid of posts content to reduce size
    blog_df.drop('post_list', axis=1, inplace=True)
    blog_df.drop(['URL', 'description', 'icon', 'lang', 'single_author'], axis=1, inplace=True)

    # Some last features
    blog_df = add_final_features(blog_df)

    # Save for ML algorithms
    # still not quite done, but not sure how to deal with list contents
    # this file is a long run though so this is a good save step
    blog_df.to_pickle(BLOG_DF_POSTS_CATEGORIZED)
