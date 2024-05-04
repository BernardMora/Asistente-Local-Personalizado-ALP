import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json

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
    # Obtain audio recorded and transcribe it
    audio = request.files.get("audio")
    text = Transcriber().transcribe(audio)

    #Utilizar el LLM para ver si llamar una funcion
    llm = LLM()
    function_name, args, message = llm.process_functions(text)

    if function_name is not None:
        # If a function needs to be called
        if function_name == "get_weather":
            # Call the weather function
            function_response = Weather().get(args["ubicacion"])
            function_response = json.dumps(function_response)
            print(f"Function response: {function_response}")
            
            final_response = LLM().process_response(text, message, function_name, function_response)
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        elif function_name == "send_email":
            # Call the function to send an email
            final_response = "You're reading the code, implement me and send emails muahaha"
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        elif function_name == "open_chrome":
            PcCommand().open_chrome(args["website"])
            final_response = "Done, I've opened chrome on the site " + args["website"]
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
                
        elif function_name == "open_file":
            # Check if the file exists
            file_name = args["file_name"]
            if os.path.exists(file_name):
                # Open the file
                TTS().open_file(file_name)
                final_response = f"File '{file_name}' opened successfully!"
            else:
                final_response = f"File '{file_name}' does not exist."
                
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}

        
        elif function_name == "dominate_human_race":
            final_response = "Don't believe it. Subscribe to the channel!"
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
    else:
        final_response = "I have no idea what you're talking about, Ringa Tech"
        tts_file = TTS().process(final_response)
        return {"result": "ok", "text": final_response, "file": tts_file}
    
if __name__ == "__main__":
    app.run(debug=True)
