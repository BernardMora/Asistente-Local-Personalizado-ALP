import os
from xml.dom.minidom import Document
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json

from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand

app = Flask(__name__)

def create_document(file_name, content):
    document = Document()
    document.add_paragraph(content)
    document.save(file_name)
    
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
    print(f"Function name: {function_name}, Args: {args}, Message: {message}")

    if function_name is not None:
        if function_name == "open_website":
            PcCommand().open_chrome(args["url"])
            final_response = "Done, I've opened chrome on the site " + args["website"]
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        elif function_name == "create_file":
            # Extract file name and content from args and message
            file_name = args["filename"]  # Assuming 'args' contains the file name
            content = args["content"]  # Assuming 'message' contains the content to write

            try:
                create_document(file_name, content)
                final_response = f"File '{file_name}' created with content."
            except Exception as e:
                final_response = f"Failed to create file '{file_name}'. Error: {e}"

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
