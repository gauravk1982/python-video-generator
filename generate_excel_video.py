import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

# ===============================
# Configuration
# ===============================
EXCEL_FILE = "input/data.xlsx"      # <-- put your excel here
OUTPUT_VIDEO = "output/video.mp4"
TITLE = "Dynamic Graph Video"
FPS = 10                 # frames per second (lower = slower)
SECONDS_PER_YEAR = 1.5   # how long each year stays on screen (increase this)

# ===============================
# Load Data
# ===============================
df = pd.read_excel(EXCEL_FILE)

years = sorted(df["Year"].unique())
categories = df["Category"].unique()

os.makedirs("output", exist_ok=True)

fig, ax = plt.subplots(figsize=(12,7))

def update(year):
    ax.clear()
    subset = df[df["Year"] == year].sort_values("Value")
    ax.barh(subset["Category"], subset["Value"], color="skyblue")
    ax.set_title(f"{TITLE}  |  Year: {year}", fontsize=18)
    ax.set_xlim(0, subset["Value"].max()*1.2)

ani = FuncAnimation(fig, update, frames=years, repeat=False)

# Save using FFmpeg writer
ani.save(OUTPUT_VIDEO, writer="ffmpeg", fps=FPS, dpi=120)

print("\n🎉 VIDEO CREATED SUCCESSFULLY!")
print(f"Find your video at: {OUTPUT_VIDEO}")
