import os
from xml.dom.minidom import Document
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json
import webbrowser
from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ProjectInstruction import ProjectInstruction

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
    # Obtener audio grabado y transcribirlo
    audio = request.files.get("audio")
    text = Transcriber().transcribe(audio)

    # Utilizar el LLM para ver si llamar una función
    llm = LLM()
    function_name, args, message = llm.process_functions(text)
    print(f"Function name: {function_name}, Args: {args}, Message: {message}")

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
        
        elif function_name == "create_file":
            print("Enters the function")
            # Extract file name and content from args and message
            file_name = args["filename"]  # Assuming 'args' contains the file name
            content = args["content"]  # Assuming 'message' contains the content to write

            try:
                create_document(file_name, content)
                final_response = f"File '{file_name}' created with content."
            except Exception as e:
                final_response = f"Failed to create file '{file_name}'. Error: {e}"

   
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
            file_name = args.get("file_name")  # Assuming 'args' contains the file name
            new_content = message  # Assuming 'message' contains the new content to append

            transcriptions_dir = "transcriptions"
            if not os.path.exists(transcriptions_dir):
                os.makedirs(transcriptions_dir)

            file_path = os.path.join(transcriptions_dir, f"{file_name}.txt")

            # Append new content to the file
            edit_document_response = edit_document(file_path, new_content)

            final_response = edit_document_response
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}

        elif function_name == "create_file":
            # Assuming 'args' is a dictionary containing 'file_name' and 'message' contains the content to write
            file_name = args["file_name"]  
            content = args["content"]

            create_document_response = create_document(file_name, content)

            final_response = create_document_response
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        elif function_name == "open_project":
            # Open postgreSQL
            ProjectInstruction().execute()
            # Open a vscode window with the project
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": "Opening IronWine project", "file": tts_file}
    
    
    # Si no se reconoce la función
    final_response = "No tengo idea de lo que estás hablando, Ringa Tech"
    tts_file = TTS().process(final_response)
    return {"result": "ok", "text": final_response, "file": tts_file}

    
if __name__ == "__main__":
    app.run(debug=True)

def create_document(file_name, content):
    transcriptions_dir = "transcriptions"
    if not os.path.exists(transcriptions_dir):
        os.makedirs(transcriptions_dir)

    file_path = os.path.join(transcriptions_dir, f"{file_name}.txt")

    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return f"File '{file_path}' created with content."
    except Exception as e:
        return f"Failed to create file '{file_path}'. Error: {e}"


def edit_document(file_path, new_content):
    # Check if the file exists at the specified path
    if os.path.exists(file_path):
        try:
            # Open the file to append content
            with open(file_path, 'a') as file:
                file.write(new_content + "\n")
            return f"Document {file_path} updated successfully."
        except Exception as e:
            return f"An error occurred while writing to {file_path}: {e}"
    else:
        # Handle the case where the file does not exist
        return f"Error: The file {file_path} does not exist."
