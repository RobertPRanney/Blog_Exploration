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
#      7/24/16: plots the number in a reconstruction error file
###--------------------------------------------------------------------------###

# Import Section
import matplotlib.pyplot as plt
import cPickle as pickle
import seaborn as sns

def make_recon_errors_plot(recon_errors, features):
    """
    DESCR: given a list of recostruction error and features make and save a plot
    INPUT: list of errors(y), vs features vecotr(x)
    OUTPUT: none
    """
    fig, ax = plt.subplots()
    ax.plot(features, recon_errors)
    ax.axvline(x=30, lw=2, color='r', ls='dashed')
    ax.set_title('Reconstruction Error of Post tfidf After NMF', fontsize=20)

    ax.set_xlabel('Number of Latent Features', fontsize=16)

    ax.set_ylabel('Reconstruction Error', fontsize=16)

    plt.savefig('from_aws/plots/reconstruction_error.png')


if __name__ == '__main__':
    # Load tfidf matrix to use
    print "Opening list of errors...."
    with open("from_aws/recon_errors.pkl", "r") as input_file:
        recon_errors = pickle.load(input_file)

    features = range(1, len(recon_errors)+1)

    # make and save a plot
    make_recon_errors_plot(recon_errors, features)
