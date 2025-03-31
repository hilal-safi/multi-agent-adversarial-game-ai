import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# Load and Prepare Move-Level Data
# -------------------------------
df_moves = pd.read_csv("performance_log.csv")
print(df_moves.columns)

# If 'Nodes1' is the intended column for nodes, rename it to 'Nodes'
if 'Nodes1' in df_moves.columns:
    df_moves.rename(columns={'Nodes1': 'Nodes'}, inplace=True)

# Convert columns to numeric, coercing errors into NaN
df_moves["Time(s)"] = pd.to_numeric(df_moves["Time(s)"], errors="coerce")
df_moves["Nodes"] = pd.to_numeric(df_moves["Nodes"], errors="coerce")

# Adjust move time for Gemini moves: subtract 12 seconds for each Gemini move
df_moves.loc[df_moves["AgentUsed"].str.lower() == "gemini", "Time(s)"] = \
    df_moves.loc[df_moves["AgentUsed"].str.lower() == "gemini", "Time(s)"] - 12

# Move-Level Summary: Average Time and Nodes per Agent
print("=== Move-Level Summary ===")
move_summary = df_moves.groupby("AgentUsed")[["Time(s)", "Nodes"]].mean()
print(move_summary)

# Define unique agents and assign each a color from the "tab10" colormap
agents = move_summary.index.tolist()
cmap = plt.get_cmap("tab10")
agent_colors = {agent: cmap(i) for i, agent in enumerate(agents)}

# -------------------------------
# Plotting Move-Level Graphs
# -------------------------------

# Avg Time per Move by Agent (Bar Chart)
plt.figure(figsize=(8, 5))
plt.bar(move_summary.index, move_summary["Time(s)"],
        color=[agent_colors[agent] for agent in move_summary.index])
plt.title("Avg Time per Move by Agent (Adjusted)")
plt.ylabel("Time (s)")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()

# Avg Nodes Evaluated per Move by Agent (Bar Chart)
plt.figure(figsize=(8, 5))
plt.bar(move_summary.index, move_summary["Nodes"],
        color=[agent_colors[agent] for agent in move_summary.index])
plt.title("Avg Nodes Evaluated per Move by Agent")
plt.ylabel("Nodes")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()

# -------------------------------
# Load and Prepare Game-Level Data
# -------------------------------
df_games = pd.read_csv("game_result.csv")
df_games["GameTime"] = pd.to_numeric(df_games["GameTime"], errors="coerce")

print("\n=== Game-Level Summary ===")
game_summary = df_games["AgentResult"].value_counts()
print(game_summary)

# Adjust game time for Gemini games:
# For each game played by Gemini, subtract 12 seconds for every Gemini move in that game.
# (Assumes the game identifier is stored in the "GameNum" column.)
gemini_move_counts = df_moves[df_moves["AgentUsed"].str.lower() == "gemini"].groupby("GameNum").size()

def adjust_game_time(row):
    if row["AgentUsed"].strip().lower() == "gemini":
        count = gemini_move_counts.get(row["GameNum"], 0)
        return row["GameTime"] - 12 * count
    else:
        return row["GameTime"]

df_games["AdjustedGameTime"] = df_games.apply(adjust_game_time, axis=1)

# -------------------------------
# Plotting Game-Level Graphs
# -------------------------------

# Pie Chart: Overall AI Game Result Distribution
plt.figure(figsize=(8, 5))
plt.pie(game_summary, labels=game_summary.index, autopct="%1.1f%%", startangle=90)
plt.title("AI Game Results")
plt.tight_layout()
plt.show()

# Avg Game Time by Agent (Bar Chart) using the adjusted game times
plt.figure(figsize=(8, 5))
avg_game_time = df_games.groupby("AgentUsed")["AdjustedGameTime"].mean()
plt.bar(avg_game_time.index, avg_game_time,
        color=[agent_colors.get(agent, cmap(0)) for agent in avg_game_time.index])
plt.title("Avg Game Time by Agent (Adjusted)")
plt.ylabel("Game Time (s)")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()

# Win Percentage by Agent (Bar Chart)
win_percentage = df_games.groupby("AgentUsed")["AgentResult"].apply(
    lambda results: (results == "Win").sum() / results.count() * 100
)
print("\n=== Win Percentage by Agent ===")
print(win_percentage)

plt.figure(figsize=(8, 5))
plt.bar(win_percentage.index, win_percentage,
        color=[agent_colors.get(agent, cmap(0)) for agent in win_percentage.index])
plt.title("Win Percentage by Agent")
plt.ylabel("Win Percentage (%)")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()


# Histogram: Distribution of Game Times for Each Agent (Adjusted)
plt.figure(figsize=(8, 5))
for agent in agents:
    agent_game_time = df_games[df_games["AgentUsed"] == agent]["AdjustedGameTime"]
    plt.hist(agent_game_time, bins=20, alpha=0.5, label=agent,
             color=agent_colors.get(agent, cmap(0)))
plt.title("Histogram of Game Times by Agent (Adjusted)")
plt.xlabel("Game Time (s)")
plt.ylabel("Frequency")
plt.legend(title="Agent")
plt.tight_layout()
plt.show()
