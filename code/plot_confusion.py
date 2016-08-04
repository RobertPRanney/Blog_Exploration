###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: plot_confusion.py
# Description: will plot all confution matrixes for all models
# Usage: python plot_confusion.py <models_path> <df_path> <save_path>
# Creation Date: 7/25/16
# Last Revision: 7/25/16
# Change Log:
#      7/25/16: moved to serpeate file from grid search
#               runs through pickled models and make plot of each
###--------------------------------------------------------------------------###

# Import Section
import os
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import cPickle as pickle
from sklearn.cross_validation import train_test_split
import pandas as pd
import numpy as np
import sys

# Constant Section
RANDOM_NUM = 42         # for reproducibility between files and runs



# Function Section
def plot_confusion_matrix(cm, est_name, save_loc, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    DESCR: make confusion plot for a given confustion matrix save fig to files
    INPUT: cm - square array of int or floats, name for fig, title, color
    OUPUT: none, figure is saved to disk
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title + '\n'+ est_name)
    plt.colorbar()
    tick_marks = np.arange(len(target_names))
    plt.xticks(tick_marks, target_names, rotation=45)
    plt.yticks(tick_marks, target_names)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

    plt.savefig(save_loc + est_name + '.png', bbox_inches='tight')
    plt.close()



if __name__ == '__main__':
    # get paths to pull data and place results
    models_path = sys.argv[1]
    df_path = sys.argv[2]
    save_path = sys.argv[3]

    #get some data
    # load in data and split for training
    post_df_w_nmf = pd.read_pickle(df_path)
    y = post_df_w_nmf.pop('success')
    target_names = np.array(['no traction', 'some traction', 'good traction', 'great traction'])

    #Remove columns that lead to data leakage if present
    try: post_df_w_nmf.drop('like_count', axis=1, inplace=True)
    except: pass
    try: post_df_w_nmf.drop('num_comments', axis=1, inplace=True)
    except: pass
    try: post_df_w_nmf.drop('success', axis=1, inplace=True)
    except: pass

    # Generate same test and train split used troughout
    X_train, X_test, y_train, y_test = train_test_split(post_df_w_nmf, y, test_size=0.1, random_state=42)


    # For every model in pickle folder, generate and save confusion_matrix
    for i in os.listdir(models_path):
        model = pickle.load ( open( models_path + str(i), 'rb') )

        # calculate confusion and then normalize
        cm = confusion_matrix(y_test ,model.predict(X_test), labels=target_names)
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        # plot
        plot_confusion_matrix(cm, str(i.split('.')[0]), save_path)
