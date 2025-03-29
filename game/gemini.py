""" gemini.py
  - This file contains the GeminiAPI class that interacts with the Gemini API
  - The class has methods to generate text and JSON responses from the API
  - The class also has a method to generate a move for the Connect 4 game
  - The class uses the dotenv library to load environment variables from a .env file
  - The class uses the google.genai library to interact with the Gemini API
  - The class uses the game.board module to interact with the Connect 4 board
  - The class uses the os library to load environment variables
"""
import os
from google import genai
from game.board import Board, check_win
from dotenv import load_dotenv
from typing import Literal, Tuple, List
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
  raise ValueError("GEMINI_API_KEY is not provided. Please provide it in .env file")

class GeminiAPI:
  def __init__(self, api_key:str) -> None:
    self.api_key = api_key
    self.client = genai.Client(api_key=api_key, http_options={'api_version':'v1alpha'})

  def generate(self, prompt:str):
    response = self.client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text
    
  def generate_with_thinking(self, prompt:str):
    response = self.client.models.generate_content(
        model="gemini-2.0-flash-thinking-exp", contents=prompt
    )
    return response.text

  def json(self, prompt:str, schema):
    response = self.client.models.generate_content(
          model="gemini-2.0-flash", contents=prompt, config={
          'response_mime_type': 'application/json',
          'response_schema': int,
      },
    )
    return response.parsed


gemini = GeminiAPI(gemini_key)

# - These are all rules that I added as I found flaws in its reasonings. Add or remove rules as you wish
rules = """Rules:
- Player A uses pieces marked as A.
- Player B uses pieces marked as B. You are player B.
- Empty slots are marked as 0.
- A player wins if they connect four of their pieces in a row, column, or diagonal.
- As much as it is important for you to win, it is important to stop player A from getting close to winning. For example if a player A has 3 in a row, you must block them from getting the 4th.
- You cannot place anything on a column that's full. If the top row of a column you pick has a number, avoid using that column.
- Pick the best move that would let you as player B to win the game by connection 4 in a row. 
- Stop player A from getting 4 in a row. For example, if you see the player has 3 'A's stacked, you must select that column to stop the player.
- If a player A has 2 'A's in a row with an ability to place their piece on either side to make 4 in a row, make sure you block at least 1 side so it doesn't lead to a fork or a double threat.
- If there is not enough room for you to create 4 in a row, there is no need to pursue that path.
- If player A has 3 in a row, attempt to stop them at all costs. Consider all the locations that the player can place their next move. Remember, they can only stack them.
- If a potential threat is surrounded by 'B's and there are no '0's for A to be placed to form 4 in a row, then it is not a threat.
"""

def get_move_from_gemini(board: Board) -> int: # - Make sure this is an int
    printed = board.to_string()
    print(f"------------------------------------\nThinking\n{printed}\n------------------------------------")
    prompt = f"""You are a professional Connect 4 player. 

{rules}

Current Connect 4 Board:

{printed}

The bottom row represent the column number.

Analyze the board and respond with what your best options are, that would prevent player A from winning and help you win, and explain your reasoning. Think hard. The column you pick must have at least 1 empty slot."""

    # - Switch with gemini.generate_with_thinking for a very slightly stronger opponent, though the response times are much longer
    response = gemini.generate(prompt)
    print(response)

    prompt = f"""You are a professional Connect 4 player. 

{rules}

Based on the insights below, pick a column number ranging from 1 to {board.columns}.

{response}
"""

    col = gemini.json(prompt, int)

    # - ----------------------------------------------------------------
    # - THIS IS A RETRYING LOGIC IN CASE GEMINI GIVES AN INVALID COLUMNS
    print(f"Initial column: {col}")
    max_tries = 3
    failedAttempts: List[int] = []
    while col - 1 < 0 or col - 1 > 7 or not board.is_valid_move(col - 1):
      if len(failedAttempts) == max_tries:
        raise Exception("Max tries reached and gemini couldn't come up with a valid column")
      failedAttempts.append(col)
      res = gemini.json(prompt + f"\nThe previous model responsed with the following columns but they are either outside of model bounds or are invalid moves such as full column: " + ", ".join(f'"{num}"' for num in failedAttempts), int)
      col = res
      print(f"New column: {col}")
      # - ----------------------------------------------------------------

    return col - 1