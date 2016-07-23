###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: post_nlp.py
# Description: exploring nlp possibilties on posts
# Usage: tbd
# Creation Date: 7/21/16
# Last Revision: 7/22/16
# Change Log:
#      7/21/16: Exploration started
#      7/22/16:
###--------------------------------------------------------------------------###

# Import Section
from sklearn.decomposition import NMF
from data_cleaning import get_df, clean_df
import pandas as pd
from bs4 import BeautifulSoup
from string import punctuation
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

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
    DESCR: takes the content column and turns it into a list of tokens that have had all punctuation removed and stop words removed and then lemmatized
    """
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


def nmf_on_df(content_series):
    """
    DESCR: perform nmf on content portion of df and return the nmf
    """


    tfidf_matrix = tfidf.fit_transform(content_series)



def make_success_col(df):
    """
    DESCR: adds collumn post succes to df. Will have to be some categorical, maybe just no_traction, some_traction, good_traction, great
    INPUT: df, needs column for likes and comments
    OUPUT:
    """
    pass
    #maybe note needed yet


if __name__ == '__main__':
    df = get_df()
    df = clean_df(df)
    post_df = get_posts_df_from_blog_df(df)
    post_df = clean_post_df(post_df)
    post_df = get_text_from_content(post_df)
