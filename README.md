# Multi-Agent Adversarial Game (Connect 4) with Minimax, Alpha-Beta Pruning & Gemini API

This project implements a multi-agent adversarial game environment using **Connect4** as the base game. It explores decision-making strategies using **Minimax**, **Alpha-Beta Pruning**, and a third-party AI agent via the **Gemini API**.

## Group Members
- Amy Freij Camacho
- Nicole Freij Camacho
- Hilal Safi
- Michael Qushair
- Cameron Zhang
- Ryan Wilson
- Gabriel Paquin
- Abtin Turing
- Afo Awogbemi
- Darsh Gandhi

## Project Overview

- Two-player turn-based **Connect4** game.
- AI Agents:
  - Minimax Algorithm
  - Alpha-Beta Pruning Algorithm
  - Gemini API-based Agent (External AI)
- Performance comparison and scalability analysis.

### Features & Goals

- [x] Implement Connect4 Game Environment.
- [x] Implement Minimax Algorithm.
- [x] Add Alpha-Beta Pruning Optimization.
- [x] Local Multiplayer: Classic Connect 4 with two human players.
- [x] Integrate Gemini API Agent.
- [x] Simulation Mode: Bulk-run or replay games for performance and statistics, pitting the AI agents against a simple random move generator.
- [x] Logging: Time-per-move and node evaluations are recorded in CSV files for performance analysis.
- [x] Compare Agent Performance (using logs stored in CSV files).
- [x] Visualize Game Trees and Pruning.

## Project Structure

```
multi-agent-adversarial-game-ai/
├── main.py                  # Main launcher for playing or simulating games
├── connect_four.py          # MinimaxAgent class and game initialization logic
├── results.py               # Graphs and performance analysis of simulations
├── game/
│   ├── board.py             # Core Connect 4 board logic (drop, win-check, etc.)
│   ├── gemini.py            # GeminiAPI wrapper for LLM-based decision making
│   └── ui.py                # Pygame-based GUI rendering and animations
├── .env                     # Your Gemini API key: GEMINI_API_KEY=your_key_here
├── performance_log.csv      # Logs each turn's agent, move, time taken, and node count
├── game_result.csv          # Stores final game outcomes, agent scores, and durations
├── gemini_analysis.txt      # Text-based reasoning and move history from the Gemini API
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hilal-safi/multi-agent-adversarial-game-ai.git
   cd multi-agent-adversarial-game-ai
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Gemini API key in a `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## How to Run

Step-by-step instructions for running the game and testing the agents.
You can run the game in one of several modes. At the bottom of `main.py`, uncomment the desired mode:

- Local multiplayer:
  ```python
  pygame_game("2player")
  ```

- Player vs. Minimax AI:
  ```python
  pygame_game("minimax")
  ```

- Player vs. Alpha-Beta Pruning AI:
  ```python
  pygame_game("alpha-beta")
  ```

- Player vs. Gemini API:
  ```python
  pygame_game("gemini")
  ```

To simulate games in headless mode (e.g. for analysis), use:
```python
pygame_game(mode="minimax", simulate=True, auto_restart=True)
```

Results will be saved to `performance_log.csv` and `game_result.csv`.

## How It Works

### Game Flow
- The game board is represented as a 2D list, where `0 = empty`, `1 = Player 1`, and `2 = Player 2`.
- Moves are selected either by human input (mouse click) or by the AI agent (Minimax, Alpha-Beta, or Gemini).
- The first player to align four tokens in a row, column, or diagonal wins.

### AI Agents
- **Minimax**: Classic recursive algorithm that evaluates all possible game states up to a fixed depth.
- **Alpha-Beta Pruning**: Optimized Minimax that skips irrelevant branches, significantly reducing computation.
- **Gemini API**: Sends board state as a prompt to a language model which returns a recommended column (not a search-based AI, so node count is zero).

## Performance Metrics

This project compares the performance of Minimax, Alpha-Beta Pruning, and Gemini API agents against a random opponent over multiple simulations.

- **Simulations Run**: 100 Minimax, 100 Alpha-Beta, 20 Gemini
- **Avg. Time per Move**:
  - Alpha-Beta: Fastest due to pruning
  - Minimax: Moderate
  - Gemini: Slowest due to API latency
- **Win Rates**:
  - Minimax: 100%
  - Alpha-Beta: 100%
  - Gemini: ~50%
- **Node Evaluation**:
  - Minimax and Alpha-Beta report number of nodes evaluated
  - Gemini API does not expose internal decision nodes (0 recorded)
  - Gemini strategy insights are further explored in `gemini_analysis.txt`, revealing how Gemini prioritizes center control, threat blocking, and fork prevention.

CSV output for analysis:
- `performance_log.csv`: Move time, agent type, nodes evaluated
- `game_result.csv`: Game outcomes and total duration

## Logging & CSV Output

After each game or simulation, two CSVs are generated:
- `performance_log.csv`: Records agent name, move number, column chosen, time taken, and evaluated nodes (if applicable).
- `game_result.csv`: Captures overall game outcome, including player/agent winner, score, and game duration.

These files can be visualized or analyzed using tools like Excel or Python:

```python
import pandas as pd
df = pd.read_csv("performance_log.csv")
print(df.describe())
```

## Gemini API

### Overview
Gemini is an external Large Language Model (LLM) used to simulate intelligent gameplay. It receives the current board state as a textual prompt and responds with strategic analysis and a chosen column.
Model used: `gemini-2.0-flash`
Note: Gemini does not expose internal computations like a search tree. Therefore, node count is always recorded as `0`.

### How it works:
  1. The board is serialized into text format.
  2. A detailed prompt is sent describing the game rules and the board state.
  3. Gemini analyzes and returns a recommended move (column number).
  4. If Gemini selects an invalid column (e.g., full), fallback logic retries or chooses a random valid column.

### Troubleshooting

- **Gemini model not found**: Check `gemini.py` and ensure you're using a valid model (e.g., `"chat-bison-001"`). Your API key must have access.
- **Rate limits**: Free-tier Gemini API may throttle you. Use fewer games or increase delay between requests.
- **Invalid column**: Gemini may return an invalid column. The program includes retry logic and falls back to a random valid move.
- **Missing API key**: Ensure `.env` file exists with `GEMINI_API_KEY=your_key`.

## References

- _Artificial Intelligence: A Modern Approach_ by Russell & Norvig  
- CP468 Course Notes
- Gemini API Documentation  

---
