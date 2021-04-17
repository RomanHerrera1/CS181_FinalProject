s.
# We import Googles word2vec model. It contains over 3 million words.
# This import can take awhile.

import gensim.downloader as api
wv = api.load('word2vec-google-news-300')
