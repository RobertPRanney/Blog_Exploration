###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: grid_search_and_save_best.py
# Description: will hold a framework to run grid search and pickle on variety
#              of models, will allow choice of model and choice of cross
#              validation error metric
# Usage: python grid_search_and_save_best.py <model_name> <accuracy_score>
# Creation Date: 7/24/16
# Last Revision: 7/24/16
# Change Log:
#      7/24/16: file started
###--------------------------------------------------------------------------###

# Import Section
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import precision_recall_curve, confusion_matrix, roc_curve
import sys
import cPickle as pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import AdaBoostClassifier


# Constant Section
RANDOM_NUM = 42         # for reproducibility between files and runs


if __name__ == '__main__':
    # Usage python grid_search_and_save_best.py <model_name> <accuracy_score>
    model_name = sys.argv[1]
    score_name = sys.argv[2]

    # load in data and split for training
    post_df_w_nmf = pd.read_pickle('pickled_dfs/post_df_w_nmf.pkl')
    y = post_df_w_nmf.pop('success')
    target_names = np.array(['no traction', 'some traction', 'good traction', 'great traction'])


    #Remove columns that lead to data leakage if present
    try: post_df_w_nmf.drop('like_count', axis=1, inplace=True)
    except: pass
    try: post_df_w_nmf.drop('num_comments', axis=1, inplace=True)
    except: pass
    try: post_df_w_nmf.drop('success', axis=1, inplace=True)
    except: pass

    # Make splits
    X_train, X_test, y_train, y_test = train_test_split(post_df_w_nmf, y, test_size=0.1, random_state=RANDOM_NUM)


    # Model dict
    models = {'MultinomialNB': MultinomialNB(),
              'RandomForestClassifier': RandomForestClassifier(),
              'GradientBoostingClassifier': GradientBoostingClassifier(),
              'AdaBoostClassifier': AdaBoostClassifier(),
              'GaussianNB': GaussianNB()}

    # Param dicts
    params = {
              'MultinomialNB': {'alpha': [1.0, 0.7, 0.5, 0.3]},
              'RandomForestClassifier': {'n_estimators': [10, 25, 100],
                                         'criterion': ['gini', 'entropy'],
                                         'max_features': [None, 'sqrt']},
              'GradientBoostingClassifier': {'n_estimators': [50,100],
                                             'max_depth': [3, 9, None],
                                             'min_samples_split': [2, 25],
                                             'max_features': [None, 'sqrt']},
              'AdaBoostClassifier': {'n_estimators': [20, 50, 100],
                                     'learning_rate': [1.0, 0.5, 0.2]},
              'GaussianNB': {}
             }

    # Score dict
    scorers = {'accuracy_score': accuracy_score,
               'precision_score': precision_score,
               'recall_score': recall_score}


    # Make a scorer for GridSearchCV
    picked_scorer = make_scorer(scorers[score_name])

    # Build grid search object
    gridcv = GridSearchCV(estimator=models[model_name], param_grid=params[model_name], scoring=picked_scorer, n_jobs=1, verbose=5)

    # Perform grid search
    gridcv.fit(X=X_train, y=y_train)
    best_est = gridcv.best_estimator_

    # Pickle best model
    pickle.dump( best_est, open( 'pickled_models/' + model_name + '_' + score_name + '.pkl', "wb" ) )

    # Apeend results to tx as redundant backup
    with open('model_results.txt', 'a') as f:
        f.write("Model: {}, Score_used: {}, Score: {}, Params: {}\n\n".format(model_name, score_name, gridcv.best_score_, gridcv.best_params_))


    #roc_curve(y_true, y_score, pos_label=None, sample_weight=None, drop_intermediate=True)

    #precision_recall_curve(y_true, probas_pred, pos_label=None, sample_weight=None)
