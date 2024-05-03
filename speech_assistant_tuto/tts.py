import os
from dotenv import load_dotenv
import requests

class TTS():
    def __init__(self):
        load_dotenv()
        self.key = os.getenv('ELEVENLABS_API_KEY')
    
    def open_file(self, file_path):
        os.system(f'start {file_path}')  # Esto abre el archivo con el programa predeterminado en Windows

    def process(self, text):
        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.key
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v1",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.55
            }
        }

        # Guardar el archivo de audio generado en una ubicación temporal
        file_name = "response.mp3"
        response = requests.post(url, json=data, headers=headers)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        
        # Devolver el nombre del archivo generado para su posterior manipulación
        return file_name
