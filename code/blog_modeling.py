###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: blog_modeling.py
# Description: functions similar to post modeling. Provides a framework for
#              generating models on
# Usage: python blog_modeling.py <model_name> <accuracy_score>
# Creation Date: 7/27/16
# Last Revision: 7/27/16
# Change Log:
#      7/27/16: file started
###--------------------------------------------------------------------------###

# Import Section
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.metrics import precision_recall_curve, confusion_matrix, roc_curve
import sys
import cPickle as pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import AdaBoostRegressor
from sklearn.linear_model import LinearRegression


# Constant Section
RANDOM_NUM              = 42     # for reproducibility between files and runs
BLOG_DF_CATEGORIZED     = 'pickled_dfs/blog_df_posts_categorized.pkl'


if __name__ == '__main__':
    # Usage python grid_search_and_save_best.py <model_name> <accuracy_score>
    model_name = sys.argv[1]
    score_name = sys.argv[2]

    # load in data and split for training
    blog_df = pd.read_pickle(BLOG_DF_CATEGORIZED)
    blog_df.drop(['likts_history', 'comment_history', 'post_topics', 'start_date', 'most_recent_date'], axis=1, inplace=True)

    # pop off target column
    y = blog_df.pop('subscribers_count')

    # Make splits
    X_train, X_test, y_train, y_test = train_test_split(blog_df, y, test_size=0.1, random_state=RANDOM_NUM)


    # Model dict
    models = {'RandomForestRegressor': RandomForestRegressor(),
              'GradientBoostingRegressor': GradientBoostingRegressor(),
              'AdaBoostRegressor': AdaBoostRegressor(),
              'LinearRegression': LinearRegression()}

    # Param dicts
    params = {'RandomForestRegressor': {'n_estimators': [10, 25, 100],
                                        'max_depth': [5, 10, 25, 50],
                                         'max_features': [None, 'sqrt']},
              'GradientBoostingRegressor': {'n_estimators': [50,100],
                                             'max_depth': [3, 9, None],
                                             'min_samples_split': [2, 25],
                                             'max_features': [None, 'sqrt'],
                                             'subsample': [1.0, 0.5]},
              'AdaBoostRegressor': {'n_estimators': [20, 50, 100],
                                    'learning_rate': [1.0, 0.5, 0.2],
                                    'loss': ['linear', 'square', 'exponential']},
              'LinearRegression': {'fit_intercept': [True, False],
                                   'normalize': [True, False]}
             }

    # Score dict
    scorers = {'r2_score': r2_score,
               'mean_squared_error': mean_squared_error}


    # Make a scorer for GridSearchCV
    picked_scorer = make_scorer(scorers[score_name])

    # Build grid search object
    gridcv = GridSearchCV(estimator=models[model_name], param_grid=params[model_name], scoring=picked_scorer, n_jobs=1, verbose=5)

    # Perform grid search
    gridcv.fit(X=X_train, y=y_train)
    best_est = gridcv.best_estimator_

    # Pickle best model
    pickle.dump( best_est, open( 'from_aws/blog_pickled_models/' + model_name + '_' + score_name + '.pkl', "wb" ) )

    # Apeend results to tx as redundant backup
    with open('from_aws/blog_models_results.txt', 'a') as f:
        f.write("Model: {}, Score_used: {}, Score: {}, Params: {}\n\n".format(model_name, score_name, gridcv.best_score_, gridcv.best_params_))


    #roc_curve(y_true, y_score, pos_label=None, sample_weight=None, drop_intermediate=True)

    #precision_recall_curve(y_true, probas_pred, pos_label=None, sample_weight=None)
