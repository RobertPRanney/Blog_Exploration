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
###--------------------------------------------------------------------------###

# Import Section
import pandas as pd

# Constant Section
DF_BLOGS_UNCHANGED_PICKLE = 'blog_df_posts_unchanged.pkl'


# Function Section
def date_convert_w_error(date_string):
    """
    DESCR: to use in lambda date conversion to avoid wierd poor formatting errors that make pandas throw a fit, random date is then returned, this should only be used to avoid very uncommon errors.
    INPUT: date in string or unicode format
    OUTPUT: pandas date object
    """
    try:
        return pd.to_datetime(date_string)
    except:
        print "used error section"
        return pd.to_datetime('2015-01-04 10:10:10')


# Constant Section 2 (stuff down here was messing with atom text highlighting)
FITNESS_KEY_WORDS = ['run', 'ran', 'bike', 'bicycle', 'biking', 'marathon', 'race', '10K', 'endurance', 'swim', 'swam', 'boulder', 'climb', 'hike', 'backpack', 'mountain', 'hiking', 'lift', 'weight', 'wrestling', 'wrestle', 'crossfit', 'boxing', 'boxer', 'boxers', 'mud', 'obstacle', 'spartan', 'tough', 'sprint', 'track', 'field', 'football', 'basketball', 'baseball', 'soccer', 'lacrosse', 'tennis', 'golf', 'sports', 'player', 'diet', 'exercise', 'nutrition', 'workout', 'strength', 'balance', 'coordination', 'body', 'muscle', 'aerobic', 'walk', 'rugby', 'cricket', 'badminton', 'ski', 'snowboard', 'cardio', 'volleyball', 'cycling', 'triathlon', 'gymnastics', 'judo', 'ufc', 'rowing', 'equestrian', 'fencing', 'hockey', 'skating', 'curling', 'biathlon', 'dance', 'dancing', 'cheerleading', 'fence', 'conditioning', 'martial arts', 'treadmill', 'health', 'fitness']
