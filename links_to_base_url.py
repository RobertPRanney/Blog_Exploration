###--------------------------------------------------------------------------###
# Author: Robert Ranney
# File: link_to_base_url.py
# Description: take csv of link_name and link. Process and only save the wanted
#              url portions. ie http://a_person_blog.blogpsot.com/post18 ==>
#              a_person_blog.blogspot.com. Also remove irrelevant stuff and
#              get rid of duplicates
# Usage: python link_to_base_url.py <in_file> <out_file>
# Creation Date: 7/15/16
# Last Revision: 7/15/16
# Change Log:
#       7/15/16: file created and test, only has one function but runs well
#                from command line to do its job.
###--------------------------------------------------------------------------###

# Import Section
import pandas as pd
import sys

# Constant Section
PROPER_USAGE    = "python link_to_base_url <in_file> <out_file>"

# Function Section
def csv_to_base_url(file_name, save_name, output_as='file', url_col='url_link', verbose=False):
    """
    DESCR: take a stored csv of and find the set of base urls
    INPUT:
        file_name - string, path to file location
        save_name - string, path to save file to
        output_as - string, type of output, options are list, or csv
        verbose   - bool, whether to output info about file
    OUTPUT:
        list      - returns a list of domains
        file      - csv of unique domains with number of urls with that domain
    """
    # Read in the data
    df = pd.read_csv(file_name)

    # Drop na rows
    if verbose:
        print "   Droping {} rows".format(df.shape[0] - df.dropna().shape[0])
    df.dropna(inplace=True, axis=0)

    # Make a new row with just domain value
    # 'http://domain.com/stuff' ==> ['http:', '', 'domain.com', 'stuff']
    df['domain'] = df[url_col].apply(lambda x: x.split('/')[2])

    # Turn df into |domian | counts_with_domain|
    df = df.groupby('domain').count()
    df.reset_index(inplace=True)
    df.drop('link_name', axis=1, inplace=True)
    df.rename(columns={'url_link': 'url_count'}, inplace=True)

    # Output the result of reduction
    if verbose:
        print "   Of {}, urls, their were {} unique domains".format(sum(df['url_count']), df.shape[0])

    # Reutrn list to user if that was parameter given
    if output_as == 'list':
        return df['domain'].tolist()

    # Save results to file for given name
    elif output_as == 'file':
        try:
            df.to_csv(save_name, index=False)
            if verbose:
                print "   Reults writing to {}".format(save_name)
        except:
            print "   ERROR: problem writing results to {}".format(save_name)


if __name__ == '__main__':
    # Check for proper number of arguments
    if len(sys.argv) != 3:
        print "   ERROR: {}".format(PROPER_USAGE)

    # Attempt to process given csv file
    else:
        in_file = sys.argv[1]
        out_file = sys.argv[2]

        try:
            f = open(in_file, 'r')
            f.close()
        except:
            print "   ERROR: problem opening file {}".format(in_file)
            sys.exit(-1)

        csv_to_base_url(file_name=in_file,
                        save_name=out_file,
                        output_as='file',
                        url_col='url_link',
                        verbose=True)
