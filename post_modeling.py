###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: post_modeling.py
# Description: creates a model to determine a successful post
# Usage: python post_modeling.py <num_nmf_features>
# Creation Date: 7/24/16
# Last Revision: 7/24/16
# Change Log:
#      7/24/16: took nmf function to here
###--------------------------------------------------------------------------###

# Import Section
import cPickle as pickle
import pandas as pd
from post_cleaning import tokenize_content
from sklearn.decomposition import NMF
import sys


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
    cols_names = [lf+str(num) for num in xrange(df.shape[0])]
    df.columns = cols_names

    # Merge onto post dataframe
    post_df = pd.concat([post_df, df], axis=1, join_axes=[post_df.index])
    return post_df



if __name__ == '__main__':
    try:
        num_features = sys.argv[1]
    except:
        nmf_features = 50


    # Load all pickled objest, post_df, post_tfidf, and tfidf
    print "Loading post df..."
    post_df = pd.read_pickle('post_df.pkl')
    tfidf_matrix  = pickle.load( open( 'post_tfidf_matrix.pkl', "rb" ) )
    tfidf  = pickle.load( open( 'post_tfidf.pkl', "rb" ) )

    # Perfrom nmf on tfidf to reduce dimensionality of the dataframe for models
    # W matrix is a:     post X latent_features      matrix
    print "Reducing dimension of tfidf matrix to {} features".format(nmf_features)
    W_matrix, nmf = nmf_on_posts(tfidf_matrix, latent_features=nmf_features)


    # Merge nmf matrix and post dataframe
    post_df = merge_W_with_post_df(W_matrix, post_df)
