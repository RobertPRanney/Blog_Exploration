###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: get_all_blogs.py
# Description: pull all blogs given a list of domains to look at
# Usage: TBD
# Creation Date: 7/18/16
# Last Revision: 7/18/16
# Change Log:
#       7/18/16: file created, will try to get it to pull whole list, main isuse
#                currently is deciding on persistence method.
#       7/18/16: currently just going to presist each blog as a json txt file
#                this way it way be easy to transfer up to an s3 bucket and run
#                from an ec2 instance
###--------------------------------------------------------------------------###

# Import section
from wordpress_data_collection import get_blog_info, get_single_post, get_all_posts
import json
import pandas as pd
from time import time

# Constant Section
SAVE_PATH = 'wordpress_fitness_blogs/'
BLOG_URLS = 'blog_urls/wordpress_fitness_blog_domains.csv'
TEST_NUMBER = 10

# Function Section
def get_whole_blog(url):
    """
    DESCR: will grab a blog, and then if successful grab the associated posts
           all of this is put into json object and returned
    INPUT:
            url designating blog location
    OUTPUT:
            False if issue with blog retrival
            blog_info, json object with all blog info
    """
    # Attempt to get the blog info
    blog_response = get_blog_info(url)

    # Check error code before trying to get posts
    if blog_response.status_code == 200:
        blog_info = blog_response.json()
        blog_id = blog_info['ID']

        #Try to the the posts
        try:
            post_list = get_all_posts(blog_id, verbose=True)
            blog_info['post_list'] = post_list              #add to json
            return blog_info
        except:
            print "Error geeting posts for blog {}".format(blog_id)
            return False

    # Return False for any issuse
    else:
        print "Got bad response, code: {} for {}".format(blog_response.status_code, url)
        return False


def save_blog_to_json(path, blog_info):
    """
    DESCR: take blog info and dump it to a json object in a given path
    INPUT:
        path - string, path to storage location
        blog_info - json, json object about blog
    OUTPUT:
        True if no problems, False if problems
    """
    # Since ID is unique it makes a good file designator
    blog_id = blog_info['ID']

    try:
        with open(path + str(blog_id) + '.txt', 'w') as outfile:
            json.dump(blog_info, outfile)
        return True

    except:
        return False


def json_to_blog(path_to_file):
    """
    DESCR: recreates json object from persisted text file
    INPUT: path to text file
    """
    try:
        with open(path_to_file) as infile:
            blog_info = json.load(infile)

            return blog_info
    except:
        print "Problem opening {}".format(path_to_file)
        return False


if __name__ == '__main__':

    start_time = time()
    df = pd.read_csv(BLOG_URLS)

    df_small = df.iloc[ : TEST_NUMBER, : ]

    for dom in df_small['domain']:
        print "Getting info for {}".format(dom)
        blog_info = get_whole_blog(dom)

        # non empty dict/list thing is True
        if blog_info:
            save_blog_to_json(SAVE_PATH, blog_info)

    end_time = time()

    print "Took {} seconds to get {} blog docs".format(end_time - start_time, TEST_NUMBER)
