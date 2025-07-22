# Smart Doorbell System

This project implements a smart doorbell system using NVIDIA Jetson Nano for motion detection and Raspberry Pi 5 for object detection inferencing. The system streams video, detects motion, records clips, performs human detection, and uploads relevant videos to Google Drive through Google Cloud's API.

## Project Structure

```
src/
  googleDriveUpload.py      # uploads detected clips to Google Drive and sends email notification
  human_object_detection.py # runs person detection on incoming video clips (Raspberry Pi 5)
  motion_detection.py       # detects motion and records video clips (Jetson Nano)
  pi_pull.py                # receives clips from Jetson Nano and runs local inference
```

## Setup Guide

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/video-doorbell.git
cd video-doorbell
```

### 2. Install Dependencies

- On both Jetson Nano and Raspberry Pi 5, install Python 3.8+ and pip.
- Install required Python packages:

```sh
pip install -r yolov5/requirements.txt
pip install ultralytics python-dotenv google-api-python-client
```

### 3. Configure Settings

- **Google Drive Upload:**
  - Place your Google service account JSON in the repo as `smart-doorbell.json`.
  - Set your Google Drive folder ID in `src/googleDriveUpload.py`.
  - Create a `.env` file with your email credentials:
    ```
    EMAIL_SENDER=your_email@gmail.com
    EMAIL_PASSWORD=your_password
    EMAIL_RECEIVER=receiver_email@gmail.com
    ```

- **Edit IP Addresses:**
  - In `motion_detection.py`, set `RASPBERRY_PI_IP` to the actual IP address of your Raspberry Pi 5.

### 4. Run the Applications

- **On Jetson Nano (Motion Detection):**
  ```sh
  python src/motion_detection.py
  ```
- **On Raspberry Pi 5 (Object Detection and Google Cloud API):**
  ```sh
  python src/pi_pull.py
  python src/human_object_detection.py
  python src/google_cloud_interaction.py

  ```

  Once everything is up and running from the dry run, feel free to package everything into a single launcher through something like bash scripts.

## Workflow
![workflow_diagram](.\docs\video_doorbell_workflow_diagram.png)


## Usage

- Jetson Nano detects motion, records clips, and sends them to Raspberry Pi 5.
- Raspberry Pi 5 runs human detection on received clips and sorts them.
- Clips with detected persons are uploaded to Google Drive and trigger email notifications.

---

**Hardware Used:**
- NVIDIA Jetson Nano (motion detection, video recording)
- Raspberry Pi (object detection)