import os
import smtplib
import time
from dotenv import load_dotenv
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = 'smart-doorbell.json'
FOLDER_ID = 'replace_with_your_folder_id'
VIDEO_FOLDER = '/home/USER/good'
UPLOADED_LOG = 'uploaded.log'
SCOPES = ['https://www.googleapis.com/auth/drive']

# load credentials and build service once
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds, cache_discovery=False)

load_dotenv()
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

def SendEmailNotification(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Notification sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"Email failed: {e}")

def UploadVideo(file_path):
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
    media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
    try:
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        file_link = uploaded_file.get('webViewLink')
        print(f"Uploaded '{file_name}' with file ID: {uploaded_file.get('id')}")
        SendEmailNotification(
            subject="Doorbell Clip Uploaded",
            body=f"A new video '{file_name}' was uploaded.\nView it here:\n{file_link}"
        )
        return True
    except Exception as e:
        print(f"Upload failed for {file_name}: {e}")
        return False

def LoadUploaded():
    if not os.path.exists(UPLOADED_LOG):
        return set()
    with open(UPLOADED_LOG, 'r') as f:
        return set(line.strip() for line in f)

def MarkUploaded(file_name):
    with open(UPLOADED_LOG, 'a') as f:
        f.write(file_name + '\n')

def GetNewVideo(uploaded):
    try:
        files = [f for f in os.listdir(VIDEO_FOLDER)
                 if f.endswith('.mp4') and f not in uploaded]
        return files
    except Exception as e:
        print(f"Error reading video folder: {e}")
        return []

def main():
    print(f"Watching folder: {VIDEO_FOLDER}")
    uploaded = LoadUploaded()
    while True:
        new_files = GetNewVideo(uploaded)
        if new_files:
            for file in new_files:
                full_path = os.path.join(VIDEO_FOLDER, file)
                if UploadVideo(full_path):
                    uploaded.add(file)
                    MarkUploaded(file)
        time.sleep(5)

if __name__ == '__main__':
    main()
