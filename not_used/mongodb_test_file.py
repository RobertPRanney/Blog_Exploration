###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: mongobd_test_file.py
# Description: test mongo db creation and insertion on local machine
# Usage: python mongodb_test_file
# Creation Date: 7/19/16
# Last Revision: 7/19/16
# Change Log:
#       7/19/16: get three blogs, one is a duplicate to make sure it doesn't
#                insert
###--------------------------------------------------------------------------###
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CollectionInvalid
from get_all_blogs import get_whole_blog


# Define a MongoDb database and table
db_client = MongoClient()
db = db_client['data_science_blogs']        # db name
table = db['blogs']                         # table(actually collection) name


def test_insert_docs():
    """
    DESCR: gets three blogs, and then inserts, third is a duplicate to test key
           error.
    INPUT: none
    OUTPUT: none
    """
    test1_url = 'randomjohn.wordpress.com'
    test2_url = 'hollyfitness.wordpress.com'
    test3_url = 'randomjohn.wordpress.com'

    stuff = [test1_url, test2_url, test3_url]

    # Get all blogs
    for url in stuff:
        blog_info = get_whole_blog(url)

        # If it works insert
        if blog_info:
            try:
                blog_info['_id'] = blog_info['ID']  #to have specified key
                table.insert(blog_info)
            except DuplicateKeyError:
                print "ERROR: Duplicate error on insert of {}".format(blog_info['ID'])
            except:
                print "ERROR: unknown insert error of {}".format(blog_info['ID'])
        else:
            print "ERROR: Problem get blog for url: {}".format(url)


if __name__ == '__main__':
    test_insert_docs()
