###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: blog_data_collection.py
# Description: file to contain all necessary functionallity to retrieve blog
#              data and blog posts from google blogger api. Worth noting that
#              api is rate limited to 100 / 100  seconds and 10,000 per day
# Usage: TBD
# Creation Date: 7/17/16
# Last Revision: 7/17/16
# Change Log:
#       7/17/16: file created, trying to replicate functionality from blogger
#                blogs to wordpress blogs
#       7/18/16: can fetch blog info and all posts, testing code added
###--------------------------------------------------------------------------###

# Import Statements
from __future__ import division
import requests
import json
from time import time, sleep
import pandas as pd
import sys

# Constansts Section
HOST            = "https://public-api.wordpress.com/rest/v1.1/"
SLEEP_DELAYS    = 0.2

# Functions Section
def get_blog_info(url_or_id):
    """
    DESCR: return a blog by providing a url.
    INPUT:
        url         - string, any url to a blog
    OUTPUT:
        blog_stuff  - Response, response object of api request
    """
    # specific endpoint for byurl api request
    endpoint = "sites/{}/".format(url_or_id)

    # public request but still needs api key
    params = {
    }

    # get response
    blog_stuff = requests.get(HOST + endpoint)
    sleep(1)

    # no known limit currently, but will keep anyways
    sleep(1)
    return blog_stuff


def get_single_post(site_id, post_id):
    """
    DESCR: grabs a single post given a blog idea and post idea
    INPUT:
        site_id     - int, unique number for site
        posst_id    - int, unique post id for given site
    OUTPUT:
        single_post - response, results of query
    """
    endpoint = "sites/{}/posts/{}".format(site_id, post_id)
    single_post = requests.get(HOST + endpoint)
    sleep(SLEEP_DELAYS)

    # Display info for user
    print "got {} for post {}".format(single_post.status_code, post_id)

    return single_post


def get_all_posts(blog_id, verbose=False):
    """
    DESCR: Gets all the posts of a given blog id. Makes initial api request and continues request following the tokens returned by previous request
    INPUT:
        blog_id - string, specify blog id
    OUTPUT:
        all_posts - list, all post objects
    """
    # build a list of all post objects
    all_posts = []

    # Parameters needed for post query
    params = {
    }

    # Proper Endpoint for posts query
    endpoint = "sites/{}/posts/".format(blog_id)

    # Query for repsonse and wait
    posts_stuff = requests.get(HOST + endpoint, params=params)
    sleep(SLEEP_DELAYS)
    try:
        all_posts.extend(posts_stuff.json()['posts'])
    except:
        print "Problem with intial query to blog: {}".format(blog_id)

    # Generate a list of all the blogspost ids by following object links
    while 'next_page' in posts_stuff.json()['meta'].keys():
        params['page_handle'] = posts_stuff.json()['meta']['next_page']

        # Display info for user
        if verbose:
            print "{}, {}".format(posts_stuff.status_code, posts_stuff.json()['meta']['next_page'])

        # Query and wait
        posts_stuff = requests.get(HOST + endpoint, params=params)
        sleep(SLEEP_DELAYS)
        try:
            all_posts.extend(posts_stuff.json()['posts'])
        except:
            print "Problem with subsequent query to blog: {}".format(blog_id)

    return all_posts


if __name__ == '__main__':
    # for time being code will only be run on import, not from command line
    # code here is simple for ipython testing, and exploration
    test_url = 'datascience101.wordpress.com'

    response = get_blog_info(test_url)

    print "Quering google for a blog with url: {}\n".format(test_url)
    print "   Got back a response with code {}".format(response.status_code)
    print "   This also contains json object about the blog, keys are {}".format(response.json().keys())

    for key in response.json().keys():
        print "   The key({}) contians: {}".format(key, response.json()[key])

    test_id = response.json()['ID']

    print "The most inmportant piece from this is the blog id: {}".format(test_id)

    print "From this comes all the posts"

    test_posts = get_all_posts(test_id, verbose=True)

    print "There are {} posts".format(len(test_posts))
    print "Each post has {}".format(test_posts[0].keys())

    print "Post 0:"
    for key in test_posts[0].keys():
        print "   key({}) holds: {}".format(key, test_posts[0][key])
