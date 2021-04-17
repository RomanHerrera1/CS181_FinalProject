#
# Final Project    ~~ CS 181 Spring 2021
#

#
# Collaborators: Roman Herrera, Kobe Lin, Valentina Vallalta, Alina Saratova
#

# our libraries
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
sns.set(style="darkgrid")
import nltk
import textblob
import pandas as pd
from textblob import Word
from textblob.wordnet import VERB
from textblob.wordnet import Synset
from textblob import TextBlob
from gensim.models import KeyedVectors
from gensim import matutils 
import random
from itertools import combinations

# print("Before")
from codenames_library import wv
# print("After")

def guess_words_given_clue(clue, board, model): 
  """ 
  This function guesses which words are associated with a clue using word2vec model.

  Inputs: 
  - clue is a tuple that contains a one word string and an integer that
    is the number of words associated with the clue in the format (clueword, n)
  - board is the current words on the board
  - model is the word2vec model used for the guessing
  
  Outputs:
  - a list of n number of words as guesses based on the clue in highest probability
  """
  word, num_words = clue
  rank = []

  # Checks to see if the clue word is in the model
  if word not in model:
    print(f"AHH the word {word} is not in the model. Try a different clue for me.")
    return []
  
  # Iterates through each word in the board and adds each tuple
  # of the similarity_score from the similarity function and
  # its corresponding_word to our rank list
  for word in board:
    score = wv.similarity(clue, word)
    rank.append((score,word))

  # Sort the list in descending score
  rank = sorted(rank, reverse=True)
  return rank[0:num_words]


def score_clue(clue, board, intended, model):
  """
  Calls guess_words_given_clue() to give a rating of how well the intended
  words ranked

  Inputs:
  - clue is a tuple that contains a one word string and an integer that
    is the number of words associated with the clue in the format (clueword, n)
  - board is the current words on the board as a list
  - intended is a list of words on the board that were meant to go with the clue

  Outputs:
  - A score of how well the clue is
  """

  clueword, num_words = clue
  rank = guess_score_given_clue((clueword, 25), board, model)
  indices = []
  for i in range(0, len(rank)): # rank is (score, word)
    if rank[i][1] in intended:
      indices.append((i,rank[i][0]))
      
    # can also check how well assassin and other team words ranked
      


def give_clue(own_words, model, opponent_words = [], neutral_words = [], assassin_word = []):
  """
  Given a team color and a board, it will use the word2vec model to return a valid clue
  using various heuristics

  Inputs:
  - own_words is the list of your team's words
  - opponent_words is words your other team has
  - neutral_words are gray words, but we still don't want our team to select those
  - asssasin_word is the assassin word
  - model is the word2vec model used for the guessing

  Output:
  - A clue is a tuple that contains a one word string and an integer that
    is the number of words associated with the clue in the format (clueword, n)
  - valid_combo is the words intended to be guesses, written as a list of strings
  """

  valid_combo = []
  num_words = 0
  max_score = 0
  clueword = ""

  if len(own_words) == 1:
    word, score = first_valid_word([own_words[0]], model.most_similar(positive=[own_words[0]], topn=100))
    return word
  
  for i in range(min(5, len(own_words)), 1, -1):
      comb = combinations(own_words, i)
      for combo in comb:
        word, score = first_valid_word(combo, model.most_similar(positive=[combo], topn=100))
        word2, score2 = first_valid_word([word.lower() for word in combo], model.most_similar(positive=[combo], topn=100))
  
        if score2 > score:
          score = score2
          word = word2
          
        # MAY NEED TO CHANGE SCORE SYSTEM
        if (score * i/2) > max_score:
          max_score = score
          num_words = i
          valid_combo = combo
          clueword = word

  return (clueword, len(valid_combo)), valid_combo


def does_not_share(a, b):
  """ 
  helper function that checks that string a has no characters from string b 
  """
  for i in a:
    if i in b:
      return False
  return True


def first_valid_word(words, similar_words, threshold = 0.6):
  """ 
  helper function that returns the first word that 
  fits the qualifications for a clue and its score
  """
  do_not_put = "0123456789!_?*&"
  for clue_word in similar_words:
    if clue_word[1] > threshold:
      curr = clue_word[0]

      words_not_in_curr = True
      for word in words:
        if word in curr:
          words_not_in_curr = False  
      
      if words_not_in_curr and (curr not in words) and does_not_share(curr, do_not_put):
        return clue_word
  return (None, 0)


# Function given from Prof. Dodds :)
def make_codenames_guess( clue, LoW, m ):
    """
        m == word-vector model from somewhere!
        LoW == any list of words (strings)
        clue == a single word (string) 
    """
    if clue not in m:
        print(f"the clue {clue} wasn't in the model!")
        return []
    
    LoS = []  # list of scores
    for word in LoW:
        if word not in m:
            print(f"the word {word} wasn't in the model! Skipping...")
            continue
        score = m.distance( clue, word )
        LoS = LoS + [ (score,word) ]
    return LoS

def generate_board(model):
  """
  Generates random valid player boards and spymaster boards and returns them

  Input:
  - model is a word2vec model that is checked to see
    if the words chosen exist in the model

  Output:
  - player_board is a list of strings which represents the board of words
  - spymaster_board is a list of tuples (word, type) which represents the
    board of words with the type of each word
    (such as whether the word is red, blue, bystander, assassin)
  - first is a string saying which team (red or blue) is going first
  """
  
  # let's read in our word data...
  filename = 'Wordlist.csv'
  df = pd.read_csv(filename, header=None)   # encoding="latin1" et al.
  print(f"{filename} : file read into a pandas dataframe.")

  # Convert to a numpy array
  A = df.values

  # Initialize lists and values
  player_board = []
  player_edit_board = []
  spymaster_board = []
  not_valid = []
  num_red = 0
  num_blue = 0
  num_bystander = 7
  num_assassin = 1
  first = ""

  # Randomly determines which team gets the extra card and goes first
  if random.randint(0,1) == 1:
      num_red = 9
      num_blue = 8
      first = "red"
  else:
      num_red = 8
      num_blue = 9
      first = "blue"

  options = ["red"] * num_red + ["blue"] * num_blue +\
    ["bystander"] * num_bystander + ["assassin"] * num_assassin

  # Repeat until the board is completely filled up
  while len(player_board) < 25:
      rand_card = list(random.choice(A))
      word1 = rand_card[0]
      word2 = rand_card[1]

      # Checks to see if the given card was already used or is not in the model
      if (rand_card not in not_valid) and (word1 in model) and (word2 in model):
          
          # Adds the chosen card to the list of used cards
          not_valid.append(rand_card)
          rand_word = rand_card[random.randint(0, 1)]
          
          # Adds the random word to the player board
          player_board.append(rand_word)
          player_edit_board.append((rand_word, ""))

          
          # Adds the random word to the spymaster board with a "team" attached and removes that option from options
          rand_option = random.choice(options)
          spymaster_board.append((rand_word, rand_option))
          options.remove(rand_option)
  return player_board, spymaster_board, first, player_edit_board

def display_player_board(board):
  formatting = len(max(board, key=len))
  print("-"*((formatting+2)*5))
  counter = 0
  for i in range(0,5):
    builder = ""
    for j in range(0,5):
      word = board[counter]
      temp = formatting - len(word)
      word = " "*((temp//2)+temp%2) + word + " "*((temp//2))
      builder += "|"+word+"|"
      counter+=1
    print(builder)
    print("-"*((formatting+2)*5))

def display_spymaster_board(playerboard, spymasterboard):
  board = playerboard + ["bystander", "red", "blue", "assassin"]
  formatting = len(max(board, key=len))
  print("-"*((formatting+2)*5))
  for i in range(0,5):
    builder1 = ""
    builder2 = ""
    for j in range(0,5):
      word = spymasterboard[j+i*5][0]
      label = spymasterboard[j+i*5][1]
      temp_word = formatting - len(word)
      temp_label = formatting - len(label)
      word = " "*((temp_word//2)+temp_word%2) + word + " "*((temp_word//2))
      label = " "*((temp_label//2)+temp_label%2) + label + " "*((temp_label//2))
      builder1 += "|"+word+"|"
      builder2 += "|"+label+"|"
    print(builder1)
    print(builder2)
    print("-"*((formatting+2)*5))


if __name__ == '__main__':
  
  player, spymaster, first, player_edit = generate_board(wv)

  #print(player)
  #print(player_edit)
  #print(spymaster)
  #print(first)

  #display_player_board(player)
  display_spymaster_board(player, player_edit)
  #display_spymaster_board(player, spymaster)

  # clue = ("suit", 2)
  # LoW = [ "armor", "spring", "romans", "tuxedo" ]
  # m = m  # defined in another cell
  # LoS = make_codenames_guess( clue, LoW, m )
  # for pair in LoS:
  #     print(f"{pair}")
