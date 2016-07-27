###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: post_cleaning.py
# Description: takes a data fraom of blogs, pulls out the posts and the cleans
#              them in preparation for ML algorithms
# Usage: python post_cleaning
# Creation Date: 7/21/16
# Last Revision: 7/26/16
# Change Log:
#      7/21/16: Exploration started
#      7/22/16: TFIDF made for post dataframe
#      7/23/16: NMF made for post dataframe, reconstruction error plot started
#               reconstruction of 1-100 error plot not sufficient, moved to
#               seperate file for running on aws for longer period
#               running file now loads a pickled blog df, and saved stuff as
#               pickled stuff
#      7/24/16: moved nmf function to post_modeling, pickled post tfidf and df
#      7/25/16: changing up 'success' some, added new features for commented
#               enabled and for number of images and links
#      7/26?16: change save location of pickles, file should be done now
###--------------------------------------------------------------------------###

# Import Section
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from helpers import date_convert_w_error, tokenize_content
import cPickle as pickle


# Constants
BLOG_DF_W_POSTS_PICKLE      = 'pickled_dfs/blog_df_w_posts.pkl'
POST_TFIDF_MATRIX_PICKLE    = 'other_pickles/post_tfidf_matrix.pkl'
POST_TFIDF_PICKLE           = 'other_pickles/post_tfidf.pkl'
POST_DF_PICKLE              = 'pickled_dfs/post_df.pkl'


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


def tag_counter(tag_name, html):
    """
    DESCR: use to find some information about extra stuff in html content
    INPUT: tag to count, and html content to look in
    OUTPUT: integer count fo tag
    """
    soup = BeautifulSoup(html, "lxml")
    return len(soup.find_all(tag_name))


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
    df['day_of_week'] = df['date'].apply(lambda x: x.weekday())
    df['year'] = df['date'].apply(lambda x: x.year)
    df['month'] = df['date'].apply(lambda x: x.month)

    # Sum a bunch of list columsn, maybe do better later
    df['num_comments'] = df['comments'].apply(lambda x: len(x))
    df['comments_enabled'] = df['discussion'].apply(lambda x: x['comments_open'])
    df['num_tags'] = df['tags'].apply(lambda x: len(x))
    df['num_cats'] = df['categories'].apply(lambda x: len(x))
    df['num_pub_urls'] = df['publicize_URLs'].apply(lambda x: len(x))
    df['num_other_urls'] = df['other_URLs'].apply(lambda x: len(x))
    df['standard_post'] = df['format'].apply(lambda x: True if x=='standard' else False)
    df['num_links'] = df['content'].apply(lambda x: tag_counter('a', x))
    df['num_images'] = df['content'].apply(lambda x: tag_counter('img', x))


    #Drop, may put some more effort into some of these later
    df.drop(['title', 'excerpt', 'terms', 'tags', 'categories', 'comments', 'attachments', 'publicize_URLs', 'other_URLs', 'geo', 'format', 'guid', 'featured_image','discussion', 'date', 'terms'], axis=1, inplace=True)

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


def tfidf_posts(post_series):
    """
    DESCR: perform nmf on content portion of df and return the nmf
    INPUT: a series full of blog post text, reach row is one post string
    OUTPUT: the resultant tfidf matrix and
            the tfidf object
    """
    # Make vectorizer object
    tfidf = TfidfVectorizer(decode_error='ignore', tokenizer=tokenize_content, max_df=1.0, min_df=5, max_features=10000, norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)

    # Make transformed document matrix
    tfidf_matrix = tfidf.fit_transform(post_series)

    return tfidf_matrix, tfidf


def make_success_col(df):
    """
    DESCR: adds collumn post succes to df. Will have to be some categorical, maybe just no_traction, some_traction, good_traction, great
    INPUT: df, needs column for likes and comments
    OUPUT:
    """
    df['num'] = (df['like_count'] * 2) + df['num_comments']
    df['success'] = df['num'].apply(succes_ranges)
    df.drop('num', axis=1, inplace=True)
    return df


def succes_ranges(num):
    """
    DESCR: Function to seperate out success into categories. Current separtion
           on test set gives about 50/20/15/15 seperation
    INPUT: num (likes + comments)
    OUTPUT: string (successcategory)
    """
    if num == 0:
        return "no traction"

    elif num < 3:
        return "some traction"

    elif num < 10:
        return "good traction"

    else:
        return "great traction"


if __name__ == '__main__':
    # Load pickled data framepost_nlp
    print "Loading blog dataframe from {}".format(BLOG_DF_W_POSTS_PICKLE)
    df = pd.read_pickle(BLOG_DF_W_POSTS_PICKLE)
    print "   DF loaded has {} blogs".format(df.shape[0])

    # Turn into just a dataframe abot posts
    print "   Converting blog posts lists to post df..."
    post_df = get_posts_df_from_blog_df(df)
    print "   Post data frame has {} blog posts".format(post_df.shape[0])

    # Clean up post dataframe
    post_df = clean_post_df(post_df)
    post_df = get_text_from_content(post_df)
    print "   After cleaning post df has {} posts".format(post_df.shape[0])

    # Make a categorical success column
    post_df = make_success_col(post_df)

    # transform posts series in to tfidf matrix
    print "   Converting post content to tfidf matrix..."
    tfidf_matrix, tfidf = tfidf_posts(post_df['content'])

    # pickle everything for later
    pickle.dump( tfidf_matrix, open( POST_TFIDF_MATRIX_PICKLE, "wb" ) )
    pickle.dump( tfidf, open( POST_TFIDF_PICKLE, "wb" ) )
    post_df.to_pickle(POST_DF_PICKLE)
    print "   tfidf object pickled as {}".format(POST_TFIDF_PICKLE)
    print "   tfidf matrix saved as {}".format(POST_TFIDF_MATRIX_PICKLE)
    print "   post df saved as {}".format(POST_DF_PICKLE)
