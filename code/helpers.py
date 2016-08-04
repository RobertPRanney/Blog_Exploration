###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: helpers.py
# Description: holds some helper constants, some word lists and a few accessory
#              functions that find useage in multiple places
# Usage: tbd
# Creation Date: 7/23/16
# Last Revision: 7/23/16
# Change Log:
#      7/23/16: file created, some functions reloavted here from other files
#      7/27/16: added some stop words that are crap that is making its way to
#               the topic descriptions.
###--------------------------------------------------------------------------###

# Import Section
import pandas as pd
from sklearn.decomposition import NMF
from string import punctuation
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

# Constant Section
DF_BLOGS_UNCHANGED_PICKLE = 'blog_df_posts_unchanged.pkl'
EXTRA_STOP_WORDS = ['', '2px', 'text-align', '10px', 'gallery-caption', 'margin-top', 'gallery_shortcode', 'gallery-item', 'margin-left', 'cfcfcf', 'wp-includes/media.php', 'img', 'got']
STOP_WORDS = stopwords.words('english')
STOP_WORDS.extend(EXTRA_STOP_WORDS)


# Function Section
def date_convert_w_error(date_string):
    """
    DESCR: to use in lambda date conversion to avoid wierd poor formatting errors that make pandas throw a fit, random date is then returned, this should only be used to avoid very uncommon errors.
    INPUT: date in string or unicode format
    OUTPUT: pandas date object
    """
    try:
        return pd.to_datetime(date_string).date()
    except:
        print "used error section"
        return pd.to_datetime('2015-01-04 10:10:10').date()

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


def tokenize_content(content):
    """
    DESCR: takes a big string, makes all lower, splits on ws, and strip junk to give backa nice tokenized list of words, may have to keep adding, also remove stop words
    INPUT: string
    OUTPUT: list of tokens
    """
    # Get rid of all punctuation, lowercase words, and split on ws
    tokens = [word.strip().strip(punctuation) for word in content.lower().split()]


    # remove stop words
    tokens = [word for word in tokens if word not in STOP_WORDS]

    # lemmatize tokens
    lemmer = WordNetLemmatizer()
    tokens = [lemmer.lemmatize(token) for token in tokens]
    return tokens


# Constant Section 2 (stuff down here was messing with atom text highlighting)
FITNESS_KEY_WORDS = ['run', 'ran', 'bike', 'bicycle', 'biking', 'marathon', 'race', '10K', 'endurance', 'swim', 'swam', 'boulder', 'climb', 'hike', 'backpack', 'mountain', 'hiking', 'lift', 'weight', 'wrestling', 'wrestle', 'crossfit', 'boxing', 'boxer', 'boxers', 'mud', 'obstacle', 'spartan', 'tough', 'sprint', 'track', 'field', 'football', 'basketball', 'baseball', 'soccer', 'lacrosse', 'tennis', 'golf', 'sports', 'player', 'diet', 'exercise', 'nutrition', 'workout', 'strength', 'balance', 'coordination', 'body', 'muscle', 'aerobic', 'walk', 'rugby', 'cricket', 'badminton', 'ski', 'snowboard', 'cardio', 'volleyball', 'cycling', 'triathlon', 'gymnastics', 'judo', 'ufc', 'rowing', 'equestrian', 'fencing', 'hockey', 'skating', 'curling', 'biathlon', 'dance', 'dancing', 'cheerleading', 'fence', 'conditioning', 'martial arts', 'treadmill', 'health', 'fitness']
