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

#url定義。root url+/webhook でアクセス
@app.route('/webhook', methods=['POST'])
def webhook():
    audio_file=request.files['wav']
    hints=request.form.getlist('hints')
    
    #サービスアカウントの情報を読み込む。ここで、ダウンロードしたjsonのパスを指定。
    credentials = service_account.Credentials.from_service_account_file('xxxxxx.json')
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
    
    #帰ってきたレスポンスのうち、リスト"results"の中の"alternatives"の0番目の"transcript"に、
    #認識結果が入っているので、それだけを取り出す。
    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))
        text+=result.alternatives[0].transcript


    #レスポンスを返却。辞書を渡すとレスポンスを作成してくれる。
    #この例では{"text" : "認識結果"}というレスポンスが返ってくる。
    r = make_response(jsonify({'text':text}))
    r.headers['Content-Type'] = 'application/json'
    
    return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
