import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.ticker as ticker
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os

# ================= SETTINGS ============================
EXCEL_FILE = r"input/ODI_runs_multilevel.xlsx"
OUTPUT_VIDEO = r"output/ODI_Top10_FlyIn_3min.mp4"

FPS = 25
SECONDS_PER_YEAR = 3      # ~3 minutes total video
TOP_N = 10
PHOTO_DIR = "Photos"
PHOTO_SIZE = 0.4
PHOTO_X_OFFSET = -0.05

# ======================================================
photo_cache = {}

def get_player_image(name):
    if name in photo_cache:
        return photo_cache[name]

    path = os.path.join(PHOTO_DIR, f"{name}.png")
    if not os.path.exists(path):
        return None

    img = plt.imread(path)
    imagebox = OffsetImage(img, zoom=PHOTO_SIZE)
    photo_cache[name] = imagebox
    return imagebox


# ---------------- LOAD DATA ----------------
df = pd.read_excel(EXCEL_FILE)

year_col = df.columns[0]
df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
df = df.dropna(subset=[year_col])
df.set_index(year_col, inplace=True)
df.index = df.index.astype(int)

for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.fillna(0)
years = df.index.tolist()


# ---------------- HELPERS ----------------
def ease(t):
    """Smooth easing for fly-in motion"""
    return 3*t**2 - 2*t**3


# ---------------- FIGURE ----------------
fig, ax = plt.subplots(figsize=(13, 7))
plt.style.use("default")

title_text = ax.text(
    0.5, 1.05,
    "Top ODI Run Scorers (1975–2020)",
    transform=ax.transAxes,
    ha="center",
    fontsize=22,
    weight="bold"
)

year_text = ax.text(
    0.88, 0.15, "",
    transform=ax.transAxes,
    fontsize=46,
    weight="bold"
)


# ---------------- ANIMATION ----------------
frames_per_year = int(FPS * SECONDS_PER_YEAR)
total_frames = (len(years) - 1) * frames_per_year


def update(frame):
    ax.clear()

    year_idx = frame // frames_per_year
    t = (frame % frames_per_year) / frames_per_year
    t = ease(t)

    if year_idx >= len(years) - 1:
        year_idx = len(years) - 2

    y1, y2 = years[year_idx], years[year_idx + 1]
    v1, v2 = df.loc[y1], df.loc[y2]

    # Interpolated values
    values = v1 + (v2 - v1) * t

    # Rankings at start and end
    rank_start = v1.rank(ascending=False, method="first")
    rank_end   = v2.rank(ascending=False, method="first")

    # Interpolated ranks (THIS IS THE FLY-IN MAGIC)
    rank_interp = rank_start + (rank_end - rank_start) * t

    # Build dataframe
    temp = pd.DataFrame({
        "value": values,
        "rank": rank_interp
    })

    # Keep only top N by current value
    temp = temp.sort_values("value", ascending=False).head(TOP_N)

    # Y positions: inverse rank (so rank 1 is at top)
    y_positions = TOP_N - temp["rank"]

    bars = ax.barh(
        y_positions,
        temp["value"],
        height=0.8,
        color="skyblue",
        edgecolor="black"
    )
# ---- PLAYER PHOTOS ----
for y, player in zip(y_positions, temp.index):
    imagebox = get_player_image(player)
    if imagebox is None:
        continue

    ab = AnnotationBbox(
        imagebox,
        (PHOTO_X_OFFSET, y),
        xycoords=("axes fraction", "data"),
        frameon=False,
        box_alignment=(0.5, 0.5)
    )
    ax.add_artist(ab)

    # Labels on bars
    for y, (name, val) in zip(y_positions, temp[["value"]].itertuples()):
        ax.text(
            val * 1.01,
            y,
            f"{int(val):,}",
            va="center",
            fontsize=12
        )

    # Y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(temp.index, fontsize=13)

    # X-axis
    ax.set_xlim(0, temp["value"].max() * 1.15)
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    ax.set_xlabel("Total ODI Runs", fontsize=14)

    # Title & Year
    ax.set_title("Top ODI Run Scorers (Career Progression)", fontsize=20, pad=12)
    year_text = ax.text(
        0.88, 0.15, str(int(y1 + (y2 - y1) * t)),
        transform=ax.transAxes,
        fontsize=46,
        weight="bold"
    )


# ---------------- RENDER ----------------
anim = FuncAnimation(
    fig,
    update,
    frames=total_frames,
    interval=1000 / FPS
)

anim.save(OUTPUT_VIDEO, writer="ffmpeg", dpi=130)

print("\n✅ Video generated successfully:")
print(OUTPUT_VIDEO)
