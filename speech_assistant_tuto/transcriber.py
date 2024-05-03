import whisper

#Convertir audio en texto
class Transcriber:
    def __init__(self):
        # Load the whisper model
        self.model = whisper.load_model("base")

    #Siempre guarda y lee del archivo audio.mp3
    #Utiliza whisper en la nube :) puedes cambiarlo por una impl local
    def transcribe(self, audio):
        # Save the audio file
        audio.save("audio.mp3")

        # Transcribe the audio using whisper
        result = self.model.transcribe("audio.mp3")
        print("Resultado: ", result)
        # Return the transcribed text
        return result["text"]