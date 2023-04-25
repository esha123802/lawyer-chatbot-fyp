To run the chatbot on telegram:
1. Start ngrok http 5005 on desktop
The https link generated should be modified in credentials.yml
2. Activate conda environment by: conda activate rasa_env
3. Use the command to run on telegram: python -m rasa run --enable-api --cors "*"
4. Also run actions server through the cmd: python -m rasa run actions

Changes made in code: 
1. python -m rasa train
2. python -m rasa shell (if on cmd)