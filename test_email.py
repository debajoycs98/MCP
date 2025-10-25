import resend
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
resend.api_key = os.getenv("RESEND_API_KEY")

r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "debajoymukherjeephdtamu@gmail.com",
  "subject": "Hello World",
  "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
})





