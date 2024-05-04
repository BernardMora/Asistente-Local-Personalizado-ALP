import json
import os
from groq import Groq
import requests
from tts import TTS

#Clase para utilizar cualquier LLM para procesar un texto
#Y regresar una funcion a llamar con sus parametros
#Uso el modelo 0613, pero puedes usar un poco de
#prompt engineering si quieres usar otro modelo

class LLM():
    def __init__(self):
        self.endpoint = "http://localhost:11434/api/chat"
        self.model = "llama3"

# "context": self.context
    def send_to_model(self, messages):
        """Send message to Llama3 for processing."""
        data = {'model': self.model, 'messages': messages, "stream": False}
        response = requests.post(self.endpoint, json=data)
        return response.json()
    
    def process_functions(self, text):
        print("Texto recibido: ", text)
        # Send the transcribed text to Llama3 with the model name
        messages = [
            {"role": "assistant", "content": "You are a local assistant who will help me achieve the tasks that I ask you to do. This means that you will be able to perform tasks such as sending emails, opening websites, and even controlling my computer. You will be able to do this by calling the functions that I have defined for you. You can ask me to do things like 'send an email', 'open a website', or 'control my computer'. I will provide you with the necessary information to complete these tasks. If I ask you to do something that you are not sure how to do, you can ask me for help. I will be happy to help you with any questions you may have."},
            {"role": "user", "content": text},
        ]
        llama3_response = self.send_to_model(messages)
        print("Llama3 res", llama3_response)

        if not llama3_response:
            final_response = "No response received from Llama3"
            tts_file = TTS().process(final_response)
            return {"result": "error", "text": final_response, "file": tts_file}

        # Do something to interpret the user petition and translate it to a function call


        # Function message (optional)
        function_message = None
        function_name = None

        # Check for weather function
        if "tijuana" and ("weather" or "clima") in text.lower():
            function_message = {
            "role": "function",
            "name": "get_weather",
            "content": json.dumps({"ubicacion": "Tijuana, Baja California"}),
            }
            function_name = "get_weather"

        # Check for open_chrome function with search term extraction
        elif ("browser" or "chrome") in text.lower():
            search_term = extract_search_term(text)
            website = f"https://www.google.com/search?q={search_term}"
            function_message = {
            "role": "function",
            "name": "open_chrome",
            "content": json.dumps({"website": website}),
            }
            function_name = "open_chrome"

        # Append the function message if identified
        if function_message:
            messages.append(function_message)

        #Nuestro amigo GPT quiere llamar a alguna funcion?
        if function_message:
            args = llama3_response.to_dict()['function_call']['arguments'] #Con que datos?
            print("Funcion a llamar: " + function_name)
            args = json.loads(args)
            return function_name, args, llama3_response
        
        return None, None, llama3_response
    
    #Una vez que llamamos a la funcion (e.g. obtener clima, encender luz, etc)
    #Podemos llamar a esta funcion con el msj original, la funcion llamada y su
    #respuesta, para obtener una respuesta en lenguaje natural (en caso que la
    #respuesta haya sido JSON por ejemplo
    def process_response(self, text, message, function_name, function_response):
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                #Aqui tambien puedes cambiar como se comporta
                {"role": "system", "content": "Eres un asistente malhablado"},
                {"role": "user", "content": text},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        return response["choices"][0]["message"]["content"]
    
import re

def extract_search_term(text):
  """
  Extracts the search term from the user's text using regular expressions.

  Args:
      text: The user's spoken text.

  Returns:
      The extracted search term, or an empty string if no search term is found.
  """
  # Define a regular expression pattern to match search terms.
  # This pattern captures phrases like "search for", "look up", "find", etc. followed by one or more words.
  pattern = r"(search for|look up|find|.*\squery|.*\sbrowse) (.*)"
  match = re.search(pattern, text.lower())

  if match:
    # Extract the captured group (the search query)
    search_term = match.group(2)
    return search_term
  else:
    # No search term found
    return ""
