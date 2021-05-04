
# We import Googles word2vec model. It contains over 3 million words.
# This import can take awhile.

import gensim.downloader as api
print("Loading in the model. Please give the computer at least 2 minutes. \n")
wv = api.load('word2vec-google-news-300')
print("Finished loading in the model.\n")