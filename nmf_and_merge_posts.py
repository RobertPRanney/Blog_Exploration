###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: post_modeling.py
# Description: creates a model to determine a successful post
# Usage: python post_modeling.py <num_nmf_features>
# Creation Date: 7/24/16
# Last Revision: 7/24/16
# Change Log:
#      7/24/16: took nmf function to here
#               took away nmf to helprs, it is used to often, this file now just
#               nmfs, the posts, and then merges into on datafram
###--------------------------------------------------------------------------###

# Import Section
import cPickle as pickle
import pandas as pd
from post_cleaning import tokenize_content
from helpers import nmf_on_posts
import sys
import numpy as np


# Constant Section
POST_DF_PICKLE              = 'pickled_dfs/post_df.pkl'
POST_TFIDF_MATRIX_PICKLE    = 'other_pickles/post_tfidf_matrix.pkl'
POST_TFIDF_PICKLE           = 'other_pickles/post_tfidf.pkl'
POST_NMF_PICKLE             = 'other_pickles/post_nmf.pkl'
POST_DF_W_NMF_PICKLE        = 'pickled_dfs/post_df_w_nmf.pkl'
W_MATRIX_PICKLE             = 'other_pickles/w_matrix.pkl'


# Function Section
def merge_W_with_post_df(W_matrix, post_df):
    """
    Descr: Puts the resultant matrix of the NMF on the post tfidf matrix onto the post dataframe
    INPUT:
        W_matrix - matrix of size M x c
        post_df  - dataframe of size M x d
    OUPUT:
        result   - df for size M x (d+c)
    """
    # Create latent feature df with relevant ish column names
    df = pd.DataFrame(W_matrix)
    col_names = ['lf'+str(num) for num in xrange(df.shape[1])]
    df.columns = col_names

    # Merge onto post dataframe
    post_df = pd.concat([post_df, df], axis=1, join_axes=[post_df.index])
    return post_df


def add_main_topic_col(W_matrix, post_df):
    """
    DESCR: Add a main colum based on highest nmf weight
    INPUT: W_matrix to find max value of and post df to  series to
    OUTPUT: post_df with new main topic column
    """
    post_df['main_topic'] = pd.Series(np.argmax(W_matrix, axis=1))
    return post_df


def content_to_num_words_and_drop(post_df):
    """
    DESCR: content string still hanging around at this point, needs to go,
           particulalry if I would like to try and bring this df down to local
           to do some eda. So convert to num words and throw away
    INPUT: post_df with content
    OUPUT: post_df with word count and content gone
    """
    post_df['num_words'] = post_df['content'].apply(lambda x: len( x.split() ) )
    post_df.drop('content', axis=1, inplace=True)
    return post_df

if __name__ == '__main__':
    try:
        nmf_features = int(sys.argv[1])
    except:
        nmf_features = 30


    # Load all pickled objest, post_df, post_tfidf, and tfidf
    print "Loading post df..."
    post_df = pd.read_pickle(POST_DF_PICKLE)
    tfidf_matrix  = pickle.load( open( POST_TFIDF_MATRIX_PICKLE, "rb" ) )
    tfidf  = pickle.load( open( POST_TFIDF_PICKLE, "rb" ) )

    # Perfrom nmf on tfidf to reduce dimensionality of the dataframe for models
    # W matrix is a:     post X latent_features      matrix
    print "Reducing dimension of tfidf matrix to {} features".format(nmf_features)
    W_matrix, nmf = nmf_on_posts(tfidf_matrix, latent_features=nmf_features)

    #Pickle nmf for future use
    pickle.dump( nmf, open( POST_NMF_PICKLE, "wb" ) )
    pickle.dump( W_matrix, open( W_MATRIX_PICKLE, 'wb') )
    print "   nmf object pickled to {}".format(POST_NMF_PICKLE)
    print "   nmf w matrix pickled to {}".format(W_MATRIX_PICKLE)


    # Merge nmf matrix and post dataframe, pickle for later use
    post_df = merge_W_with_post_df(W_matrix, post_df)
    post_df = add_main_topic_col(W_matrix, post_df)
    post_df = content_to_num_words_and_drop(post_df)
    post_df.to_pickle(POST_DF_W_NMF_PICKLE)
    print "   post df with nmf pickled to {}".format(POST_DF_W_NMF_PICKLE)
