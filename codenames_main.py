#
# Final Project    ~~ CS 181 Spring 2021
#

#
# Collaborators: Roman Herrera, Kobe Lin, Valentina Vallalta, Alina Saratova
#


def guess_words_given_clue(clue, board, model): 
  """ 
  This function guesses which words are associated with a clue using word2vec model.

  Inputs: 
  - clue is a tuple that contains a one word string and an integer that
    is the number of words associated with the clue in the format (clueword, n)
  - board is the current words on the board
  - model is the word2vec model used for the guessing
  
  Outputs:
  - n number of words as guesses based on the clue in highest probability
  """


def score_clue(clue, board, intended):
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

def give_clue(own_words, opponent_words = [], neutral_words = [], assassin_word = [], model):
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
  """

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
  """
  
  player_board = []
  spymaster_board = []
  not_valid = []

  num_red = 0
  num_blue = 0
  num_bystander = 7
  num_assassin = 1

  if random.randint(0,1) == 1:
      num_red = 9
      num_blue = 8
  else:
      num_red = 8
      num_blue = 9

  options = ["red"] * num_red + ["blue"] * num_blue + ["bystander"] * num_bystander + ["assassin"] * num_assassin

  while len(player_board) < 25:
      rand_card = list(random.choice(A))

      if (rand_card not in not_valid):   # Checks to see if the given card was already used
          
          # Adds the chosen card to the list of used cards
          not_valid.append(rand_card)
          rand_word = rand_card[random.randint(0, 1)]
          
          # Adds the random word to the player board
          player_board.append(rand_word)
          
          # Adds the random word to the spymaster board with a "team" attached and removes that option from options
          rand_option = random.choice(options)
          spymaster_board.append((rand_word, rand_option))
          options.remove(rand_option)

  return player_board, spymaster_board


if __name__ == '__main__':
  clue = ("suit", 2)
  LoW = [ "armor", "spring", "romans", "tuxedo" ]
  m = m  # defined in another cell
  LoS = make_codenames_guess( clue, LoW, m )
  for pair in LoS:
      print(f"{pair}")
