###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: post_cleaning.py
# Description: exploring nlp possibilties on posts
# Usage: python post_cleaning
# Creation Date: 7/21/16
# Last Revision: 7/23/16
# Change Log:
#      7/21/16: Exploration started
#      7/22/16: TFIDF made for post dataframe
#      7/23/16: NMF made for post dataframe, reconstruction error plot started
#               reconstruction of 1-100 error plot not sufficient, moved to
#               seperate file for running on aws for longer period
#               running file now loads a pickled blog df, and saved stuff as
#               pickled stuff
###--------------------------------------------------------------------------###

# Import Section
from sklearn.decomposition import NMF
import pandas as pd
from bs4 import BeautifulSoup
from string import punctuation
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from helpers import date_convert_w_error
from helpers import DF_BLOGS_UNCHANGED_PICKLE
import cPickle as pickle

# Constants
EXTRA_STOP_WORDS = []
STOP_WORDS = stopwords.words('english')
STOP_WORDS.extend(EXTRA_STOP_WORDS)


# Function Section
def get_posts_df_from_blog_df(df, post_col='post_list'):
    """
    DESCR: from a large df take a col of nested posts and turn into stand alone df
    INPUT:
        df - maindf to extract from, expected to have one column of post list
        post_col - specify column to turn into df
    OUTPUT:
        post_df - df of only only posts
    """
    #flatten series to list
    all_posts = df[post_col].tolist()

    # Put in chronological order, and then give each post an ordering num
    for post_list in all_posts:
        post_list.reverse()

        for ind, post in enumerate(post_list):
            post['number_of_post'] = ind + 1

    # Initialize the dataframe
    post_df = pd.DataFrame(all_posts[0])

    # Append each post list to data frame
    for post in all_posts[1:]:
        post_df = post_df.append(pd.DataFrame(post))

    return post_df


def clean_post_df(df):
    """
    DESCR: does some intial clenaing of post df, not a lot of though in some of these, currently many things just get dropped.
    INPUT: messy df
    OUTPUT: clean df
    """
    # Stuff to drop immediately
    drop_list = ['ID', 'capabilities', 'page_template', 'menu_order', 'global_ID', 'is_following', 'is_reblogged', 'URL', 'short_URL', 'password', 'i_like', 'modified', 'type', 'parent', 'status', 'slug', 'post_thumbnail', 'meta', 'author', 'metadata']
    df.drop(drop_list, axis=1, inplace=True)

    # Play with the dates a bit to make them useful
    df['date'] = df['date'].apply(lambda x: date_convert_w_error(x))
    df['day_of_week'] = df['date'].dt.dayofweek
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Sum a bunch of list columsn, maybe do better later
    df['num_comments'] = df['comments'].apply(lambda x: len(x))
    df['num_terms'] = df['terms'].apply(lambda x: len(x))
    df['num_tags'] = df['tags'].apply(lambda x: len(x))
    df['num_cats'] = df['categories'].apply(lambda x: len(x))
    df['num_pub_urls'] = df['publicize_URLs'].apply(lambda x: len(x))
    df['num_other_urls'] = df['other_URLs'].apply(lambda x: len(x))
    df['standard_post'] = df['format'].apply(lambda x: True if x=='standard' else False)


    #Drop, may put some more effort into some of these later
    df.drop(['title', 'excerpt', 'terms', 'tags', 'categories', 'comments', 'attachments', 'publicize_URLs', 'other_URLs', 'geo', 'format', 'guid', 'featured_image','discussion', 'date'], axis=1, inplace=True)

    return df


def get_text_from_content(df):
    """
    DESCR: takes the content column that is html, get the text from it
    INPUT: df with a content column that is html
    OUPTUT: df that has a content column ths is now text
    """
    # Retrive text
    df['content'] = df['content'].apply(lambda x: BeautifulSoup(x, 'lxml').get_text())

    # Somehow get some empty posts, thorws these away
    df = df[post_df['content'].apply(lambda x: x.strip()) != ""]

    return df


def tokenize_content(content):
    """
    DESCR: takes a big string, makes all lower, splits on ws, and strip junk to give backa nice tokenized list of words, may have to keep adding, also remove stop words
    INPUT: string
    OUTPUT: list of tokens
    """
    # Get rid of all punctuation, lowercase words, and split on ws
    tokens = [word.strip().strip(punctuation) for word in content.lower().split()]


    # remove stop words
    tokens = [word for word in tokens if word not in STOP_WORDS]

    # lemmatize tokens
    lemmer = WordNetLemmatizer()
    tokens = [lemmer.lemmatize(token) for token in tokens]
    return tokens


def tfidf_posts(post_series):
    """
    DESCR: perform nmf on content portion of df and return the nmf
    INPUT: a series full of blog post text, reach row is one post string
    OUTPUT: the resultant tfidf matrix and
            the tfidf object
    """
    # Make vectorizer object
    tfidf = TfidfVectorizer(decode_error='ignore', tokenizer=tokenize_content, max_df=1.0, min_df=5, max_features=20000, norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)

    # Make transformed document matrix
    tfidf_matrix = tfidf.fit_transform(post_series)

    return tfidf_matrix, tfidf


def nmf_on_posts(posts_tfidf, latent_features=15):
    """
    DESCR: perform NMF on on a tfidf matrix of blog posts
    INPUT: tfidf matrix
           num of latent features to decompose to
    OUTPUT: W_matrix - matrix of rows still as documents and columns as
                       latent features
            latent_features - columns in resultant W matrix
    """
    nmf = NMF(n_components=latent_features, tol=0.0001, max_iter=200, random_state=45, alpha=0.0, l1_ratio=0.0, verbose=0, shuffle=False, nls_max_iter=2000, sparseness=None, beta=1, eta=0.1)

    #fit model to post data, and then return transformed matrix

    W_matrix = nmf.fit_transform(posts_tfidf)
    return W_matrix, nmf




def make_success_col(df):
    """
    DESCR: adds collumn post succes to df. Will have to be some categorical, maybe just no_traction, some_traction, good_traction, great
    INPUT: df, needs column for likes and comments
    OUPUT:
    """
    df['success'] = df[like_count].apply(lambda x: x)


if __name__ == '__main__':
    # Load pickled data framepost_nlp
    print "Loading blog dataframe from {}".format(DF_BLOGS_UNCHANGED_PICKLE)
    df = pd.read_pickle(DF_BLOGS_UNCHANGED_PICKLE)
    print "   DF loaded has {} blogs".format(df.shape[0])

    # Turn into just a dataframe abot posts
    print "   Converting blog posts lists to post df..."
    post_df = get_posts_df_from_blog_df(df)
    print "   Post data frame has {} blog posts".format(post_df.shape[0])

    # Clean up post dataframe
    post_df = clean_post_df(post_df)
    post_df = get_text_from_content(post_df)
    print "   After cleaning post df has {} posts".format(post_df.shape[0])

    # transform posts series in to tfidf matrix
    print "   Converting post content to tfidf matrix..."
    tfidf_matrix, tfidf = tfidf_posts(post_df['content'])
    with open('post_tfidf_matrix.pkl', 'w') as f:
        pickle.dump(tfidf_matrix, f)
    with open('post_tfidf.pkl', 'w') as f:
        pickle.dump(tfidf, f)
    print "   tfidf object pickled as {}".format('post_tfidf.pkl')
    print "   tfidf matrix saved as {}".format('post_tfidf_matrix.pkl')


    # perform NMF on tfidf post matrix
    W_matrix, nmf = nmf_on_posts(tfidf_matrix, 25)
