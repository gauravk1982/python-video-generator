import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from moviepy import VideoClip, ImageClip, CompositeVideoClip, TextClip
import os

# ===============================
# CONFIGURATION YOU CAN CHANGE
# ===============================
VIDEO_TITLE = "Sample Dynamic Chart Video"
FPS = 15
DURATION_PER_YEAR = 1  # seconds per frame/year
OUTPUT_FILE = "output/video.mp4"

# ===============================
# Load Excel (Later you will replace sample with your file)
# ===============================
df = pd.DataFrame({
    "Year": [2018,2018,2018,2019,2019,2019,2020,2020,2020],
    "Category": ["BMW","Audi","Toyota","BMW","Audi","Toyota","BMW","Audi","Toyota"],
    "Value": [80,95,120,90,110,140,100,115,160]
})

years = sorted(df["Year"].unique())
categories = df["Category"].unique()

# Create output folder if missing
os.makedirs("output", exist_ok=True)

# ===============================
# Create frames using Matplotlib
# ===============================
fig, ax = plt.subplots(figsize=(10,6))

def update(year):
    ax.clear()
    subset = df[df["Year"]==year].sort_values("Value")
    ax.barh(subset["Category"], subset["Value"], color="skyblue")
    ax.set_title(f"{VIDEO_TITLE}\nYear: {year}", fontsize=16)
    ax.set_xlabel("Value")
    ax.set_xlim(0, subset["Value"].max()*1.2)

ani = FuncAnimation(fig, update, frames=years, repeat=False)

TEMP_VIDEO = "temp_video.mp4"
ani.save(TEMP_VIDEO, writer="ffmpeg", fps=FPS)

# ===============================
# Add Title Overlay Using MoviePy
# ===============================
video = VideoClip(lambda t: None, duration=len(years)*DURATION_PER_YEAR)
title = TextClip(VIDEO_TITLE, fontsize=60, color="white").set_position("top").set_duration(video.duration)

final = CompositeVideoClip([
    ImageClip(TEMP_VIDEO).set_duration(video.duration),
    title
])

final.write_videofile(OUTPUT_FILE, fps=FPS)

print("\n🎉 Video Generated Successfully!")
print("Check the output folder.")