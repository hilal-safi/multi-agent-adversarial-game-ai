import pandas as pd
import matplotlib.pyplot as plt

# === Load Move-Level Data ===
df_moves = pd.read_csv("performance_log.csv")

# Clean and prepare move data
df_moves["Time(s)"] = pd.to_numeric(df_moves["Time(s)"], errors="coerce")
df_moves["Nodes"] = pd.to_numeric(df_moves["Nodes"], errors="coerce")

# === Move-Level Summary ===
print("=== Move-Level Summary ===")
move_summary = df_moves.groupby("AgentUsed")[["Time(s)", "Nodes"]].mean()
print(move_summary)

# Plot: Avg Time per Move by Agent
plt.figure(figsize=(8, 5))
move_summary["Time(s)"].plot(kind="bar", title="Avg Time per Move by Agent")
plt.ylabel("Time (s)")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()

# Plot: Avg Nodes Evaluated per Move by Agent
plt.figure(figsize=(8, 5))
move_summary["Nodes"].plot(kind="bar", title="Avg Nodes Evaluated per Move by Agent")
plt.ylabel("Nodes")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()

# === Load Game-Level Data ===
df_games = pd.read_csv("game_result.csv")

# Clean and convert time column
df_games["GameTime"] = pd.to_numeric(df_games["GameTime"], errors="coerce")

# === Game-Level Summary ===
print("\n=== Game-Level Summary ===")
game_summary = df_games["AgentResult"].value_counts()
print(game_summary)

# Plot: AI Game Result Distribution
plt.figure(figsize=(8, 5))
game_summary.plot(kind="pie", autopct="%1.1f%%", title="AI Game Results")
plt.ylabel("")
plt.tight_layout()
plt.show()

# Plot: Avg Game Time by Agent
plt.figure(figsize=(8, 5))
df_games.groupby("AgentUsed")["GameTime"].mean().plot(kind="bar", title="Avg Game Time by Agent")
plt.ylabel("Seconds")
plt.xlabel("Agent")
plt.tight_layout()
plt.show()