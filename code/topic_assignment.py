###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: topic_assignment.py
# Description: for assigning blog posts to a given topic from trained stuff.
# Usage: tbd
# Creation Date: 7/26/16
# Last Revision: 7/26/16
# Change Log:
#      7/26/16: file started
###--------------------------------------------------------------------------###

# Import Section
import cPickle as pickle
import numpy as np
from collections import Counter

# Function Section
POST_TFIDF_PICKLE       = 'other_pickles/post_tfidf.pkl'
POST_NMF_PICKLE         = 'other_pickles/post_nmf.pkl'
W_MATRIX_PICKLE         = 'other_pickles/w_matrix.pkl'

def topic_sizes(W_matrix, limit = 0.0):
    """
    DESCR: given a W_matrix that is documents X latent features, assign each
           document to its highest latent feature and sum the columns.
    INPUT: W_matrix
    OUTPUT: list of length latent-features
    """
    return Counter(np.argmax(W_matrix, axis=1))


if __name__ == '__main__':
    # Get the tfidf - has the 10,000 word vocabulary
    post_tfidf = pickle.load( open(POST_TFIDF_PICKLE) )

    # Get the nmf, .componets_ is latent-features by 10,000
    post_nmf = pickle.load( open(POST_NMF_PICKLE) )

    # Get the W_matrix is        documents X latent-features
    W_matrix = pickle.load( open(W_MATRIX_PICKLE) )

    # Turn feature words in numpy array for lists indexing later
    words = np.array(post_tfidf.get_feature_names())

    # Topic sizes
    topic_counts = topic_sizes(W_matrix)


    # Find most relevant words and print to file
    with open('topic_analysis/topic_words.csv', 'wb') as f:
        f.write('topic_num, num_docs, words')
        for topic in xrange(post_nmf.components_.shape[0]):
            idx = np.argsort(post_nmf.components_[topic])[-15:][::-1]
            important = words[idx]

            f.write("{}, {}, {}\n".format(topic, topic_counts[topic], important))
