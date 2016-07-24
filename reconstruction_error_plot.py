###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: reconstruction_error_plot.py
# Description: plots reconstruction error for nmf on post data frame,  this
#              should probably not be run on my machine since it will take
#              forever
# Usage: pytho reconstruction_error_plot.py <num_features>
# Creation Date: 7/23/16
# Last Revision: 7/23/16
# Change Log:
#      7/23/16: started function, hopefully finsih today
###--------------------------------------------------------------------------###

# Import Section


# Function Section
def plot_reconstruction_err(tfidf, min_features=1, max_features=20, verbose=False):
    recon_errors = []
    features = range(min_features, max_features + 1)

    for feature in features:
        if verbose:
            print "Running NMF on tfidf for {} features".format(feature)

        W_matrix, nmf = nmf_on_posts(tfidf, latent_features=feature)
        recon_errors.append(nmf.reconstruction_err_)

    return recon_errors, features












if __name__ == '__main__':

    recon_errors, features = plot_reconstruction_err(tfidf_matrix, min_features=1, max_features=100, verbose=True)
