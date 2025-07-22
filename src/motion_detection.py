import base64
import cv2
import datetime
import os
import time
import zmq

# config
VIDEO_DURATION = 5  # seconds to record after motion is detected
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 20
LOCAL_CLIP_PATH = 'clips' # home directory for storing clips temporarily
RASPBERRY_PI_IP = 'LOL.LOL.LOL.LOL'  # replace with actual IP address of Raspberry Pi
PORT = 5555

os.makedirs(LOCAL_CLIP_PATH, exist_ok=True)

# ZeroMQ PUSH Socket
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect(f"tcp://{RASPBERRY_PI_IP}:{PORT}")

def RecordClip(cap, filename):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
    frames_to_record = int(VIDEO_DURATION * FPS)
    for _ in range(frames_to_record):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    out.release()

def SendClipZMQ(filepath):
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read())
        socket.send_multipart([os.path.basename(filepath).encode(), encoded])
        print(f"Sent clip {os.path.basename(filepath)} to Raspberry Pi")

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    ret, prev_frame = cap.read()
    if not ret:
        print("Failed to read from camera.")
        cap.release()
        return

    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_frame = cv2.GaussianBlur(prev_frame, (21, 21), 0)

    print("Motion detection started...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        delta = cv2.absdiff(prev_frame, gray)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_pixels = cv2.countNonZero(thresh)
        motion_detected = motion_pixels > 5000

        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(LOCAL_CLIP_PATH, f"motion_{timestamp}.mp4")
            print(f"[{timestamp}] Motion detected! ({motion_pixels} px) Saving to {filename}")
            RecordClip(cap, filename)
            SendClipZMQ(filename)
            time.sleep(0.5)  # shorter sleep for responsiveness

            # Skip updating prev_frame for next detection to avoid false positives
            ret, frame = cap.read()
            if ret:
                prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                prev_frame = cv2.GaussianBlur(prev_frame, (21, 21), 0)
            continue

        prev_frame = gray

    cap.release()
    print("Motion detection ended.")

if __name__ == "__main__":
    main()
