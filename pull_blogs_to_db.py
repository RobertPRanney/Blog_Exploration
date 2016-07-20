###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: pull_blogs_to_db.py
# Description: test mongo db creation and insertion on local machine
# Usage: python pull_blogs_to_db <all or number>
# Creation Date: 7/19/16
# Last Revision: 7/20/16
# Change Log:
#       7/19/16: for running on ec2 instance, pulls all blogs files into mongodb
#       7/20/16: exceptions now caught and written to error file. Size limit
#                checked with post call before collection. Change main block
#                to allow for picking the number of documents to pull or all.
#                size limits still hard coded, might change.
###--------------------------------------------------------------------------###
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CollectionInvalid
from get_all_blogs import get_whole_blog
from wordpress_data_collection import get_num_posts_byurl
from time import time, sleep
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import sys


# Constant Section
BLOG_URLS = 'blog_urls/wordpress_fitness_blog_domains.csv'
TEST_NUMBER = 100
BLOG_SIZE_MAX = 2500
BLOG_SIZE_MIN = 5

# Define a MongoDb database and table
db_client = MongoClient()
db = db_client['fitness_blogs']        # db name
table = db['blogs']                         # table(actually collection) name


def get_and_insert_doc(url):
    """
    DESCR: get a single blog object, insert into mongodb
    INPUT:
        url - string, domain of wordpress blog
    OUTPUT: none
    """
    try:
        length = get_num_posts_byurl(url)
        print length

        if length > BLOG_SIZE_MAX:
            print "Blog too big({}): {}".format(length, url)
            with open('errors.txt', "a") as f:
                f.write("Blog too big({}): {}\n".format(length, url))

        elif length < BLOG_SIZE_MIN:
            print "Blog too small({}): {}".format(length, url)
            with open('errors.txt', "a") as f:
                f.write("Blog too small({}): {}\n".format(length, url))

        # Ok its nots too big or too small, go ahead and get all of it
        else:
            blog_info = get_whole_blog(url)

            # Non empty blog object means success and is interpreted as True
            if blog_info:
                try:
                    blog_info['_id'] = blog_info['ID']  #to have specified key
                    table.insert(blog_info)
                except DuplicateKeyError:
                    print "ERROR: Duplicate error on insert of {}".format(blog_info['ID'])
                    with open('errors.txt', "a") as f:
                        f.write("ERROR: Duplicate error on insert of {}\n".format(url))
                except Exception as e:
                    print "ERROR: {} when inserting {}".format(str(e), blog_info['ID'])
                    with open('errors.txt', "a") as f:
                        f.write("ERROR: {} when inserting {}\n".format(str(e), url))

            else:
                with open('errors.txt', "a") as f:
                    f.write("ERROR: problem getting info on {}\n".format(url))

    except Exception as e:
        with open('errors.txt', "a") as f:
            f.write('problem with blog {} retrieval, exception: {}\n'.format(url, str(e)))



if __name__ == '__main__':
    # Read list to gather
    df = pd.read_csv(BLOG_URLS)

    # Determine amount of list to user
    if len(sys.argv) == 2 and sys.argv[1] == 'all':
        df_use = df
        print "Getting {} rows...\n".format(sys.argv[1])

    elif len(sys.argv) == 2:
        df_use = df.iloc[ : int(sys.argv[1]), : ]
        print "Getting {} rows...\n".format(sys.argv[1])

    else:
        df_use = df.iloc[ : TEST_NUMBER, : ]
        print "Getting {} rows...\n".format(TEST_NUMBER)

    # Pause to read message, and then start timer
    sleep(5)
    start_time = time()

    # Set up for threaded api query
    with ThreadPoolExecutor(max_workers=10) as executor:
        for num, dom in enumerate(df_use['domain']):
            executor.submit(get_and_insert_doc, dom)
            print "\n\n Blog {}: Getting info for {}".format(num, dom)

    end_time = time()


    print "\n\nTook {} seconds to get {} blog docs".format(end_time - start_time, TEST_NUMBER)
