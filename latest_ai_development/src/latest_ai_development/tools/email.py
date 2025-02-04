Use the code from test.py file to send the mail 
#text.py
import os
import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying the email content, set the SCOPES to 'https://www.googleapis.com/auth/gmail.send'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate the user and return the Gmail API service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\siddhesh.bankar\Downloads\Desktop.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build the Gmail API service
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def create_message(sender, to, subject, message_text):
    """Create an email message."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Attach the body of the email to the MIME message
    msg = MIMEText(message_text)
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, sender, to, subject, message_text):
    """Send an email message."""
    try:
        message = create_message(sender, to, subject, message_text)
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print(f'Message sent: {sent_message["id"]}')
    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    sender = "siddheshbankar16@gmail.com"  # Replace with your email address
    to = "siddheshbankar16@gmail.com"  # Replace with the recipient's email address
    subject = "Test Email from Gmail API"
    message_text = "This is a test email sent using the Gmail API with Python."
    
    service = authenticate_gmail()
    if service:
        send_message(service, sender, to, subject, message_text)
