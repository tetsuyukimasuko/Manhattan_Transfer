from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import os
import io

from flask import Flask
from flask import request
from flask import make_response, jsonify

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import google.auth
from google.oauth2 import service_account

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    audio_file=request.files['wav']
    hints=request.post['hints']

    credentials = service_account.Credentials.from_service_account_file('My First Project-f92e7a809607.json')
    if credentials.requires_scopes:
        credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])

    # Instantiates a client
    client = speech.SpeechClient(credentials=credentials)

    # Loads the audio into memory
    #with io.open(file, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

    contexts=[speech.types.SpeechContext(
            phrases=hints,
        )]

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='ja-JP',
        speech_contexts=contexts
        )

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    text=''

    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))
        text+=result.alternatives[0].transcript


    #返却
    r = make_response(jsonify({'text':text}))
    r.headers['Content-Type'] = 'application/json'
    
    return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
