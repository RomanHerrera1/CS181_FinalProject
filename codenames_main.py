#
# Final Project    ~~ CS 181 Spring 2021
#

#
# Collaborators: Roman Herrera, Kobe Lin, Valentina Vallalta, Alina Saratova
#

# our libraries
import numpy as np
# import matplotlib.pyplot as plt 
# import seaborn as sns
# sns.set(style="darkgrid")
# import nltk
# import textblob
import pandas as pd
# from textblob import Word
# from textblob.wordnet import VERB
# from textblob.wordnet import Synset
# from textblob import TextBlob
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
  num_words = int(num_words)
  rank = []

  # Checks to see if the clue word is in the model
  if word not in model:
    print(f"AHH the word {word} is not in the model. Try a different clue for me.")
    return []
  
  # Iterates through each word in the board and adds each tuple
  # of the similarity_score from the similarity function and
  # its corresponding_word to our rank list
  for word_type in board:
    if word_type[1] == "":
      potential_guess = word_type[0]
      score = wv.similarity(potential_guess, word)
      rank.append((score, potential_guess))

  # Sort the list in descending score
  rank.sort(reverse=True)

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
      
used_clues = []     
def give_clue(own_words, model, opponent_words = [], neutral_words = [], assassin_word = ""):
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

  print("Please hold as the computer thinks of a clue. (May take up to 1 min)\n")
  global used_clues

  min_size = 1

  valid_combo = []
  num_words = 0
  max_score = .5
  clueword = ""
  
  # back up clue just in case function has no clue
  emergency_combo = []
  emergency_num_words = 0
  emergency_max_score = 0.01
  emergency_clueword = ""
  
  
  # If there is only 1 remaining word, just use the most similar word to the last word
  if len(own_words) == 1:
    word, score = first_valid_word([own_words[0]], model.most_similar(positive=[own_words[0]], topn=100))
    return (word, 1), own_words[0]
  
  if len(own_words) <= 2:
    min_size = 0
    
  for i in range(min(3, len(own_words)), min_size, -1):
    comb = combinations(own_words, i)
    for combo in comb:
      word, score = first_valid_word(combo, model.most_similar(positive=list(combo), topn=100))
        
      # TODO: CHANGE SCORING SYSTEM
      
      # Checks to see if new similarity score is better than the previous.
      # Slightly favors clues that hint at more words
      if (score + i * 0.01) > emergency_max_score:
        emergency_max_score = score + i * 0.01
        emergency_num_words = i
        emergency_valid_combo = combo
        emergency_clueword = word

      if (score + i * 0.01) > max_score:
                 
        #print(f"This is the word: {word}. This is the score: {score}. What combo? : {combo}")
        bad_clue = False

        # we want our emergency words to not be related to the assassin
        if word in used_words:
          continue

        if assassin_word != "" and wv.similarity(word, assassin_word) > 0.7:
          #print(f"{word} is too similar to the assassin")
          continue   # clue doesn't work
        
        if opponent_words is not []:
          for bad_word in opponent_words:
            if wv.similarity(word, bad_word) > 0.73:
              #print(f"{word} is too similar to {bad_word}")
              bad_clue = True # clue doesn't work
              break
            
          if bad_clue == True: # the clue is too related to one of the opponent words 
            continue
          
        # Goes through neutral words to see if they are too related to the clue   
        if neutral_words is not []:
          for neutral_word in neutral_words:
            if wv.similarity(word, neutral_word) > 0.75:
              #print(f"{word} is too similar to {neutral_word}")
              bad_clue = True   # clue doesn't work
              break

          if bad_clue == True: # the clue is too related to one of the neutral words 
            continue

        # clue works so we update it
        # print("Was a successful clue!")
        max_score = score + i * 0.01
        num_words = i
        valid_combo = combo
        clueword = word

  if clueword == "":
    # if emergency_clueword == "":
    #   rand_word = random.choice(own_words)
    #   combo = [rand_word]
    #   word, score = first_valid_word(combo, model.most_similar(positive=combo, topn=100))

    #   print(f"rand_word: {rand_word}. Combo: {combo}. word: {word}. score:{score}")
    #   return (word, 1), combo
    print("There were no clear clues. Here's an emergency clue.")
    used_word.append(emergency_clueword)
    return (emergency_clueword, len(emergency_valid_combo)), emergency_valid_combo

  used_words.append(clueword)
  return (clueword, len(valid_combo)), valid_combo

def does_not_share(a, b):
  """ 
  helper function that checks that string a has no characters from string b 
  """
  for i in a:
    if i in b:
      return False
  return True

def first_valid_word(gamewords, similar_words, threshold = 0.5):
  """ 
  helper function that returns the first word that 
  fits the qualifications for a clue and its score
  """
  do_not_put = "0123456789!_?*& "
  for clue_word in similar_words:
    if clue_word[1] > threshold:
      curr = clue_word[0]
      curr.lower()

      words_not_in_curr = True
      for word in gamewords:
        word.lower()
        if (word in curr) or (curr in word):
          words_not_in_curr = False 
          break 
      
      if words_not_in_curr and does_not_share(curr, do_not_put):
        return clue_word
  return (None, 0)

def generate_board(model):
  """
  Generates random valid player boards and spymaster boards and returns them

  Input:
  - model is a word2vec model that is checked to see
    if the words chosen exist in the model

  Output:
  - gamewords is a list of strings which represents the board of words
  - spymaster_board is a list of tuples (word, type) which represents the
    board of words with the type of each word
    (such as whether the word is red, blue, bystander, assassin)
  - first is a string saying which team (red or blue) is going first
  - player_edit_board is a list of tuples (word, ) which represents the unedited board
  """
  
  # let's read in our word data...
  filename = 'Wordlist.csv'
  df = pd.read_csv(filename, header=None)   # encoding="latin1" et al.
  # print(f"{filename} : file read into a pandas dataframe.")

  # Convert to a numpy array
  A = df.values

  # Initialize lists and values
  gamewords = []
  player_edit_board = []
  spymaster_board = []
  not_valid = []
  num_red = 0
  num_blue = 0
  num_bystander = 7
  num_assassin = 1
  first = ""
  second = ""

  # Randomly determines which team gets the extra card and goes first
  if random.randint(0,1) == 1:
      num_red = 9
      num_blue = 8
      first = "red"
      second = "blue"
  else:
      num_red = 8
      num_blue = 9
      first = "blue"
      second = "red"

  options = ["red"] * num_red + ["blue"] * num_blue +\
    ["bystander"] * num_bystander + ["assassin"] * num_assassin

  # Repeat until the board is completely filled up
  while len(gamewords) < 25:
      rand_card = list(random.choice(A))
      word1 = rand_card[0]
      word2 = rand_card[1]

      # Checks to see if the given card was already used or is not in the model
      if (rand_card not in not_valid) and (word1 in model) and (word2 in model):
          
          # Adds the chosen card to the list of used cards
          not_valid.append(rand_card)
          rand_word = rand_card[random.randint(0, 1)]
          
          # Adds the random word to the player board
          gamewords.append(rand_word)
          player_edit_board.append((rand_word, ""))

          
          # Adds the random word to the spymaster board with a "team" attached and removes that option from options
          rand_option = random.choice(options)
          spymaster_board.append((rand_word, rand_option))
          options.remove(rand_option)
  return gamewords, spymaster_board, player_edit_board, first, second

def display_gamewords(board):
  """
  """
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

def display_board_color_player(gamewords, board):
  """
  Prints out a given board, can be player board or spymaster board
  """
  gamewords = gamewords + ["bystander", "red", "blue", "assassin"]
  formatting = len(max(gamewords, key=len))
  lines = "-"*((formatting+2)*5)
  print(f"\033[1;37;40m{lines}")
  for i in range(0,5):
    #printint words all in one line
    for j in range(0,5):
      n = "" #color variable
      label = board[j+i*5][1] 
      if label == "red":
        n = "31"
      elif label == "blue":
        n = "34"
      elif label == "assassin":
        n = "35"
      elif label == "bystander":
        n = "33"
      else:
        n = "37"

      word = board[j+i*5][0]
      temp_word = formatting - len(word)
      word = " "*((temp_word//2)+temp_word%2) + word + " "*((temp_word//2))
      if j < 4:
        print(f"\033[1;{n};40m|{word}|", end="")
      else:
        print(f"\033[1;{n};40m|{word}|")
    #printing lables all in one line
    for k in range(0,5):
      n = ""
      label = board[k+i*5][1]
      if label == "red":
        n = "31"
      elif label == "blue":
        n = "34"
      elif label == "assassin":
        n = "35"
      elif label == "bystander":
        n = "33"
      else:
        n = "37"

      temp_label = formatting - len(label)
      label = " "*((temp_label//2)+temp_label%2) + label + " "*((temp_label//2))
      if k < 4:
        print(f"\033[1;{n};40m|{label}|", end="")
      else:
        print(f"\033[1;{n};40m|{label}|")

    lines = "-"*((formatting+2)*5)
    print(f"\033[1;37;40m{lines}")

def display_board_color_spymaster(gamewords, playerboard, spymasterboard):
  """
  Prints out a given board, can be player board or spymaster board
  """
  gamewords = gamewords + ["bystander", "red", "blue", "assassin"]
  formatting = len(max(gamewords, key=len))
  lines = "-"*((formatting+2)*5)
  print(f"\033[1;37;40m{lines}")
  for i in range(0,5):
    #printing words all in one line
    for j in range(0,5):
      n = "" #color variable
      label = spymasterboard[j+i*5][1] 
      if label == "red":
        n = "31"
      elif label == "blue":
        n = "34"
      elif label == "assassin":
        n = "35"
      elif label == "bystander":
        n = "33"
      else:
        n = "37"
      
      if spymasterboard[j+i*5] == playerboard[j+i*5]:
        n = "37"

      word = spymasterboard[j+i*5][0]
      temp_word = formatting - len(word)
      word = " "*((temp_word//2)+temp_word%2) + word + " "*((temp_word//2))
      if j < 4:
        print(f"\033[1;{n};40m|{word}|", end="")
      else:
        print(f"\033[1;{n};40m|{word}|")
    #printing lables all in one line
    for k in range(0,5):
      n = ""
      label = spymasterboard[k+i*5][1]
      if label == "red":
        n = "31"
      elif label == "blue":
        n = "34"
      elif label == "assassin":
        n = "35"
      elif label == "bystander":
        n = "33"
      else:
        n = "37"

      if spymasterboard[k+i*5] == playerboard[k+i*5]:
        n = "37"

      temp_label = formatting - len(label)
      label = " "*((temp_label//2)+temp_label%2) + label + " "*((temp_label//2))
      if k < 4:
        print(f"\033[1;{n};40m|{label}|", end="")
      else:
        print(f"\033[1;{n};40m|{label}|")

    lines = "-"*((formatting+2)*5)
    print(f"\033[1;37;40m{lines}")

def display_board(gamewords, board):
  """
  Prints out a given board, can be player board or spymaster board
  """
  gamewords = gamewords + ["bystander", "red", "blue", "assassin"]
  formatting = len(max(gamewords, key=len))
  print("-"*((formatting+2)*5))
  for i in range(0,5):
    builder1 = ""
    builder2 = ""
    for j in range(0,5):
      word = board[j+i*5][0]
      label = board[j+i*5][1]
      temp_word = formatting - len(word)
      temp_label = formatting - len(label)
      word = " "*((temp_word//2)+temp_word%2) + word + " "*((temp_word//2))
      label = " "*((temp_label//2)+temp_label%2) + label + " "*((temp_label//2))
      builder1 += "|"+word+"|"
      builder2 += "|"+label+"|"
    print(builder1)
    print(builder2)
    print("-"*((formatting+2)*5))

def guess_word(spymasterboard, playerboard, gamewords, guessword):
  """
  Edits the current game board to reflect a guess made on a word
  
  Input:
  - spymasterboard is a board (list) of tuples 
  
  Output:
  - updated_player_board is a board with the guess "revealing" the type of the chosen word
  - type is the type of the card guessed
  """
  
  if guessword not in gamewords:
    print(f"You inputted the invalid word {guessword}, please try again")
    return [], None
  
  index = gamewords.index(guessword)

  if playerboard[index][1] != "":
    print("You inputted an already guessed word, please try again")
    return [], None

  playerboard[index] = spymasterboard[index]

  return playerboard, playerboard[index][1]


def finished_game(playerboard, firstteam, guesser):
  """
  - Checks if the given playerboard is a completed board (meaning that the game has finished).
  - Condition for a completed game: Either one team has guessed every word of theirs 
    or one team has chosen the assassin word.
  """
  if firstteam.lower() == "red":
    countRedWords = 9
    countBlueWords = 8
  elif firstteam.lower() == "blue":
    countRedWords = 8
    countBlueWords = 9

  for card in playerboard:
    if card[1] == "red":
      countRedWords -= 1
    elif card[1] == "blue":
      countBlueWords -= 1
    
    if countRedWords == 0:
      print("Red team won!\n")
      return True
    elif countBlueWords == 0:
      print("Blue team won!\n")
      return True
    elif card[1] == "assassin":
      print(f"{guesser} team lost because they chose the assassin\n")
      return True
  return False

def invalid(clueword, gamewords, m):
  """
  Determines if the given word is valid by checking if the word
  is in gamewords, in the model, or has weird punctuation
  """
  do_not_put = "0123456789!_?*& "
  clueword = clueword.lower()
  for word in gamewords:
    word = word.lower() 
    if (word in clueword) or (clueword in word) or (not clueword in m) or (not does_not_share(clueword, do_not_put)):

      #print(f"(word in clueword): {(word in clueword)}")
      #print(f"(clueword in word): {(clueword in word)}")
      #print(f"(not clueword in m): {(not clueword in m)}")
      #print(f"(does_not_share(clueword, do_not_put)): {(does_not_share(clueword, do_not_put))}")
      return True
  
  return False
  
def play_game_as_spymaster(m):
  """
  Starts up a game with a given model to guess words
  """ 
  gamewords, spymaster_board, current_board, first, second = generate_board(m)

  counter = 0
  guesser = first

  print(f"\nGame started up!\n")

  while True:
    if counter % 2 == 0:
      guesser = first
    else:
      guesser = second

    counter += 1
    print(f"\nIt is {guesser} team's turn.\n")
    print("\nSpymaster board:\n")
    display_board_color_spymaster(gamewords, current_board, spymaster_board)
    print("\nPlayer board:\n")
    display_board_color_player(gamewords, current_board)
    print()
    
    clueword = input("Input your clue word:\n")
    while invalid(clueword, gamewords, m):
      clueword = input("Your clue was invalid or not in the model, try again:\n")
    n = input("\nInput the number:\n")

    clue = (clueword, n)
    guess = guess_words_given_clue(clue, current_board, m)

    guess_words = []
    for pair in guess:
      guess_words.append(pair[1])
      
    print(f"\nThe computer is thinking of guessing {guess_words}\n")
    for score_and_guess in guess:
      guessword = score_and_guess[1]
      current_board, card_type = guess_word(spymaster_board, current_board, gamewords, guessword)
      if current_board == [] or card_type == None:
        print("Uh oh ... invalid guess by computer. Please restart game.")
        return False

      print(f"The computer guessed {guessword}, a {card_type} card.")
      if card_type == "assassin":
        pass
      
      elif card_type != guesser:
        print(f"{guessword} is not one of your words. You lose your remaining guesses.")
        break

      if finished_game(current_board, first, guesser):
        again = input("\nThe game ended. Do you want to play again? y or n\n")
        if again == "y":
          return True
        else:
          return False
  return False
    
def play_game_as_player(m):
  """
  Starts up a game with a given model to guess words
  """ 
  gamewords, spymaster_board, current_board, first, second = generate_board(m)

  red_words = []
  blue_words = []
  neutral_words = []
  assassin_word = ""

  # Separate the board into their respective lists
  for combo in spymaster_board:
    word = combo[0]
    label = combo[1]
    if label == "red":
      red_words.append(word)
    elif label == "blue":
      blue_words.append(word)
    elif label == "neutral":
      neutral_words.append(word)
    else:
      assassin_word = word

  counter = 0
  guesser = first

  print(f"\nGame started up!\n")

  while True:
    if counter % 2 == 0:
      guesser = first
    else:
      guesser = second

    counter += 1

    print(f"\nIt is {guesser} team's turn.\n")

    print("\nPlayer board:\n")
    display_board_color_player(gamewords, current_board)
    print()

    # TODO: give a hint here
    own_words = blue_words
    opponent_words = red_words

    if guesser == "red":
      own_words = red_words
      opponent_words = blue_words
    
    clue, intended = give_clue(own_words, m, opponent_words = opponent_words, neutral_words = neutral_words, assassin_word = assassin_word)
    clueword = clue[0]
    number = clue[1]
    print(f"Your clue is {clueword} {number}\n")
    
    for i in range(0, number + 1):
      invalid = True
      answer = ""

      while invalid:
        answer = input("Input a guess (case-sensitive) or type -1 to end turn:\n")
        if answer == "-1":
          break
        current_board, card_type = guess_word(spymaster_board, current_board, gamewords, answer)
        if card_type is not None or answer == "-1":
          invalid = False
          
      if answer == "-1":
        break

      print(f"\nYou guessed {answer}, a {card_type} card.")

      if card_type == "red":
        red_words.remove(answer)

      if card_type == "blue":
        blue_words.remove(answer)
      
      if card_type == "neutral":
        neutral_words.remove(answer)
      
      
      print("\nPlayer board:\n")
      display_board_color_player(gamewords, current_board)
      print()  
        
      if card_type == "assassin":
        break
      
      elif card_type != guesser:
        print(f"{answer} is not one of your words. You lose your remaining guesses.")
        break

    print(f"\nThe intended words were: {intended}\n")
    if finished_game(current_board, first, guesser):
      again = input("\nThe game ended. Do you want to play again? y or n\n")
      if again == "y":
        return True
      else:
        return False
        
  return False
    
  
if __name__ == '__main__':
  
  # print(f"\033[1;34;40m|{x}|", end = "")
  # print("\033[1;32;40mhi2")
  # print("\033[1;37;40mhi3")

  # gamewords, spymaster_board, current_board, first, second = generate_board(wv)
  # print("\nSpymaster board:\n")
  # display_board_color(gamewords, spymaster_board)
  # print("\nPlayer board:\n")
  # display_board_color(gamewords, current_board)
  # print()

  # own_words = ["phoenix", "pirate", "leprechaun", "needle", "card", "diamond", "paste"]
  # bad_words = ["Jupiter", "laser", "eye", "olive", "bottle", "disease", "moon", "bond"]
  # neutral_words = ["engine", "shot", "spider", "bark", "India", "maple", "plate"]
  # assassin = "field"

  # clue, intended = give_clue(own_words, wv, opponent_words = bad_words,\
  #   neutral_words = neutral_words, assassin_word = assassin)

  #print(f"The final results:\nThis is the clue: {clue}.\nThese are the intended words: {intended}")


  continue_to_play = True
  while continue_to_play:
    continue_to_play = play_game_as_player(wv)

  print("\n\n\nThanks for playing!")

  
