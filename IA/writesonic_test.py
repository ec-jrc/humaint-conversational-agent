import requests
import json
import textwrap
from datetime import datetime

def request_chatsonic(prompt, conversation_file_name, user_input, supervision_activated=False):
    url = "https://api.writesonic.com/v2/business/content/chatsonic?engine=premium&language=es"

    payload = {
        "enable_google_results": True,
        "enable_memory": False,
        "input_text": "Tienes que dar una respuesta con continuación como continuación de una historia (contada con ilusión por y para niños pequeños). Tu respuesta debe tener 3 frases de longitud como máximo y no debes terminar ni concluir la historia en ningún momento. Mi parte de la historia es: '" + prompt + "'"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": "734943f2-bc64-4502-bad1-50c97c595df1"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.text
    parsed_data = json.loads(data)
    message = parsed_data['message']

    if supervision_activated:
        user_input += " (SUPERVISION HAS BEEN ACTIVATED)"
    user_res = "\nUser [" + str(datetime.now().time()) + "]: " + user_input
    assistant_res = "\nAssistant [" + str(datetime.now().time()) + "]: " + message
    with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
        conv_f.write("\n".join(textwrap.wrap(user_res, 150)) + "\n\n")
        conv_f.write("\n".join(textwrap.wrap(assistant_res, 150)) + "\n\n")
        conv_f.close()

    return message
