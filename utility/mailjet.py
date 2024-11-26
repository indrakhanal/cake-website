from mailjet_rest import Client
import os


def send_email_mailjet(request):
    api_key = '84ad78a22f5491a1e9b065f9fbe8cd96'
    api_secret = '7247297415339d6cad7d575d4fad0abf'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "alson.prasai55@gmail.com",
                    "Name": "Demo Name"
                },
                "To": [
                    {
                        "Email": "curious.benj5@gmail.com",
                        "Name": "passenger 1"
                    }
                ],
                "TemplateID": 1569674,
                "TemplateLanguage": True,
                "Subject": "Demo Subject",
                "Variables": {
                    "Heading": "Heading 123 Test",
                    "name": "Alson Test",
                    "button": "www.google.com"
                }

            }]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
