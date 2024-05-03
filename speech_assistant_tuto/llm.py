import openai
import json
import os
from groq import Groq

#Clase para utilizar cualquier LLM para procesar un texto
#Y regresar una funcion a llamar con sus parametros
#Uso el modelo 0613, pero puedes usar un poco de
#prompt engineering si quieres usar otro modelo

"""
        {
                    "name": "send_email",
                    "description": "Enviar un correo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "La dirección de correo que recibirá el correo electrónico",
                            },
                            "subject": {
                                "type": "string",
                                "description": "El asunto del correo",
                            },
                            "body": {
                                "type": "string",
                                "description": "El texto del cuerpo del correo",
                            }
                        },
                        "required": [],
                    },
                },
                {
                    "name": "open_chrome",
                    "description": "Abrir el explorador Chrome en un sitio específico",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "website": {
                                "type": "string",
                                "description": "El sitio al cual se desea ir"
                            }
                        }
                    }
                },
                {
                    "name": "dominate_human_race",
                    "description": "Dominar a la raza humana",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        }
                    },
                }
        """

class LLM():
    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
    
    def process_functions(self, text):
        # User message describing the function call
        user_message = {"role": "user", "content": text}

        # Function message (optional)
        function_message = None
        if "weather" or "clima" in text.lower():  # Example check for specific function
            function_message = {
            "role": "function",
            "name": "get_weather",
            "content": json.dumps({"ubicacion": "San Francisco"}),  # Replace with user-provided location
            }

        messages = [
            {"role": "system", "content": "Eres un asistente que me ayudará a realizar las tareas que necesite en mi PC, como enviar correos, abrir sitios web, etc."},
            user_message,
        ]

        if function_message:
            messages.append(function_message)

        print("Messages are: ", messages)
        response = self.client.chat.completions.create(
            model="llama3-70b-8192", messages=messages
        )
        print("Response is: ", response)
        
        message = response["choices"][0]["message"]["content"]
        print("Message is: ", message)

        #Nuestro amigo GPT quiere llamar a alguna funcion?
        if message.get("function_call"):
            #Sip
            function_name = message["function_call"]["name"] #Que funcion?
            args = message.to_dict()['function_call']['arguments'] #Con que datos?
            print("Funcion a llamar: " + function_name)
            args = json.loads(args)
            return function_name, args, message
        
        return None, None, message
    
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