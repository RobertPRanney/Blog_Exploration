###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: data_cleaning.py
# Description: start of cleaning process, may not hold full pipeline
# Usage: tbd
# Creation Date: 7/20/16
# Last Revision: 7/21/16
# Change Log:
#      7/20/16: Rough file to store cleaning commands. May turn into part of
#               pipeline in the future. Currently makes df from mongdodb
#      7/21/16: started in on feature engineering in dataframe
###--------------------------------------------------------------------------###

# Import Section
from pymongo import MongoClient
import pandas as pd



client = MongoClient()          # Make Connection mongo
db = client['fitness_blogs_w_comments']    # specify db
coll = db['blogs']              # specify collection

test = coll.find()             # make a cursor object


df = pd.DataFrame(list(test))   # create dataframe from cursor

# Get rid of stuff that just has no chance of being useful
worthless = ['ID', '_id', 'visible', 'is_private', 'is_following']
df.drop(worthless, axis=1, inplace=True)







# New Features Section

    #Feature for length of domain portion
#df['url_length'] = df['URL'].apply(lambda x: len(x.split('.')[0]) - 8)

    #Is it someting.wordpress.com or just something.com
df['wordpress_in_url'] = df['URL'].apply(lambda x: 'wordpress.com' in x)

    #chars in blog name
df['len_blog_name'] = df['name'].apply(lambda x: len(x))

    #words in blog name
df['words_in_blog_name'] = df['name'].apply(lambda x: len(x.split()))
df.drop('name', axis=1, inplace=True)



# Stuff from post list
df['num_posts'] = df['post_list'].apply(lambda x: len(x))
df['start_date'] = df['post_list'].apply(lambda x: min([pd.to_datetime(post['modified']).date() for post in x]))
df['most_recent_date'] = df['post_list'].apply(lambda x: max([pd.to_datetime(post['modified']).date() for post in x]))






def stuff_to_post_list(list_of_posts):
    pass
