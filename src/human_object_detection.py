# source .venv/bin/activate

#!/usr/bin/env python3
import cv2
import shutil
import time
from pathlib import Path
from ultralytics import YOLO

# load dir pathing
base_dir = Path.home()
good_dir = base_dir / 'good'
bad_dir = base_dir / 'bad'
incoming_dir = base_dir / 'incoming'

# verify dir exist
good_dir.mkdir(parents=True, exist_ok=True)
bad_dir.mkdir(parents=True, exist_ok=True)
incoming_dir.mkdir(parents=True, exist_ok=True)

#config
INCOMING_DIR = Path(incoming_dir)
GOOD_DIR = Path(good_dir)
BAD_DIR = Path(bad_dir)
MODEL_PATH = Path("model=/home/USER/yolov5/yolov5nu.pt").expanduser()
PERSON_CLASS = 0 # COCO class ID for "person"
CONF_THRESH = 0.3 # confidence threshold
FRAME_SKIP = 7 # only run detection every n frames
INPUT_SIZE = 416

VIDEO_EXTENSIONS = ['*.avi', '*.flv', '*.mkv', '*.mov', '*.mp4', '*.wmv',]

# ensure output dirs exist
for d in (GOOD_DIR, BAD_DIR, INCOMING_DIR):
  d.mkdir(parents=True, exist_ok=True)

# load YOLOv5 model once, outside functions
model = YOLO(str(MODEL_PATH))
model.fuse() # fuse Conv + BN for speed on CPU

def ProcessVideo(video_path: Path):
  """Returns True if a person is detected, else False."""
  cap = cv2.VideoCapture(str(video_path))
  frame_id = 0
  person_found = False

  # read frames in batches for better performance
  while cap.isOpened() and not person_found:
    ret, frame = cap.read()
    if not ret:
      break

    if frame_id % FRAME_SKIP == 0:
      # YOLOv5 expects BGR -> RGB
      results = model.predict(frame[..., ::-1], conf=CONF_THRESH, classes=[PERSON_CLASS])
      if results and len(results[0].boxes) > 0:
        person_found = True
        break  # early exit on detection

    frame_id += 1

  cap.release()
  return person_found

def main():
  processed = set()  # avoid re-processing files

  while True:
    # process all supported video formats
    video_files = []
    for extension in VIDEO_EXTENSIONS:
      video_files.extend(INCOMING_DIR.glob(extension))

    # sort files by modification time for predictable processing order
    video_files.sort(key=lambda f: f.stat().st_mtime)

    for video_file in video_files:
      print(f"[+] Checking {video_file.name}...", flush=True)

      if ProcessVideo(video_file):
        target = GOOD_DIR / video_file.name
        print("    -> person detected, moving to good/", flush=True)
      else:
        target = BAD_DIR / video_file.name
        print("    -> no person, moving to bad/", flush=True)

      shutil.move(str(video_file), str(target))

    time.sleep(2)  # poll interval

if __name__ == "__main__":
  print("Starting person object detection...")
  main()
