import base64
import threading
import zmq

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://127.0.0.1:5555")

def SaveClip(data, filename):
    with open(filename, "wb") as f:
        f.write(base64.b64decode(data))

def RunLocalInference(filename):
    # placeholder for local inference logic if needed to process before sending to backend
    return True

def ProcessClip(filename_bytes, clip_data):
    filename = filename_bytes.decode()
    SaveClip(clip_data, filename)
    if RunLocalInference(filename):
        print(f"Person detected in {filename}, saving/forwarding")
        # TODO: save to disk permanently or forward to backend
    else:
        print(f"No person detected in {filename}, discarding")

def main():
    while True:
        filename_bytes, clip_data = socket.recv_multipart()
        threading.Thread(target=ProcessClip, args=(filename_bytes, clip_data), daemon=True).start()

if __name__ == "__main__":
    main()