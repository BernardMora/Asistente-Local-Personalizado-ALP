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

def load_functions(file_path):
    with open(file_path, "r") as file:
        functions = json.load(file)
    return ",".join([json.dumps(function) for function in functions])

class LLM():
    def __init__(self):
        self.llm = Ollama(model="llama3")
        self.model = "llama3"
        self.functions = load_functions("speech_assistant_tuto/functions.json")


    def create_prompt_message(self, text):
        messages = [
                    {"role": "assistant", "content": "You are a local assistant who will help me achieve the tasks that I ask you to do. This means that you will be able to perform tasks such as sending emails, opening websites, and even controlling my computer. You will be able to do this by calling the functions that I have defined for you. You can ask me to do things like 'send an email', 'open a website', or 'control my computer'. I will provide you with the necessary information to complete these tasks. If I ask you to do something that you are not sure how to do, you can ask me for help. I will be happy to help you with any questions you may have."},

                    {"role": "user", "content": "Input text: " + text},

                    {"role": "user", "content": """Based on the input text that you will recieve, determine the function to be called, any necessary arguments, and a breif description in the form of a message of the set of instructions to be done. Provide your output in the following JSON format:
                    {"function_name": "...","arguments": {{ ... }},"message": "..."}
                    """},

                    # {"role": "user", "content": """Here are is the list of functions that you can call along with their arguments. Keep in mind, these are templates, the actual values of the arguments and the message may change depending on the input text. The only, things you must keep the same are: the function name, and the name of the argument keys. The functions are as follows:
                    
                    # """ + self.functions},

                    # {"role": "user", "content": "If you are asked to perform a task that you are not sure how to do, you will need to tell the me that you do not have the information to complete this task, based on my input, you will suggest a new function that could be created in order to complete this task. You will need to provide the function name, the arguments, and a message that describes the set of instructions to be done. You will ask for user input on the creation of this function, If you recieve a negative response: you will just say that you could not complete the task. If you recieve a positive response: you will need to provide your output in the JSON format described previously (function name, arguments, and template message) as well as a code snippet on the implementation of that task in python. If the user asks for a new function, you will ask for a description of the function and have the same behaviour as before"},

                    # {"role": "assistant", "content": "Do not respond to this first prompt, as it is only the prompt for configuration."}
                ]
        
        
        return messages

    def process_functions(self, text):
        print("Texto: ", text)
        messages = self.create_prompt_message(text)
        print("Messages: ", messages)

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
    
