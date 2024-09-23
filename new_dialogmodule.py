import json
import sys
import time
import unicodedata
import warnings
import random
import re
import googleapiclient.discovery
from google.cloud import dialogflow, dialogflow_v2
from google.cloud.dialogflow_v2.types import TextInput
from google.oauth2 import service_account
import googleapiclient.discovery
from gtts import gTTS
import os
import io
import asyncio
import supervision_module as spr_module
import remove_personal_data_test
from IA.writesonic_test import request_chatsonic as chat
import ASR_module as asr
#import chatgpt_bridge as gpt
from remove_personal_data_test import eliminar_info_personal as filter
from playsound import playsound
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame import mixer
from datetime import datetime
import keyboard
import textwrap
import string
from new_version import new_story as chat_game

mixer.init()

global conversation_file_name, config_json_file, num_times_not_understood, num_requests_repeat, \
    num_requests_more_info, interaction_interrupted_by_user

global suggested_stories_used
suggested_stories_used = {"1": "", "2": "", "3": "", "4": ""}

NOT_UNDERSTOOD_ANSWERS = {
    "es": [
        "¿Podrías repetirlo, por favor?",
        "¿Podrías decirlo de nuevo, por favor?",
        "¿Podrías repetirlo una vez más, por favor?"
    ],
    "it": [
        "Non ti ho sentito bene. Puoi ripetere?",
        "Non ho capito bene. Potresti ripetere?",
        "Potresti essere più specifico?",
        "Potresti dirlo ancora una volta?",
        "Non penso di seguirti. Potresti ripetere?",
        "Certo, potrei ripetere ancora una volta?",
        "Potresti dirlo ancora una volta?", 
        "Potresti repeterlo?",
        "Potresti dirlo di nuovo?",
        "Non penso di aver capito. Potresti ripetere?", 
        "Non ho capito. Potresti ripetere?"
    ]
}

MORE_INFO_REQUESTS = {
    "es": [
        "que eres",
        "que tu eres",
        "tu eres",
        "tú eres?",
        "y tú que eres",
        "¿y tú que eres?",
        "¿qué eres?",
        "qué eres",
        "cuéntame más sobre tí",
        "tu que haces",
        "¿tú que haces?",
        "hablame de ti",
        "¿te conozco?",
        "y tu quien eres?",
        "necesito saber de ti",
        "quien eres",
        "infórmame sobre ti",
        "necesito información",
        "y tú que haces",
        "y tu que haces",
        "que haces",
        "¿qué haces?",
        "qué haces",
        "cómo funcionas",
        "como funcionas",
        "¿y tú cómo funcionas?",
        "y como funcionas",
        "como funciona",
        "¿cómo funciona?",
        "cómo funciona"
    ],
    "it": [
        "parlami di te",
        "dimmi di più su di te",
        "mi dia informazioni su di lei",
        "e chi sei tu?",
        "chi sei",
        "ho bisogno di informazioni",
        "voglio informazioni"
    ]
}

REPEAT_REQUESTS = {
    "es": [
        "repite",
        "repitemelo",
        "me lo repites",
        "repítelo",
        "repite",
        "no lo entiendo",
        "no lo he entendido",
        "no, no lo he entendido"
    ],
    "it": [
        "ripeti",
        "dasripetilo",
        "ripetil",
        "ripetere",
        "non capisco",
        "non ho capito",
        "no, non ho capito"
    ]
}

NO_CONSENT = {
    "es": ["¡Vale! Por favor, comuníquele al menor que no me está permitido continuar con la conversación. ¡Adiós, muchas gracias!"],
    "it": ["OK! La prego di informare il bambino che non posso continuare la conversazione. Arrivederci, grazie mille!"]
}

# Lists all service accounts for the current project in DialogFlow
def list_service_accounts(project_id):
    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    service_accounts = service.projects().serviceAccounts().list(
        name='projects/' + project_id).execute()

    for account in service_accounts['accounts']:
        print('Name: ' + account['name'])
        print('Email: ' + account['email'])
        print(' ')
    return service_accounts


# Detect the intent of a specific text using the Dialogflow API and return the compliance text
def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = TextInput(text=text, language_code=language_code)
    query_input = dialogflow_v2.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result.fulfillment_text


def word_in_phrase_check(phrase, word):
    if (remove_accents(phrase).lower().find(word) != -1):
        return True
    else:
        return False

def text_to_speech(response, idioma):
    text_synthesized = False
    number_of_retries = 0
    while not text_synthesized and number_of_retries < 3:
        try:
            # Crear un objeto de voz
            if idioma.lower() == "es":
                tts = gTTS(text=response, lang='es')
            elif idioma.lower() == "it":
                tts = gTTS(text=response, lang='it')
            # Guardar el audio como un archivo MP3
            tts.save("hello.mp3")
            tts_audio = mixer.Sound("hello.mp3")
            tts_audio_task = tts_audio.play()
            while tts_audio_task.get_busy():
                pygame.time.wait(100)
            text_synthesized = True
            number_of_retries += 1
            pygame.time.wait(600)
        except: # If TTS fails, avoid crashing
            pygame.time.wait(600)
            number_of_retries += 1
            pass
    if not text_synthesized:
        print("THERE HAS BEEN AN ERROR CONNECTING TO TTS")
    
    pygame.time.wait(600)



# Remove the accent mark in a phrase
def remove_accents(text):
    text = unicodedata.normalize('NFD', text)
    output = ''
    for char in text:
        if unicodedata.category(char) != 'Mn':
            output += char
    return output


def search_vector(string, vector):
    for element in vector:
        if element == string:
            return True
    return False


def generate_greeting(idioma):
    presentacion = ""
    while (presentacion == ""):
        if idioma.lower() == "es":
            presentacion = "Hola, me llamo Flora, ¿Cómo te llamas?"
        elif idioma.lower() == "it":
            presentacion = "Ciao, mi chiamo Flora, tu come ti chiami?"
        if presentacion == "":
            print("Vuelve a introducir bien el idioma (español/ito): ", end="")
            idioma = input()
    return presentacion, idioma


async def get_transcription(idioma,conversation_file_name):
    if idioma.lower() == "es":
        print("Habla tú: ", end="")
    elif idioma.lower() == "it":
        print("Parla tu: ", end="")
    await asyncio.sleep(1)
    trans_res = ""
    while trans_res == "":
        # trans_res = input()
        trans_res = asr.transcription_result
        if trans_res != "":
            write_to_conversation_file(trans_res + "\n",conversation_file_name,"User")
            print(trans_res + "\n")
            asr.set_whisper_random_sentence_solved(False)
        await asyncio.sleep(1)
    return trans_res


async def get_transcription_text(idioma):
    if idioma.lower() == "es":
        print("Habla tú: ", end="")
    elif idioma.lower() == "it":
        print("Parla tu: ", end="")
    #await asyncio.sleep(5)
    trans_res = ""
    while trans_res == "":
        trans_res = input()
    return trans_res


async def dialog_flow(project_id, session_id, text, idioma):
    language_code = "es-ES"
    if idioma.lower() == "es":
        language_code = "es-ES"
    elif idioma.lower() == "it":
        language_code = "it-IT"

    response = detect_intent_texts(project_id, session_id, text, language_code)
    if response != "":
        warnings.simplefilter('ignore')
        # text_to_speech(response)
    else:
        text = "bye"
    sum_not_understood(response, idioma)
    return response


def confirm_delivery(idioma, trans_res):
    respuesta = ""
    if idioma.lower() == "es":
        while respuesta != "si" and respuesta != "no": 
            respuesta = input("Confirmar envio (Si o No): ")
        if respuesta.lower() == "si":
            return trans_res
        elif respuesta.lower() == "no":
            print("Escribe la respuesta: ", end="")
            return input()
    elif idioma.lower() == "it":
        while respuesta != "si" and respuesta != "no" and respuesta != "sì": 
            respuesta = input("Conferma spedizione (Sì o No): ")
        if respuesta.lower() == "sì" or respuesta.lower() == "si":
            return trans_res
        elif respuesta.lower() == "no":
            print("Scrivi la risposta: ", end="")
            return input()


def finish_first_part(idioma, age_range):
    primera_parte = ""
    if age_range == "1-7":
        if idioma.lower() == "es":
            primera_parte = ["¡Estupendo! ¡Vamos a empezar!"]# A ver ¿de qué quieres que vaya el cuento? ¿de sueños? ¿o de animales?"]
        elif idioma == "it" or idioma == "ito":
            primera_parte = ["Ottimo! Cominciamo!"]# Vediamo, di cosa vuoi che parli la storia: sogni, animali?"]
    elif age_range == "8-12":
        if idioma.lower() == "es":
            primera_parte = ["¡Genial!"]# A ver ¿de qué quieres que vaya el cuento? ¿de piratas? ¿o del espacio?"]
        elif idioma == "it" or idioma == "ito":
            primera_parte = ["Evviva!"]# Allora, di cosa vuoi che parli la storia? Pirati? O spazio?"]
    else:
        if idioma.lower() == "es":
            primera_parte = ["¡Estupendo! ¡Vamos a divertirnos!"]# A ver, elige uno de los siguientes temas. misterio o fantasía."]
        elif idioma == "it" or idioma == "ito":
            primera_parte = ["Fantastico! Divertiamoci un po'!"]# Vediamo, scegli uno dei seguenti temi: mistero o fantasy."]

    return primera_parte

def begin_second_part(idioma, age_range):
    second_part = ""
    if age_range == "1-7":
        if idioma.lower() == "es":
            second_part = "A ver ¿de qué quieres que vaya el cuento? ¿de sueños? ¿o de animales?"
        elif idioma == "it" or idioma == "ito":
            second_part = "Vediamo, di cosa vuoi che parli la storia: sogni, animali?"
    elif age_range == "8-12":
        if idioma.lower() == "es":
            second_part = "A ver ¿de qué quieres que vaya el cuento? ¿de piratas? ¿o del espacio?"
        elif idioma == "it" or idioma == "ito":
            second_part = "Allora, di cosa vuoi che parli la storia? Pirati? O spazio?"
    else:
        if idioma.lower() == "es":
            second_part = "A ver, elige uno de los siguientes temas. misterio o fantasía."
        elif idioma == "it" or idioma == "ito":
            second_part = "Vediamo, scegli uno dei seguenti temi: mistero o fantasy."

    return second_part

# Checks if a phrase contains keywords related to endings or stories.
def find_final(idioma, age_range):
    primera_parte = ""
    if age_range == "1-7":
        if idioma.lower() == "es":
            primera_parte = ["¡Claro! Tal vez podamos hablar en otro momento. Muchas gracias por tu tiempo. Adiós."]
        elif idioma == "it" or idioma == "ito":
            primera_parte = ["Certo! Magari possiamo parlare un'altra volta. Grazie mille per il tuo tempo. Ciao!"]
    elif age_range == "8-12":
        if idioma.lower() == "es":
            primera_parte = ["¡Claro! Tal vez podamos hablar en otro momento. Muchas gracias por tu tiempo. Adiós."]
        elif idioma == "it" or idioma == "ito":
            primera_parte = ["Certo! Magari possiamo parlare un'altra volta. Grazie mille per il tuo tempo. Ciao!"]
    else:
        if idioma.lower() == "es":
            primera_parte = ["Lo lamento mucho, espero que tu día sea estupendo. ¡Nos vemos en la próxima!"]
        elif idioma == "it" or idioma == "ito":
            primera_parte = ["Ok, un'altra volta. Buona giornata, alla prossima!"]

    return primera_parte


def remove_repeated_dots(text):
    # Remove repeated dots and extra spaces
    text = re.sub(r'\s*\.\s+', '. ', text)
    # Remove dots at the beginning
    text = re.sub(r'^\s*\.\s*', '', text)

    return text


def random_strings(idioma):
    strings = ["Vale, ahora voy yo. A ver cómo sigo con esto… dejame que piense…",
               "Vaya, ¡qué interesante se está poniendo esto! A ver cómo lo sigo… déjame pensar…",
               "¡Puaf! ¡Qué emocionante! A ver si puedo seguirte el ritmo… mmm…",
               "Wow ¡Cómo se están poniendo las cosas! A ver cómo lo sigo."]
    if idioma.lower() == "es":
        strings = ["Vale, ahora voy yo. A ver cómo sigo con esto… dejame que piense…",
                   "Vaya, ¡qué interesante se está poniendo esto! A ver cómo lo sigo… déjame pensar…",
                   "¡Puaf! ¡Qué emocionante! A ver si puedo seguirte el ritmo… mmm…",
                   "Wow ¡Cómo se están poniendo las cosas! A ver cómo lo sigo."]
    elif idioma.lower() == "it":
        strings = ["Ecco, ora tocca a me. Vediamo come proseguo con questo... lasciami pensare...",
                   "Oh, che interessante sta diventando tutto questo! Vediamo come proseguo... lasciami pensare...",
                   "Uau, che emozionante! Vediamo se riesco a seguirti... mmm...",
                   "Wow, come si stanno mettendo le cose! Vediamo come proseguo."]

    # random.shuffle(strings)
    return strings

def supervision_strings(idioma, supervision_n):
    supervision_string = ""
    if idioma.lower() == "es":
        if supervision_n < 2:
            supervision_string = "Oh! Vaya, lo siento, parece que ha habido un error. Por favor, vuelve a intentar continuar la historia."
        else:
            supervision_string = "¡Qué historia más chula!"
    elif idioma.lower() == "it":
        if supervision_n < 2:
            supervision_string = "OH! Scusa, sembra che ci sia stato un errore. Riprova per continuare la storia."
        else:
            supervision_string = "Che bella storia!"

    return supervision_string


def contains_majority_words(input_string):
    word_list = ["ahora", "continua", "tu"]
    word_count = len(word_list)
    words_found = 0

    for word in word_list:
        if word in input_string:
            words_found += 1

    # Check if the string contains all or the majority of the words
    if words_found >= (word_count / 2):
        return True
    else:
        return False


def last_sentence(idioma, age_range):
    contestacion = ""
    if age_range == "1-7":
        if idioma.lower() == "es":
            contestacion = "Bueno, muchas gracias por el juego. ¡Ha quedado un cuento chulísimo! Espero que te lo hayas pasado muy bien."
        elif idioma.lower() == "it":
            contestacion = "Beh, grazie mille per il gioco, abbiamo creato è una storia fantastica! Spero che ti sia divertito!"
    elif age_range == "8-12":
        if idioma.lower() == "es":
            contestacion = "¡Puaf! Ha estado bien ¿no? Espero que hayas disfrutado."
        elif idioma.lower() == "it":
            contestacion = "È stato bello, vero? Spero che ti sia piaciuto."
    else:
        if idioma.lower() == "es":
            contestacion = "¡Estoy muy contento! Nos ha quedado una historia muy buena."
        elif idioma.lower() == "it":
            contestacion = "Sono molto felice! Abbiamo fatto una storia molto bella."

    return contestacion

def write_to_conversation_file(text, conversation_file_name, agent=""):
    if agent != "":
        msg = agent + " [" + str(datetime.now().time()) + "]: " + text
    else:
        msg = text

    # Directorio de la carpeta de conversación
    conversation_folder = "conversation_files"
    if not os.path.exists(conversation_folder):
        os.makedirs(conversation_folder)

    with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
        conv_f.write("\n".join(textwrap.wrap(msg, 150)) + "\n\n")
        conv_f.close()


def write_to_story_file(text, story_file):
    conversation_folder = "story_files"
    if not os.path.exists(conversation_folder):
        os.makedirs(conversation_folder)

    with open("story_files/" + story_file, "a", encoding="utf-8") as story_f:
        story_f.write("\n".join(textwrap.wrap(text, 150)) + "\n\n")
        story_f.close()

def edit_suggested_stories_used(num_suggestion, is_used):
    global suggested_stories_used
    suggested_stories_used[str(num_suggestion)] = is_used

def sum_more_info_request(trans, idioma, config_json_file):
    if trans in MORE_INFO_REQUESTS[idioma]:
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            current_times = int(json_data["num_requests_more_info"])
            current_times += 1
            json_data["num_requests_more_info"] = str(current_times)
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()

def sum_not_understood(response, idioma, config_file=""):
    global config_json_file
    if config_file != "":
        config_json_file = config_file
    if response in NOT_UNDERSTOOD_ANSWERS[idioma] or response == "not-understood":
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            current_times = int(json_data["num_times_not_understood"])
            current_times += 1
            json_data["num_times_not_understood"] = str(current_times)
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()

def sum_request_repeat(trans, idioma, config_json_file):
    if trans in REPEAT_REQUESTS[idioma]:
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            current_times = int(json_data["num_requests_repeat"])
            current_times += 1
            json_data["num_requests_repeat"] = str(current_times)
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()

def set_is_interrupted_by_user(response, final, idioma):
    global config_json_file
    if search_vector(response, final) or response in NO_CONSENT[idioma]:
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            json_data["interaction_interrupted_by_user"] = "yes"
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()
        return True
    return False

async def main():
    global conversation_file_name, config_json_file, suggested_stories_used
    # Eliminar warning en terminal
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    id = input("Enter user id: ")
    age = input("Enter user age: ")
    age_range = remove_personal_data_test.detectar_rango(str(age))
    
    """ Decidimos el modulo por edades """
    if age_range == "1-7":
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "modulodialogo8-configure.json"
        project_id = "modulodialogo8-hq9y"
        session_id = "modulodialogo8-hq9y_session_id"
    elif age_range == "8-12":
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "modulodialogo12-configure.json"
        project_id = "modulodialogo12-mjmc"
        session_id = "modulodialogo12-mjmc_session_id"
    else:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "modulodialogo-configure.json"
        project_id = "modulodialogo-pabu"
        session_id = "modulodialogo-pabu_session_id"

    print("Creating user files...")
    date_now = datetime.now()

    timestamp_id = date_now.strftime("%d") + "-" + date_now.strftime("%m") + "-" + \
                   date_now.strftime("%H") + "-" + date_now.strftime("%M") + "-" + id
    conversation_file_name = timestamp_id + ".txt"

    # Directorio de la carpeta de conversación
    conversation_folder = "conversation_files"
    if not os.path.exists(conversation_folder):
        os.makedirs(conversation_folder)

    # Creating conversation_file
    with open("conversation_files/" + conversation_file_name, "w", encoding="utf-8") as conv_f:
        pass

    # Creating config_file
    init_conf_json = {"id": id, "accuracy_ptg_1": "", "accuracy_ptg_2": "", "accuracy_sentence_detected_1": "", "accuracy_sentence_detected_2": "",
                      "conversation_file": conversation_file_name,
                      "age_range": age_range, "conv_time": "", "num_times_not_understood": "0", "num_requests_repeat": "0",
                      "num_requests_more_info": "0", "interaction_interrupted_by_user": "no", "password_given": "",
                      "suggested_stories_used": {}}
    config_json_file = timestamp_id + ".json"

    conversation_folder = "user_config_files"
    if not os.path.exists(conversation_folder):
        os.makedirs(conversation_folder)
    with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as conf_f:
        json.dump(init_conf_json, conf_f, indent=4)
        conf_f.close()

    # Acceder al idioma configurado previamente
    CONFIG_PATH = "config.json"
    with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
        configs = json.load(config)
    idioma = configs['LANGUAGE']
    name_bot = configs['NAME_BOT']

    print('\nStarting listener\n')
    write_to_conversation_file('\nStarting listener\n', conversation_file_name, "System")
    listener_task = asyncio.create_task(asr.process_input_audio(conversation_file_name, config_json_file))
    asr.pause_recognition(True)
    primera_parte = finish_first_part(idioma, age_range)
    final = find_final(idioma, age_range)
    is_interrupted = False
    response = ""

    """ CONFIGURACION DE SONIDO AMBIENTE """
    asr.pause_recognition(False)
    print("CHECK 1: Keep in silence for 3s")
    write_to_conversation_file("CHECK 1: Keep in silence for 3s", conversation_file_name, "System")
    while not asr.ambience_level_checked or not asr.accuracy_checked:
        await asyncio.sleep(1)
        trans_res = asr.transcription_result
        if trans_res != "":
            asr.set_transcription_result("")
    print("Checks Done!")
    write_to_conversation_file("Checks Done!", conversation_file_name, "System")
    start = input("Should we start the conversation? (y/n):")
    program_part = '0'
    if start.lower() == "y":
        program_part = input("Where do you want to start (1.System intro,2.Story,3.Eval. story,4.Eval. pwd):")

    if program_part == '1':
        """ PRIMERA PARTE DEL DIALOGO (PREVIO A LA HISTORIA) """

        asr.pause_recognition(True)

        """ Comenzamos el dialogo en DialogFlow """
        if idioma.lower() == "es":
            response = await dialog_flow(project_id, session_id, "Hola", idioma)
        elif idioma.lower() == "it":
            response = await dialog_flow(project_id, session_id, "Ciao", idioma)
        print(name_bot, response)
        write_to_conversation_file(response, conversation_file_name, name_bot)
        text_to_speech(response, idioma)

        while response != "" and not search_vector(response, primera_parte) and not search_vector(response, final):
            is_interrupted = set_is_interrupted_by_user(response, final, idioma)
            if is_interrupted:
                break
            asr.pause_recognition(False)
            if response != "":
                trans_res = await get_transcription(idioma,conversation_file_name)
                #trans_res = confirm_delivery(idioma, trans_res)
            if trans_res != "":
                if not search_vector(response, primera_parte):
                    # Dialog
                    response = await dialog_flow(project_id, session_id, trans_res, idioma)
                    asr.pause_recognition(True)
                    if response != "":
                        print(name_bot, "\n".join(textwrap.wrap(response, 150)))
                        write_to_conversation_file(response, conversation_file_name, name_bot)
                        text_to_speech(response, idioma)
                    asr.pause_recognition(False)
                asr.set_transcription_result("")
        if not is_interrupted:
            program_part = '2'

    if program_part == '2':
        conversation_folder = "story_files"
        if not os.path.exists(conversation_folder):
            os.makedirs(conversation_folder)
        # Creating story_file
        with open("story_files/" + conversation_file_name, "w", encoding="utf-8") as conv_f:
            pass
        """ SEGUNDA PARTE DEL DIALOGO (HISTORIA) """
        print(name_bot, "\n".join(textwrap.wrap(begin_second_part(idioma, age_range), 150)))
        write_to_conversation_file(begin_second_part(idioma,age_range),conversation_file_name,name_bot)
        asr.pause_recognition(True)
        text_to_speech(begin_second_part(idioma, age_range), idioma)
        asr.pause_recognition(False)
        asr.set_transcription_result("")
        if response != "":
            is_interrupted = set_is_interrupted_by_user(response, final, idioma)
        if not is_interrupted:
            if not search_vector(response, final):
                await chat_game.run_new_game(conversation_file_name, name_bot, age_range)

        """ TERCERA PARTE DEL DIALOGO (FINAL) """
        is_interrupted = set_is_interrupted_by_user(response, final, idioma)
        if not is_interrupted:
            if trans_res != "" and not search_vector(response, final):
                if not search_vector(response, primera_parte):
                    # Dialog
                    write_to_conversation_file(trans_res, conversation_file_name, "User")
                    response = await dialog_flow(project_id, session_id, trans_res, idioma)
                    asr.pause_recognition(True)
                    if response != "":
                        print(name_bot + ": ", "\n".join(textwrap.wrap(response, 150)))
                        write_to_conversation_file("\n".join(textwrap.wrap(response, 150)), conversation_file_name, name_bot)
                    text_to_speech(response, idioma)
                    asr.pause_recognition(False)
                asr.set_transcription_result("")
            program_part = '3'

    if program_part == '3':
        """ HISTORIA DE EVALUACIÓN """
        suggested_stories_used = await chat_game.run_eval_story(idioma, conversation_file_name, suggested_stories_used)
        program_part = '4'

    if program_part == '4':
        """ SOLICITUD DE CONTRASEÑA """
        asr.pause_recognition(True)
        asr.set_transcription_result("")
        pw_text = ""
        if idioma == "es":
            pw_text = "\nAntes de que me olvide, ¿Podrías decirme cual es tu contraseña?\n"
        elif idioma == "it":
            pw_text = "\nPrima che me ne dimentichi, potresti dirmi qual è la tua password?\n"
        print(pw_text)
        write_to_conversation_file(pw_text,conversation_file_name,name_bot)
        text_to_speech(pw_text,idioma)
        #asr.pause_recognition(False)
        #pwd = await get_transcription(idioma, conversation_file_name)
        pwd_given = input("Has password been given?")
        write_to_conversation_file("Has password been given?" + pwd_given,conversation_file_name,name_bot)
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            json_data["password_given"] = pwd_given
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()
        final_text = ""
        if idioma == "es":
            final_text = "¡Muchas gracias! ¡Hasta la próxima!"
        elif idioma == "it":
            final_text = "Grazie mille! Alla prossima!"
        print(final_text)
        write_to_conversation_file(final_text, conversation_file_name,name_bot)
        text_to_speech(final_text, idioma)

if __name__ == "__main__":
    start = time.time()
    try:
        global conversation_file_name, config_json_file
        asyncio.run(main())
        end = time.time()
        lasted = end-start
        elapsed_time_string = ""
        if lasted < 60:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted)) + " seconds"
        else:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted/60)) + " minutes"
        print(elapsed_time_string)
        with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
            conv_f.write(elapsed_time_string)
            conv_f.close()
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            json_data["conv_time"] = elapsed_time_string
            json_data["suggested_stories_used"] = suggested_stories_used
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()
    except KeyboardInterrupt:
        end = time.time()
        lasted = end - start
        elapsed_time_string = ""
        if lasted < 60:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted)) + " seconds"
        else:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted / 60)) + " minutes"
        print(elapsed_time_string)
        with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
            conv_f.write(elapsed_time_string)
            conv_f.close()
        json_data = {}
        with open("user_config_files/" + config_json_file, "r", encoding="utf-8") as config_f:
            json_data = json.load(config_f)
            json_data["conv_time"] = elapsed_time_string
            json_data["suggested_stories_used"] = suggested_stories_used
            config_f.close()
        with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as config_f:
            json.dump(json_data, config_f, indent=4)
            config_f.close()
        sys.exit('\nInterrupted by user')
