import base64, os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials      import Credentials
from google_auth_oauthlib.flow      import InstalledAppFlow
from googleapiclient.discovery      import build
from email.message                  import EmailMessage

SCOPES =['https://www.googleapis.com/auth/gmail.send']
class GoogleEmail:
    def __init__(self):
        self.credentials = {}

    def generate_token(self, token_file_path, credentials_file_path):
        temp_credentials = None
        
        if os.path.exists(token_file_path):
            temp_credentials = Credentials.from_authorized_user_file(token_file_path, SCOPES)
        
        if not temp_credentials or not temp_credentials.valid:
            if temp_credentials and temp_credentials.expired and temp_credentials.refresh_token:
                temp_credentials.refresh(Request())
        
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file_path, SCOPES)
                temp_credentials = flow.run_local_server(port=0)
        
            with open(token_file_path, 'w') as token:
                token.write(temp_credentials.to_json())
        
        self.credentials = temp_credentials

    def send_email(self, content, author, sender_email):
            service = build('gmail', 'v1', credentials = self.credentials)
            content = "제안자 : " + sender_email + "/n" + "제안 내용 : " + content
            message = EmailMessage()
            message.set_content(content)
            message['To']      = author.user.email
            message['From']    = "ebsgreat7@gmail.com"
            message['Subject'] = "작가" + author.user.name + '에게 제안메일 드립니다'

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message  = {
                'raw': encoded_message
            }

            send_message = service.users().messages().send(userId='me', body=create_message).execute()
            return send_message