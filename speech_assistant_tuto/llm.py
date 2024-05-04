import json
import os
import requests
from tts import TTS
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import re

#Clase para utilizar cualquier LLM para procesar un texto
#Y regresar una funcion a llamar con sus parametros
#Uso el modelo 0613, pero puedes usar un poco de
#prompt engineering si quieres usar otro modelo

class LLM():
    def __init__(self):
        self.llm = Ollama(model="llama3")
        self.model = "llama3"

    def process_functions(self, text):
        print("Texto: ", text)

        messages = [
            {"role": "assistant", "content": "You are a local assistant who will help me achieve the tasks that I ask you to do. This means that you will be able to perform tasks such as sending emails, opening websites, and even controlling my computer. You will be able to do this by calling the functions that I have defined for you. You can ask me to do things like 'send an email', 'open a website', or 'control my computer'. I will provide you with the necessary information to complete these tasks. If I ask you to do something that you are not sure how to do, you can ask me for help. I will be happy to help you with any questions you may have."},

            {"role": "user", "content": "Input text: " + text},

            {"role": "assistant", "content": """Based on the input text, determine the function to be called, any necessary arguments, and a breif description in the form of a message of the set of instructions to be done. Provide your output in the following JSON format:
            
            {{
                "function_name": "...",
                "arguments": {{ ... }},
                "message": "..."
            }}
            """},
        ]
        # Use the LLMChain to process the input text and get the function call
        response = self.llm.invoke(messages)
        # Use the LLMChain to process the input text
        if not response:
            final_response = "No response received from Llama3"
            tts_file = TTS().process(final_response)
            return {"result": "error", "text": final_response, "file": tts_file}
        print("Response: ", response)


        # Find the start and end indices of the JSON object in the string
        start_index = response.find("{")
        end_index = response.rfind("}") + 1

        # Extract the JSON object from the string
        json_str = response[start_index:end_index]

        # Convert the JSON string to a Python dictionary
        output_dict = json.loads(json_str)

        print("Output dict: ", output_dict)

        # Extract the function name and arguments from the structured output
        function_name = output_dict["function_name"]
        arguments = output_dict["arguments"]
        message = output_dict["message"]

        return function_name, arguments, message
    

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
