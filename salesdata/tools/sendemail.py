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
from mailersend import emails
from dotenv import load_dotenv
import mailersend
from mailersend import emails
import mailtrap as mt

load_dotenv()

MAILTRAP_TOKEN=st.secrets["MAILTRAP_TOKEN"]

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
           

            mail = mt.Mail(
                sender=mt.Address(email="hello@demomailtrap.com", name="Mailtrap Test"),
                to=[mt.Address(email="demohackathon894@gmail.com")],
                subject="Insights",
                text=message_text,
                category="Integration Test",
            )

            client = mt.MailtrapClient(token=MAILTRAP_TOKEN)
            response = client.send(mail)

            print(response)
        except Exception as e:
            return f"Error sending email: {str(e)}"