import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.ticker as ticker
import random

# ====================== SETTINGS ======================
EXCEL_FILE = r"input/ODI_runs_multilevel.xlsx"
OUTPUT_VIDEO = r"output/top10_odi_batsmen_beautified.mp4"

FPS = 18                # smooth animation speed
SECONDS_PER_YEAR = 3    # you can reduce to 2 later for faster videos

MILESTONES = [5000, 10000, 15000]   # show popup when crossed
# =======================================================


# --------------------- Load Data -----------------------
df = pd.read_excel(EXCEL_FILE)

# Fix year + numeric conversion
year_col = df.columns[0]
df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.fillna(0)
df.set_index(year_col, inplace=True)
df.index = df.index.astype(int)
years = df.index.tolist()


# ---------- Assign permanent unique colors per player ------
players = df.columns.tolist()
random.seed(42)
colors = {p: (random.random(), random.random(), random.random()) for p in players}


# ---------- Plot Setup ----------
fig, ax = plt.subplots(figsize=(12, 7))
plt.style.use("seaborn-v0_8-darkgrid")
ax.set_facecolor("#111111")
fig.patch.set_facecolor("#111111")

title = ax.text(0.5, 1.07, "Top ODI Batsmen – Total Runs Progression (1975-2020)",
                transform=ax.transAxes, ha='center', fontsize=22, color="#ffffff", weight="bold")

year_text = ax.text(0.90, 0.15, "", transform=ax.transAxes, fontsize=40,
                    color="white", ha="center", va="center", weight="bold")

milestone_text = ax.text(0.5, 0.92, "", transform=ax.transAxes,
                         fontsize=18, color="gold", ha="center", va="center", weight="bold")


# Smooth interpolation function (easing)
def smooth_step(val):
    return 3*val**2 - 2*val**3     # S-curve (0→1 smoothly)


# ---------------- Animation Update ----------------------
def update(frame):
    i = frame // (FPS * SECONDS_PER_YEAR)
    progress = (frame % (FPS * SECONDS_PER_YEAR)) / (FPS * SECONDS_PER_YEAR)
    progress = smooth_step(progress)

    if i >= len(years)-1:
        return

    y1, y2 = years[i], years[i+1]
    d1, d2 = df.loc[y1], df.loc[y2]

    values = d1 + (d2 - d1) * progress
    top10 = values.sort_values(ascending=False).head(10)[::-1]  # reversed for top at bottom

    ax.clear()
    ax.set_facecolor("#111111")

    # Bars plotted with player colors, modern look
    bars = ax.barh(top10.index, top10.values,
                   color=[colors[p] for p in top10.index],
                   edgecolor="white", linewidth=1.1)

    # Value labels
    for bar, value in zip(bars, top10.values):
        ax.text(value + (max(top10.values)*0.01),
                bar.get_y()+bar.get_height()/2,
                f"{int(value):,}",
                va='center', color="white", fontsize=14, weight="bold")

    # Styling
    ax.set_xlim(0, top10.max() * 1.25)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.tick_params(axis='both', colors='white', labelsize=12)
    ax.set_ylabel("")
    ax.set_xlabel("Runs", color="white", fontsize=14)
    for spine in ax.spines.values():
        spine.set_color("#555555")

    # Year display
    year_display = int(y1 + (y2-y1)*progress)
    year_text.set_text(str(year_display))

    # ---------------- Milestones Pop-up ----------------
    crossed = [m for m in MILESTONES if any((d1 < m) & (d2 >= m))]
    if crossed and progress > 0.3:
        milestone_text.set_text(f"🎉 Milestone reached: {crossed[0]:,} runs!")
    else:
        milestone_text.set_text("")


# ------------------ Run Animation -----------------------
total_frames = len(years) * FPS * SECONDS_PER_YEAR

anim = FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
anim.save(OUTPUT_VIDEO, writer="ffmpeg", dpi=120)

print("🎬 Video generation complete → ", OUTPUT_VIDEO)
