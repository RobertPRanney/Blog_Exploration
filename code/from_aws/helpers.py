import numpy as np
from wordcloud import WordCloud
import cPickle as pickle
import matplotlib.pyplot as plt
import sys

POST_TFIDF_PICKLE       = 'other_pickles/post_tfidf.pkl'
POST_NMF_PICKLE         = 'other_pickles/post_nmf.pkl'
W_MATRIX_PICKLE         = 'other_pickles/w_matrix.pkl'




def is_outlier(points, thresh=4.0):
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh


def make_word_cloud(topic_num, max_words=1000, width=10, height=10):
    post_nmf = pickle.load( open(POST_NMF_PICKLE) )
    post_tfidf = pickle.load( open(POST_TFIDF_PICKLE) )
    words = np.array(post_tfidf.get_feature_names())
    freq_sum = np.sum(post_nmf.components_[topic_num])
    frequencies = [val / freq_sum for val in post_nmf.components_[topic_num]]
    word_freq = zip(words, frequencies)


    wc = WordCloud(background_color='white')

    wc.fit_words(word_freq)


    #fig = plt.figure(figsize=(10,10))
    #ax = fig.add_subplot(111)
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
    return word_freq

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

if __name__ == '__main__':
    # Generate a wordcloud
    topic_num = int(sys.argv[1])
    test = make_word_cloud(topic_num)
