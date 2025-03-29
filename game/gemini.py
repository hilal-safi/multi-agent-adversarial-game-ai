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
import google.generativeai as genai
from game.board import Board, check_win
from dotenv import load_dotenv
from typing import Literal, Tuple, List
import re
import time
import csv
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
  raise ValueError("GEMINI_API_KEY is not provided. Please provide it in .env file")

logged_games = set()

def get_next_game_number() -> int:
    try:
        with open("game_result.csv", "r") as f:
            rows = list(csv.reader(f))
            if len(rows) <= 1:
                return 1
            last_row = rows[-1]
            return int(last_row[0]) + 1
    except FileNotFoundError:
        return 1

def start_new_game_log(game_num: int):
    with open("gemini_analysis.txt", "a") as f:
        f.write(f"\n####################################\n")
        f.write(f"###          GAME {game_num:<3}          ###\n")
        f.write(f"####################################\n\n")

class GeminiAPI:
  def __init__(self, api_key: str) -> None:
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

  def generate(self, prompt: str):
      start = time.time()
      max_retries = 3
      for attempt in range(max_retries):
          try:
              response = self.model.generate_content(prompt)
              self.last_time = round(time.time() - start, 4)
              return response.text
          except Exception as e:
              print(f"[Gemini Retry {attempt + 1}/{max_retries}] Error: {e}")
              if attempt == max_retries - 1:
                  with open("gemini_analysis.txt", "a") as f:
                      f.write(f"[GEMINI ERROR - Quota/Failure]: {e}\n")
                      f.write("------------------------------------------------------------\n")
                  return "ERROR: Gemini API quota exceeded or failed to respond."
              time.sleep(1)  # Small delay before retry

  def generate_with_thinking(self, prompt: str):
    response = self.model.generate_content(prompt)
    return response.text

  def json(self, prompt: str, schema):
    response = self.model.generate_content(prompt)
    match = re.findall(r"\b[1-7]\b", response.text)
    if match:
        return int(match[0])
    raise ValueError("Could not parse a valid column number from Gemini response.")

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

def get_move_from_gemini(board: Board, game_num: int) -> int: # - Make sure this is an int
    if game_num not in logged_games:
        start_new_game_log(game_num)
        logged_games.add(game_num)
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

    with open("gemini_analysis.txt", "a") as f:
        f.write("BOARD STATE:\n" + printed + "\n")
        f.write("RESPONSE:\n" + response + "\n")
        f.write("------------------------------------------------------------\n")

    prompt = f"""You are a professional Connect 4 strategist.
    
{rules}

Analyze the thought process and commentary below, and choose the BEST column number (1 to {board.columns}) for player B to play. Only return a single integer on its own line. Do not include any explanation.

{response}
"""

    col = gemini.json(prompt, int)
    if isinstance(col, str) and col.startswith("ERROR"):
        print("Gemini failed to return a valid response. Falling back to random valid column.")
        for i in range(board.columns):
            if board.is_valid_move(i):
                return i
        raise RuntimeError("No valid moves available.")

    print(f"[Gemini JSON Response] Column: {col}")

    if not isinstance(col, int) or col < 1 or col > board.columns:
        raise ValueError(f"Invalid column received from Gemini: {col}")

    col_index = col - 1
    print(f"Initial column: {col}")
    max_tries = 3
    failedAttempts: List[int] = []

    while col_index < 0 or col_index >= board.columns or not board.is_valid_move(col_index):
        failedAttempts.append(col)
        if len(failedAttempts) == max_tries:
            print("Max tries reached. Attempting fallback column.")
            fallback_col = 3
            if board.is_valid_move(fallback_col):
                return fallback_col
            for i in range(board.columns):
                if board.is_valid_move(i):
                    return i
            raise RuntimeError("Gemini and fallback logic failed to find a valid move.")
        res = gemini.json(prompt + f"\nThe previous model responded with the following columns but they are invalid: " + ", ".join(f'"{num}"' for num in failedAttempts), int)
        col = res
        col_index = col - 1
        print(f"New column: {col}")

    decision_time = gemini.last_time if hasattr(gemini, "last_time") else 0.5
    board.last_decision_time = decision_time

    board.last_nodes_evaluated = "N/A"
    board.last_agent_used = "gemini"

    with open("gemini_analysis.txt", "a") as f:
        f.write(f"FINAL MOVE SELECTED: Column {col}\n")
        f.write("------------------------------------------------------------\n")

    return col - 1