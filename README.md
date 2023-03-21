To run the chatbot on telegram:
1. Start ngrok http 5005 on desktop
The https link generated should be modified in credentials.yml
2. Use the command to run on telegram: python -m rasa run --enable-api --cors "*"
3. Also run actions server through the cmd: python -m rasa run action

