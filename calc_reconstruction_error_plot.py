###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: calc_reconstruction_error_plot.py <max num features>
# Description: plots reconstruction error for nmf on post data frame,  this
#              should probably not be run on my machine since it will take
#              forever
# Usage: pytho reconstruction_error_plot.py <num_features>
# Creation Date: 7/23/16
# Last Revision: 7/24/16
# Change Log:
#      7/23/16: started function, hopefully finsih today
#      7/24/16: change to just a calculate file for aws to do, plotting done in
#               seperate file on local
###--------------------------------------------------------------------------###

# Import Section
from helpers import nmf_on_posts
import cPickle as pickle
import sys

# Function Section
def find_reconstruction_errors(tfidf, min_features=1, max_features=20, verbose=False):
    """
    DESCR: calculate all reconstruction errors for given tfidf matrix
    INPUT:
        tfidf - tfidf for posts.
        min_features - start of plot range
        max_features - end of plot range
        verbose      - whether or not to print output to screen
    OUTPUT:
        recon_errors - list of reconstruction error (frobenius norm)
        features     - list of features numbers
    """
    # Empty list of reconstsruction errors
    recon_errors = []

    # Range to generate nmf over
    features = range(min_features, max_features + 1)

    # Calculate rcon err for all given features and add to list
    for feature in features:
        if verbose:
            print "   Running NMF on tfidf for {} features".format(feature)

        W_matrix, nmf = nmf_on_posts(tfidf, latent_features=feature)
        recon_errors.append(nmf.reconstruction_err_)

    return recon_errors, features


if __name__ == '__main__':
    # features to calculate to
    latent_features = int(sys.argv[1])

    # Load tfidf matrix to use
    print "Opening tfidf matrix for use......"
    with open("post_tfidf_matrix.pkl", "r") as input_file:
        tfidf_matrix = pickle.load(input_file)

    # calculate reconstruction erros
    print "Calculating list of reconstruction errors"
    recon_errors, features = find_reconstruction_errors(tfidf_matrix, min_features=1, max_features=latent_features, verbose=True)

    # Save so calculation doesn't need to be over if graphing changes
    with open('recon_errors.pkl', 'w') as f:
        pickle.dump(recon_errors, f)
