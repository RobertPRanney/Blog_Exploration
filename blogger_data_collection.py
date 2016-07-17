###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: blog_data_collection.py
# Description: file to contain all necessary functionallity to retrieve blog
#              data and blog posts from google blogger api. Worth noting that
#              api is rate limited to 100 / 100  seconds and 10,000 per day
# Usage: TBD
# Creation Date: 7/12/16
# Last Revision: 7/12/16
# Change Log:
#       7/12/16: file created, function to pull blogs and post added
###--------------------------------------------------------------------------###

# Import Statements
import requests
import json
from time import time, sleep
import pandas as pd

# Constansts Section
BLOG_BY_URL = "https://www.googleapis.com/blogger/v3/blogs/byurl?url={}key={}"
POSTS_BY_ID = "https://www.googleapis.com/blogger/v3/blogs/{}/posts?key={}"

HOST        = "https://www.googleapis.com/blogger/"


# Get kes from json
with open('keys.json') as f:
     data = json.load(f)
     api_key = data['blogger_api_key']


# Functions Section
def get_a_blog_byurl(url):
    """
    DESCR: return a blog by providing a url.
    INPUT:
        url         - string, any url to a blog
    OUTPUT:
        blog_stuff  - Response, response object of api request
    """
    # specific endpoint for byurl api request
    endpoint = "v3/blogs/byurl"

    # public request but still needs api key
    params = {
        "url":url,
        "key":api_key
    }

    # get response
    blog_stuff = requests.get(HOST + endpoint, params=params)
    sleep(1)

    # avoid 100 / 100 secs api rate limit
    sleep(1)
    return blog_stuff

def get_a_blog_byid(id_num, get_posts=False, nums_posts=1000):
    """
    DESCR: return a blog by providing a id. Can also return all the information about posts, such as post ids. Is an option to get posts.
    INPUT:
        url         - string, any id to a blogspot blog
    OUTPUT:
        blog_stuff  - Response, response object of api request
    """
    # specific endpoint for byurl api request
    endpoint = "v3/blogs/{}".format(id_num)

    # public request but still needs api key
    params = {
        "key":api_key
    }

    # Add extra parameter to grab post information
    if get_posts:
        params['maxPosts']=nums_posts

    # get response
    blog_stuff = requests.get(HOST + endpoint, params=params)
    sleep(1)

    return blog_stuff

def get_all_posts(blog_id):
    """
    DESCR: Gets all the posts of a given blog id. Makes initial api request and continues request following the tokens returned by previous request
    INPUT:
        blog_id - string, specify blog id
    OUTPUT:
        all_posts - list, all post objects
    """
    # Posts will be returned as a list
    all_posts = []

    # Parameters needed for post query
    params = {
            'blogID':blog_id,
            'key':api_key,
            }

    # Proper Endpoint for posts query
    endpoint = "v3/blogs/{}/posts".format(blog_id)

    # Query for repsonse and wait
    posts_stuff = requests.get(HOST + endpoint, params=params)
    sleep(1)
    all_posts.extend(posts_stuff.json()['items'])

    # If posts are paginated follow the token to next page
    while 'nextPageToken' in posts_stuff.json().keys():
        params['pageToken'] = posts_stuff.json()['nextPageToken']   #Add token

        # Display infor for user
        print "{}, {}".format(posts_stuff.status_code, posts_stuff.json()['nextPageToken'])

        # Query and wait
        posts_stuff = requests.get(host + endpoint, params=params)
        sleep(1)
        all_posts.extend(posts_stuff.json()['items'])

    return all_posts


if __name__ == '__main__':



    hope = get_a_blog_byurl(test2)
    test_id = hope.json()['id']

    maybe = get_all_posts(test_id)
