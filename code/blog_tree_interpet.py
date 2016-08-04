###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: tree_interpet.py.py
# Description: tbd
# Usage: python tree_interpet.py <path_to_model> <path_to_df>
# Creation Date: 7/29/16
# Last Revision: 7/29/16
# Change Log:
#      7/29/16: gaining some random forest interpretability
###--------------------------------------------------------------------------###

# Import section
import cPickle as pickle
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.ensemble.partial_dependence import partial_dependence
from sklearn.cross_validation import train_test_split
from ew_pred_prob import predicted_value_plot

# Constant Sections
RANDOM_NUM = 42

# Get feature importance
def make_feat_plot(model, features):
    # Create plot and add data to it
    fig, ax = plt.subplots(figsize=(10,10))
    width = 0.8
    importance = model.feature_importances_
    xlabels = features
    importance, xlabels = zip(*sorted(zip(importance, xlabels), reverse=True))
    importance = importance[1:]
    xlabels = xlabels[1:]
    ind = np.arange(len(importance))
    ax.bar(ind, importance, width)

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Feature Importance', fontsize=20)
    ax.set_title('Feature importance for Blogs', fontsize=20)
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(xlabels, rotation='vertical', fontsize=16)
    fig.tight_layout()

    plt.show()

def make_part_plot(mdoel, features):
    importance = model.feature_importances_
    importance = np.argsort(importance)[::-1]
    importance = importance[10:25]

    fig, axs = plot_partial_dependence(model, df, importance,
                                       feature_names=features,
                                       n_jobs=3, grid_resolution=50)

    for ax in axs:
        name = ax.get_xlabel()
        ax.set_xlabel(name, fontsize=16)
        ax.set_ylim(-4,4)

        if name == 'average_gap':
            ax.set_xlim(0, 6)
            #ax.set_ylim(-2, 2)
        if name == 'highest_like':
            ax.set_ylim(-10, 40)
        if name == 'highest_topic_percent':
            ax.set_xlim(0.5, 0.8)
        if name == 'url_length':
            ax.set_xlim(0,25)



    fig.suptitle('Partial Dependence Plot for Selected Features \n Effect on Subscribers Count', fontsize=24)
    plt.subplots_adjust(top=0.9)  # tight_layout causes overlap with suptitle

    plt.show()


def make_pred_plot(model, X_test, y_test):
    fig, ax = plt.subplots()
    ax.scatter(y_test, model.predict(X_test))
    ax.set_xlabel('Acutal')
    ax.set_ylabel('Predicted')
    ax.set_title('')
    plt.show()


if __name__ == '__main__':
    model_path = sys.argv[1]
    df_path = sys.argv[2]
    y_path = sys.argv[3]

    # get model
    model = pickle.load( open(model_path, 'rb') )

    # get_features
    df = pd.read_pickle(df_path)
    y = pd.read_pickle(y_path)

    features = np.array(df.columns.tolist())

    # Make same splits as training
    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.1, random_state=RANDOM_NUM)


    #make_feat_plot(model,features)


    #make_part_plot(model, features)

    #make_pred_plot(model, X_test, y_test)


    predicted_value_plot(model=model, df=df, column='number_topics', classification=False, discrete_col=False, freq=False, response_label='Subsrciber_Count', xlim=(3,23))
