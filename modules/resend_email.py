import os
import resend

resend.api_key = os.environ.get('RESEND_API_KEY')

params = {
    "from": "noreply@mail.comfyflow.app",
    "to": ["yexingren23@126.com"],
    "subject": "hello world",
    "html": "<strong>it works!</strong>",
}

email = resend.Emails.send(params)
print(email)