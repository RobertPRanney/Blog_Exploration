###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: topic analysis.py
# Description: begining of looking into main topics dicovered by nmf in on tfidf
#              matrix for fitness blogs
# Usage: python topic_analysis.py <num_descriptive_words>
# Creation Date: 7/25/16
# Last Revision: 7/27/16
# Change Log:
#      7/25/16: file started
#      7/27/16: will now create a csv of with <topic num>, <num docs>, <words>
###--------------------------------------------------------------------------###

# Import Section
import cPickle as pickle
import numpy as np
from collections import Counter
import csv
import sys

# Constants
DESCRIP_DEFAULT = 20

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
    # Descriptive words
    try:
        num_descriptive_words = sys.argv[1]
    except:
        num_descriptive_words = DESCRIP_DEFAULT

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
        # Make an obejct to write to csv
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        # Add header row to doc
        writer.writerow(['topic', 'num_docs', 'important'])

        # for every single latent features write the desriptives words to csv
        for topic in xrange(post_nmf.components_.shape[0]):
            #Find the indexes with the highest term weights
            idx = np.argsort(post_nmf.components_[topic])[-num_descriptive_words:][::-1]
            # get the terms from resulting indexes
            important = words[idx]
            #write to file
            writer.writerow([topic, topic_counts[topic], important])
