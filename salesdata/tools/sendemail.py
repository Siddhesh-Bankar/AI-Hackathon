from crewai.tools import BaseTool
from litellm import Type
from pydantic import BaseModel, Field
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate the user and return the Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(r'D:\arieotech\AI Hackathon\Latest Project Data\AI-Hackathon\salesdata\tools\client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
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
    
    msg = MIMEText(message_text)
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, sender, to, subject, message_text):
    """Send an email message using Gmail API."""
    try:
        message = create_message(sender, to, subject, message_text)
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print(f'Message sent: {sent_message["id"]}')
    except HttpError as error:
        print(f'An error occurred: {error}')

class SendEmailInput(BaseModel):
    message_text: str = Field(..., description="Body content of the email")

class SendEmailTool(BaseTool):
    name: str = "Send Email"
    description: str = "Sends an email to a specified recipient"
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(self,message_text: str) -> str:
        try:
            print("Message from sendmail",message_text)
            print("EmailTask")
            service = authenticate_gmail()
            sender_email = "shelarpooja21@gmail.com"
            body = message_text

            send_message(service, sender_email, "sarthakdongre0303@gmail.com", "mail from crew", body)
            return f"Email sent successfully to {sender_email}"
        except Exception as e:
            return f"Error sending email: {str(e)}"