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



if __name__ == '__main__':
  clue = ("suit", 2)
  LoW = [ "armor", "spring", "romans", "tuxedo" ]
  m = m  # defined in another cell
  LoS = make_codenames_guess( clue, LoW, m )
  for pair in LoS:
      print(f"{pair}")
