###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: blog_data_collection.py
# Description: file to contain all necessary functionallity to retrieve blog
#              data and blog posts from google blogger api. As far as I can
#              tell there is no kind of limiting in place, but will be cautsious
#              just in case.
# Usage: import functionally to other scripts, main is just test code
# Creation Date: 7/17/16
# Last Revision: 7/21/16
# Change Log:
#       7/17/16: file created, trying to replicate functionality from blogger
#                blogs to wordpress blogs
#       7/18/16: can fetch blog info and all posts, testing code added
#       7/20/16: aggregates strange dicts in post object that were causing key
#                errors for mongo. Bunch of garbage in those anyways, hopefully
#                no real info lost.
#       7/21/16: Now fetches comments, as a list of comment content in a post
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
SLEEP_DELAYS    = 0.1

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
    sleep(SLEEP_DELAYS)

    # no known limit currently, but will keep anyways
    sleep(SLEEP_DELAYS)
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


def get_num_posts_byurl(blog_url):
    response = get_blog_info(blog_url)
    try:
        blog_id = response.json()['ID']
        return get_num_posts_byid(blog_id)
    except:
        return 0


def get_num_posts_byid(blog_id):
    """
    DESCR: finds the number of posts in a blog and returns it, some of these sites have thousands of posts, so they don't eve seem blog like anymore
    INPUT:
        blog_id     - int, unique to blog
    OUTPUT:
        num   - int, posts number returned from query
    """
    # Parameters needed for post query
    params = {
    }

    endpoint = "sites/{}/posts/".format(blog_id)
    posts_stuff = requests.get(HOST + endpoint, params=params)
    sleep(SLEEP_DELAYS)

    try:
        num = posts_stuff.json()['found']
    except:
        num = 0

    return num


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

    # This dictionary is a garbage mess of links, and it causes way to manny errors during mongodb insertion, better to just aggregate to a number
    for post in all_posts:
        post['tags'] = post['tags'].keys()
        post['terms'] = post['terms'].keys()
        post['categories'] = post['categories'].keys()
        post['attachments'] = post['attachments'].keys()


    # Now retrieve comments for posts
    for post in all_posts:
        post['comments'] = get_all_comments(blog_id, post['ID'])

    return all_posts


def get_all_comments(blog_id, post_id):
    """
    DESCR: Gets all comments for given blog_id and post_id
    INPUT:
        blog_id - string, specify blog id
        post_id - string, unique num
    OUTPUT:
        comments - list, content of all comments, rest tossed
    """
    # Parameters needed for post query
    params = {
              'number':100
    }

    # Proper Endpoint for posts query
    endpoint = "sites/{}/posts/{}/replies/".format(blog_id, post_id)

    # Query for repsonse and wait, build list of comments
    try:
        comment_stuff = requests.get(HOST + endpoint, params=params)
        sleep(SLEEP_DELAYS)

        if comment_stuff.json()['found'] == 0:
            return []

        comments = [comment['content'] for comment in comment_stuff.json()['comments']]
    except:
        print "Problem with intial query to blog: {} for comments".format(blog_id)
        return []

    return comments



if __name__ == '__main__':
    # for time being code will only be run on import, not from command line
    # code here is simple for ipython testing, and exploration
    test_url = 'jasetagle.wordpress.com'

    response = get_blog_info(test_url)

    print "Quering wrodpress for a blog with url: {}\n".format(test_url)
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
