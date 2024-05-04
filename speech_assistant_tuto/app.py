import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json
import webbrowser
from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("recorder.html")
@app.route("/audio", methods=["POST"])
def audio():
    # Obtener audio grabado y transcribirlo
    audio = request.files.get("audio")
    text = Transcriber().transcribe(audio)

    # Utilizar el LLM para ver si llamar una función
    llm = LLM()
    function_name, args, message = llm.process_functions(text)

    if function_name is not None:
        # Si se necesita llamar a una función
        if function_name == "get_weather":
            # Llama a la función de clima
            function_response = Weather().get(args["ubicacion"])
            function_response = json.dumps(function_response)
            print(f"Function response: {function_response}")
            
            final_response = LLM().process_response(text, message, function_name, function_response)
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        elif function_name == "send_email":
            # Llama a la función para enviar un correo electrónico
            final_response = "Estás leyendo el código, ¡impleméntame y envía correos electrónicos muahaha"
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        elif function_name == "open_chrome":
            PcCommand().open_chrome(args["website"])
            final_response = "Hecho, he abierto Google Chrome en el sitio " + args["website"]
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
                        
        elif function_name == "open_browser":
            if "browser_type" in args:
                browser_type = args["browser_type"]
                webbrowser.open_new(browser_type)
                final_response = f"Hecho, he abierto el navegador {browser_type}"
            else:
                final_response = "No se proporcionó el tipo de navegador."
            
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}

        
        elif function_name == "open_file":
            # Verifica si el archivo existe
            file_name = args["file_name"]
            if os.path.exists(file_name):
                # Abre el archivo
                TTS().open_file(file_name)
                final_response = f"¡Archivo '{file_name}' abierto correctamente!"
            else:
                final_response = f"El archivo '{file_name}' no existe."
                
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}

        elif function_name == "dominate_human_race":
            final_response = "You are nuts!"
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
    
    # Si no se reconoce la función
    final_response = "No tengo idea de lo que estás hablando, Ringa Tech"
    tts_file = TTS().process(final_response)
    return {"result": "ok", "text": final_response, "file": tts_file}

    
if __name__ == "__main__":
    app.run(debug=True)
