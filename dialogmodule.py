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
import asyncio

import remove_personal_data_test
from IA.writesonic_test import request_chatsonic as chat
import ASR_module as asr
#import chatgpt_bridge as gpt
from remove_personal_data_test import eliminar_info_personal as filter
from playsound import playsound
import pygame
from pygame import mixer
from datetime import datetime
import keyboard
import textwrap

# Include DialogFlow module configuration file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "modulodialogo-configure.json"

mixer.init()

global conversation_file_name, num_times_supervision_activated

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

def text_to_speech(response):
    # Crear un objeto de voz
    tts = gTTS(text=response, lang='es-es')
    # Guardar el audio como un archivo MP3
    tts.save("hello.mp3")
    # Reproducir el audio
    # playsound("hello.mp3")
    tts_audio = mixer.Sound("hello.mp3")
    tts_audio_task = tts_audio.play()
    while tts_audio_task.get_busy():
        pygame.time.wait(100)


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


async def get_transcription(idioma):
    if idioma.lower() == "es":
        print("Habla tú: ", end="")
    elif idioma.lower() == "it":
        print("Parla tu: ", end="")
    await asyncio.sleep(5)
    trans_res = ""
    while trans_res == "":
        # trans_res = input()
        trans_res = asr.transcription_result
        if trans_res != "":
            print(trans_res + "\n")
        await asyncio.sleep(3)
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
    await asyncio.sleep(3)
    return response


def confirm_delivery(idioma):
    if idioma.lower() == "es":
        respuesta = input("Confirmar envio (Si o No): ")
        if respuesta.lower() == "si":
            return True
        elif respuesta.lower() == "no":
            return False
    elif idioma.lower() == "it":
        respuesta = input("Conferma spedizione (Sì o No): ")
        if respuesta.lower() == "sì":
            return True
        elif respuesta.lower() == "no":
            return False
    else:
        print("Respuesta no válida. Intente de nuevo.")
        return confirm_delivery()


def finish_first_part(idioma):
    primera_parte = ""
    if idioma.lower() == "es":
        primera_parte = [
            "¡Grande! ¡Vamos a divertirnos! A ver cómo me preparo... Vale, ya estoy listo, empieza cuando quieras.",
            "¡Estupendo! ¡Vamos a divertirnos! A ver que me prepare… Vale, yo ya estoy listo, cuando quieras empieza."]
    elif idioma == "it" or idioma == "ito":
        primera_parte = ["Fantastico! Divertiamoci! Vediamo cosa prepararmi... Ok, sono pronto, quando vuoi iniziamo",
                         "Grande! Ci divertiremo! Vediamo come mi preparo... Ok, sono pronto, inizia quando vuoi"]
    return primera_parte


# Checks if a phrase contains keywords related to endings or stories. It searches for words in a vector of vectors, and returns True if all the words are found.
def find_final(frase, idioma):
    vector_de_vectores = [["final", "fin"], ["historia", "cuento"]]
    if idioma.lower() == "es":
        vector_de_vectores = [["final", "fin", "acabo", "acabar", "terminar"], ["historia", "cuento"]]
    elif idioma.lower() == "it":
        vector_de_vectores = [["finale", "fine"], ["storia", "racconto"]]

    for vector in vector_de_vectores:
        vector_encontrado = False
        for palabra in vector:
            if palabra in frase.lower():
                vector_encontrado = True
                break
        if not vector_encontrado:
            return False
    return True


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

async def chat_with(idioma, conversation_file):
    global num_times_supervision_activated
    trans_res = ""
    response = ""
    envio = ""
    num_times_supervision_activated = 0
    i = 0
    supervision_counter = 0
    while not find_final(trans_res, idioma):
        while not contains_majority_words(remove_accents(trans_res)):
            trans_res += await get_transcription(idioma)
        if find_final(trans_res,idioma):
            envio = envio + ". " + response + ". " + trans_res
            user_res = "\nUser [" + str(datetime.now().time()) + "]: " + trans_res
            with open("conversation_files/" + conversation_file, "a", encoding="utf-8") as conv_f:
                conv_f.write("\n".join(textwrap.wrap(user_res, 150)) + "\n\n")
                conv_f.close()
            break
        # trans_res = filter(trans_res, idioma)
        print("Press [s] to Send or [w] to let Whisper keep listening")
        while True:
            if keyboard.is_pressed("s"):
                supervision_counter = 0
                envio = envio + ". " + response + ". " + trans_res
                envio = remove_repeated_dots(envio)
                response = chat(envio, conversation_file, trans_res)
                #response = gpt.process_request(envio,conversation_file, trans_res)
                asr.set_transcription_result("")
                random.seed(time.process_time())
                if not finish_first_part(idioma):
                    print("Flora: ", random_strings(idioma)[random.randint(0, 3)])
                    print(re.sub("(.{64})", "\\1\n", response, 0, re.DOTALL))
                    i += 1
                    if i == 4:
                        i = 0
                    break
                else:
                    splitted_resp = "\n".join(textwrap.wrap(response, 150))
                    print("Flora: ", splitted_resp)
                    break
            elif keyboard.is_pressed("w"):
                supervision_counter += 1
                num_times_supervision_activated += 1
                asr.set_transcription_result("")
                if supervision_counter < 2: #There has only been one supervision, ask user to retry
                    print("Flora: ", supervision_strings(idioma, 1))
                else: # Second supervision, CA adds a new input
                    envio = envio + ". " + response
                    envio = remove_repeated_dots(envio)
                    response = chat(envio, conversation_file, trans_res, supervision_activated=True)
                    asr.set_transcription_result("")
                    supervision_counter = 0
                    if not finish_first_part(idioma):
                        print("Flora: ", random_strings(idioma)[random.randint(0, 3)])
                        print(re.sub("(.{64})", "\\1\n", response, 0, re.DOTALL))
                        # print(response)
                        i += 1
                        if i == 4:
                            i = 0
                        break
                    else:
                        splitted_resp = "\n".join(textwrap.wrap(response, 150))
                        print("Flora: ", splitted_resp)
                        break
                break

    with open("story_files/" + conversation_file, "a", encoding="utf-8") as story_f:
        story_f.write("\n".join(textwrap.wrap(envio, 150)))
        story_f.close()


def ask_repeat(idioma):
    contestacion = ""
    if idioma.lower() == "es":
        contestacion = "¡Estoy muy contento! Nos ha quedado una historia muy buena.\n¿Te gustaría repetir? (si/no)"
    elif idioma.lower() == "it":
        contestacion = "Sono molto contento! Abbiamo creato una storia molto buona.\nTi piacerebbe ripetere?"

    return contestacion


async def main():
    global conversation_file_name
    # Eliminar warning en terminal
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    id = input("Enter user id: ")
    age = input("Enter user age: ")
    age_range = remove_personal_data_test.detectar_rango(str(age))
    print("Creating user files...")
    date_now = datetime.now()

    timestamp_id = date_now.strftime("%d") + "-" + date_now.strftime("%m") + "-" + \
                   date_now.strftime("%H") + "-" + date_now.strftime("%M") + "-" + id
    conversation_file_name = timestamp_id + ".txt"

    # Creating conversation_file
    with open("conversation_files/" + conversation_file_name, "w", encoding="utf-8") as conv_f:
        pass

    # Creating story_file
    with open("story_files/" + conversation_file_name, "w", encoding="utf-8") as conv_f:
        pass

    # Creating config_file
    init_conf_json = {"id": id, "accuracy": "", "conversation_file": conversation_file_name, "age_range": age_range}
    config_json_file = timestamp_id + ".json"
    with open("user_config_files/" + config_json_file, "w", encoding="utf-8") as conf_f:
        json.dump(init_conf_json, conf_f, indent=4)
        conf_f.close()
    print('\nStarting listener\n')

    listener_task = asyncio.create_task(asr.process_input_audio(conversation_file_name, config_json_file))

    while not asr.ambience_level_checked or not asr.accuracy_checked:
        await asyncio.sleep(1)
        trans_res = asr.transcription_result
        if trans_res != "":
            asr.set_transcription_result("")

    print("Checks Done! Initiating conversation...\n\n")

    project_id = "modulodialogo-pabu"
    session_id = "modulodialogo-pabu_session_id"

    """ PRIMERA PARTE DEL DIALOGO (PREVIO A LA HISTORIA) """
    response = ""
    # print("Idioma (español/ito): ", end="")

    # Acceder al idioma configurado previamente
    CONFIG_PATH = "config.json"
    with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
        configs = json.load(config)
    idioma = configs['LANGUAGE']

    asr.pause_recognition(True)
    presentacion, idioma = generate_greeting(idioma)
    print("Flora: ", presentacion)
    #text_to_speech(presentacion)
    primera_parte = finish_first_part(idioma)

    while not search_vector(response, primera_parte):
        asr.pause_recognition(False)
        trans_res = await get_transcription(idioma)
        # if confirm_delivery(idioma) == False:
        #    trans_res = ""
        if trans_res != "":
            if not search_vector(response, primera_parte):
                # Dialog
                response = await dialog_flow(project_id, session_id, trans_res, idioma)
                asr.pause_recognition(True)
                print("Flora: ", response)
                #text_to_speech(response)
                asr.pause_recognition(False)
                # await asyncio.sleep(3)

            # gpt.process_request(trans_res)
            asr.set_transcription_result("")

    """ SEGUNDA PARTE DEL DIALOGO (HISTORIA) """
    await chat_with(idioma, conversation_file_name)
    repetir = False
    respuesta = ""
    contestacion = ask_repeat(idioma)
    # print(contestacion)
    while repetir == False:
        print(contestacion)
        print("Responde: ", end="")
        respuesta = input()
        if respuesta == "si":
            await chat_with(idioma, conversation_file_name)
        elif respuesta == "no":
            repetir = True

    """ TERCERA PARTE DEL DIALOGO (FINAL) """
    if trans_res != "":
        if not search_vector(response, primera_parte):
            response = await dialog_flow(project_id, session_id, trans_res, idioma)
            asr.pause_recognition(True)
            print("Flora: ", response)
            #text_to_speech(response)
            asr.pause_recognition(False)

        asr.set_transcription_result("")

    """
    listener_task.cancel()

    try:
        await listener_task
    except asyncio.CancelledError:
        print('\nWhisper not listening anymore')
    """


if __name__ == "__main__":
    start = time.time()
    try:
        global conversation_file_name, num_times_supervision_activated
        asyncio.run(main())
        end = time.time()
        lasted = end-start
        elapsed_time_string = ""
        supervision_activated_times_string = "Supervision was activated " + str(num_times_supervision_activated) + " times"
        if lasted < 60:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted)) + " seconds"
        else:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted/60)) + " minutes"
        print(elapsed_time_string)
        with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
            conv_f.write(supervision_activated_times_string)
            conv_f.write(elapsed_time_string)
            conv_f.close()
    except KeyboardInterrupt:
        end = time.time()
        lasted = end - start
        elapsed_time_string = ""
        supervision_activated_times_string = "Supervision was activated " + str(num_times_supervision_activated) + " times"
        if lasted < 60:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted)) + " seconds"
        else:
            elapsed_time_string = "\nConversation lasted " + str(round(lasted / 60)) + " minutes"
        print(elapsed_time_string)
        with open("conversation_files/" + conversation_file_name, "a", encoding="utf-8") as conv_f:
            conv_f.write(supervision_activated_times_string)
            conv_f.write(elapsed_time_string)
            conv_f.close()
        sys.exit('\nInterrupted by user')
