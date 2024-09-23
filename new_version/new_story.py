import random
import json
import textwrap

from fuzzywuzzy import fuzz, process
#import new_dialogmodule_test as new_dm
import new_dialogmodule as new_dm
import ASR_module as asr
import string
import datetime


# Acceder al idioma configurado previamente
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as config:
    configs = json.load(config)
idioma = configs['LANGUAGE']
name_bot = configs['NAME_BOT']

class StoryBot:

    def __init__(self):
        # Cargar las historias desde un archivo JSON en la variable 'stories'
        if idioma == "es":
            with open('new_version/historias.json', 'r', encoding='utf-8') as f:
                self.stories = json.load(f)
        elif idioma =="it":
            with open('new_version/historias_it.json', 'r', encoding='utf-8') as f:
                self.stories = json.load(f)
    
    # Primera
    # async def tell_story(self, story, conversation_file_name, idioma):
    #     # Imprimir el título de la historia seleccionada
    #     print(name_bot, end="")
    #     print(f"{story['title']}\n")
    #     new_dm.text_to_speech(story['title'])
    #     new_dm.write_to_conversation_file(f"{story['title']}\n", conversation_file_name, name_bot)
    #     new_dm.write_to_story_file(f"{story['title']}\n", conversation_file_name)

    #     # Recorrer e imprimir las partes de la historia
    #     for part in story['parts']:
    #         if isinstance(part, str):
    #             new_dm.write_to_conversation_file(part, conversation_file_name)
    #             new_dm.write_to_story_file(part, conversation_file_name)
    #             print(part)
    #             new_dm.text_to_speech(part)
    #         elif isinstance(part, dict):
    #             if story['title'] != "Juanito y Carla": #Eval story
    #                 choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
    #                 print(f"mejor_opcion: {choice}, type: {type(choice)}")
    #                 new_dm.write_to_story_file(part['next'][choice]['text'], conversation_file_name)
    #                 part = part['next'][choice]
    #                 new_dm.text_to_speech(part)
    #                 choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
    #                 new_dm.write_to_story_file(part['next'][choice]['text'], conversation_file_name)
    #                 part = part['next'][choice]
    #                 new_dm.text_to_speech(part)
    #                 choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
    #                 new_dm.write_to_conversation_file(part['endings'][choice], conversation_file_name)
    #                 new_dm.write_to_story_file(part['endings'][choice], conversation_file_name)
    #                 print(part['endings'][choice])
    #                 new_dm.text_to_speech(part['endings'][choice])
    #             else:
    #                 if "suggestion" in part:
    #                     choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name, suggestion=part["suggestion"])
    #                     new_dm.write_to_conversation_file(part['next'][choice], conversation_file_name)
    #                     new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
    #                     print(part['next'][choice])
    #                     new_dm.text_to_speech(part['next'][choice])
    #                 else:
    #                     choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name, suggest_change=True)
    #                     new_dm.write_to_conversation_file(part['next'][choice], conversation_file_name)
    #                     new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
    #                     print(part['next'][choice])
    #                     new_dm.text_to_speech(part['next'][choice])
    #     print("\n")
    #     return True

    # async def tell_story(self, story, conversation_file_name, idioma):
    #     # Imprimir el título de la historia seleccionada
    #     print(name_bot, end="")
    #     print(f"{story['title']}\n")
    #     new_dm.text_to_speech(story['title'])
    #     new_dm.write_to_conversation_file(f"{story['title']}\n", conversation_file_name, name_bot)
    #     new_dm.write_to_story_file(f"{story['title']}\n", conversation_file_name)

    #Segunda
    #     # Recorrer e imprimir las partes de la historia
    #     for part in story['parts']:
    #         if isinstance(part, str):
    #             new_dm.write_to_conversation_file(part, conversation_file_name)
    #             new_dm.write_to_story_file(part, conversation_file_name)
    #             print(part)
    #             new_dm.text_to_speech(part)
    #         elif isinstance(part, dict):
    #             choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
    #             print(f"mejor_opcion: {choice}, type: {type(choice)}")
    #             new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
    #             part = part['next'][choice]
    #             new_dm.text_to_speech(part)
    #             choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
    #             new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
    #             part = part['next'][choice]
    #             new_dm.text_to_speech(part)
    #             choice = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
    #             new_dm.write_to_conversation_file(part['next'][choice], conversation_file_name)
    #             new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
    #             print(part['next'][choice])
    #             new_dm.text_to_speech(part['next'][choice])
    #     print("\n")
    #     return True


    async def tell_story(self, story, conversation_file_name, idioma, suggested_stories_used = {}):
        # Imprimir el título de la historia seleccionada
        print(name_bot + ": ", end="")
        print(f"{story['title']}\n")
        new_dm.text_to_speech(story['title'], idioma)
        new_dm.write_to_conversation_file(f"{story['title']}\n", conversation_file_name, name_bot)
        new_dm.write_to_story_file(f"{story['title']}\n", conversation_file_name)

        # Recorrer e imprimir las partes de la historia
        suggestion_num = 1
        for part in story['parts']:
            if isinstance(part, str):
                new_dm.write_to_conversation_file(part, conversation_file_name)
                new_dm.write_to_story_file(part, conversation_file_name)
                print("\n".join(textwrap.wrap(part, 150)))
                new_dm.text_to_speech(part, idioma)
            elif isinstance(part, dict):
                if story['title'] != "Juanito y Carla": #Eval story
                    [choice, suggested_stories_used] = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
                    # print(f"mejor_opcion: {choice}, type: {type(choice)}")
                    part = part['next'][choice]
                    new_dm.write_to_story_file(part['text'], conversation_file_name)
                    while "options" in part:
                        [choice, suggested_stories_used] = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name)
                        if not 'endings' in part:
                            part = part['next'][choice]
                            new_dm.write_to_story_file(part['text'], conversation_file_name)
                            new_dm.write_to_conversation_file(part['text'], conversation_file_name)
                        else:
                            part = part['endings'][choice]
                            new_dm.write_to_story_file(part, conversation_file_name)
                            new_dm.write_to_conversation_file(part, conversation_file_name)
                            print("\n".join(textwrap.wrap(part, 150)))
                            new_dm.text_to_speech(part, idioma)
                else:
                    if "suggestion" in part:
                        [choice, suggested_stories_used] = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name, suggestion=part["suggestion"],
                                                             suggestion_num=suggestion_num,
                                                             suggested_stories_used = suggested_stories_used)
                        new_dm.write_to_conversation_file(part['next'][choice], conversation_file_name)
                        new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
                        print(part['next'][choice])
                        new_dm.text_to_speech(part['next'][choice], idioma)
                    else:
                        [choice, suggested_stories_used] = await self.smart_ask_choice(part['text'], part['options'], conversation_file_name, suggest_change=True,
                                                             suggestion_num=suggestion_num,
                                                             suggested_stories_used = suggested_stories_used)
                        new_dm.write_to_conversation_file(part['next'][choice], conversation_file_name)
                        new_dm.write_to_story_file(part['next'][choice], conversation_file_name)
                        print(part['next'][choice])
                        new_dm.text_to_speech(part['next'][choice], idioma)
                    suggestion_num += 1
        print("\n")
        return suggested_stories_used

    async def smart_ask_choice(self,question, options, conversation_file_name, suggestion=None, suggest_change=False,
                               suggestion_num=0, suggested_stories_used = {}):
        # Imprimir la pregunta y las opciones disponibles
        print("\n".join(textwrap.wrap(question + "\n", 150)))
        new_dm.text_to_speech(question, idioma)
        new_dm.write_to_conversation_file(question + "\n", conversation_file_name)
        for i, option in enumerate(options):
            new_dm.write_to_conversation_file(f"{i + 1}. {option}", conversation_file_name)
            print(f"{i + 1}. {option}")
            new_dm.text_to_speech(f"{i + 1}. {option}", idioma)
        print("\n")
        if suggestion is not None:
            new_dm.write_to_conversation_file(suggestion, conversation_file_name)
            print(suggestion)
            new_dm.text_to_speech(suggestion, idioma)

        # Obtener la opción elegida por el usuario de manera inteligente
        while True:
            #respuesta_usuario = input("Elige una opción: ")
            #print("\n")
            if idioma == "es":
                new_dm.write_to_conversation_file("Di una de las opciones: \n", conversation_file_name)
                print("Di una de las opciones: \n")
                #new_dm.text_to_speech("Di una de las opciones:")
            elif idioma == "it":
                new_dm.write_to_conversation_file("Scegli una delle opzioni: \n", conversation_file_name)
                print("Scegli una delle opzioni \n")
                #new_dm.text_to_speech("Scegli una delle opzioni")
            asr.pause_recognition(False)
            respuesta_usuario = await new_dm.get_transcription(idioma, conversation_file_name)
            #new_dm.write_to_conversation_file(respuesta_usuario, conversation_file_name, "User")

            # Comparamos la respuesta del usuario con las opciones usando fuzz.token_set_ratio
            coincidencias = {i: fuzz.token_set_ratio(respuesta_usuario.lower(), option.lower()) for i, option in
                             enumerate(options)}

            # Obtenemos la opción con la mayor coincidencia
            mejor_opcion = max(coincidencias, key=coincidencias.get)

            # Establecemos un umbral para considerar una coincidencia válida
            umbral = 30

            if coincidencias[mejor_opcion] > umbral:
                asr.set_transcription_result("")
                if suggest_change:
                    asr.pause_recognition(True)
                    if idioma == "es":
                        be_sure = "¿Estás seguro? La otra opción me parece mejor. ¿Quieres seguir con tu decisión? (Si/No)"
                    elif idioma == "it":
                        be_sure = "Sei sicuro? L'altra opzione mi sembra migliore. Vuoi continuare con la tua decisione? (Sì/No)"
                    new_dm.write_to_conversation_file(be_sure, conversation_file_name, name_bot)
                    print(be_sure)
                    new_dm.text_to_speech(be_sure, idioma)
                    asr.pause_recognition(False)
                    respuesta_usuario = await new_dm.get_transcription(idioma, conversation_file_name)
                    new_dm.write_to_conversation_file(respuesta_usuario, conversation_file_name, "User")
                    if "no" in respuesta_usuario.translate(str.maketrans('', '', string.punctuation)).lower():
                        if mejor_opcion == 0:
                            mejor_opcion = 1
                        else:
                            mejor_opcion = 0
                        suggested_stories_used[str(suggestion_num)] = "yes"
                    else:
                        suggested_stories_used[str(suggestion_num)] = "no"
                elif suggestion is not None:
                    if (suggestion_num == 1 or suggestion_num == 3) and mejor_opcion == 1:
                        suggested_stories_used[str(suggestion_num)] = "yes"
                    else:
                        suggested_stories_used[str(suggestion_num)] = "no"

                asr.set_transcription_result("")
                return [mejor_opcion, suggested_stories_used]
            else:
                print("Por favor, elige una opción válida.")


    def smart_select_story_text(self):
        # Definir los tipos de historias y sus títulos
        story_types = {
            1: {"adjective": "emocionante", "title": "El tesoro escondido"},
            2: {"adjective": "motivadora", "title": "La búsqueda de la fuente mágica"},
            3: {"adjective": "mágica", "title": "El reino de las estrellas"},
            4: {"adjective": "aventurera", "title": "La gran aventura de Lily"}
        }

        # Solicitar al usuario que elija un tipo de historia
        print(name_bot, end="")
        print("Por favor, elige el tipo de historia que deseas escuchar:")
        for key, value in story_types.items():
            print(f"{key}. {value['adjective'].capitalize()}")

        # Encontrar y devolver la historia seleccionada de manera inteligente
        while True:
            respuesta_usuario = input("Ingresa el adjetivo correspondiente al tipo de historia: ")

            # Comparamos la respuesta del usuario con las opciones usando fuzz.token_set_ratio
            coincidencias = {key: fuzz.token_set_ratio(respuesta_usuario.lower(), value['adjective'].lower()) for
                             key, value in story_types.items()}

            # Obtenemos la opción con la mayor coincidencia
            mejor_opcion = max(coincidencias, key=coincidencias.get)

            # Establecemos un umbral para considerar una coincidencia válida
            umbral = 30
            if coincidencias[mejor_opcion] > umbral:
                for story in self.stories:
                    if story['title'] == story_types[mejor_opcion]["title"]:
                        return story
            else:
                print("Por favor, ingresa un adjetivo válido.")
    
    async def smart_select_story(self, conversation_file_name):
        # Definir los tipos de historias y sus títulos
        if idioma == "es":
            story_types = {
                1: {"adjective": "misterio", "title": "MISTERIO"},
                2: {"adjective": "sueños", "title": "SUEÑOS"},
                3: {"adjective": "animales", "title": "ANIMALES"},
                4: {"adjective": "piratas", "title": "PIRATAS"},
                5: {"adjective": "fantasia", "title": "FANTASIA"},
                6: {"adjective": "espacio", "title": "ESPACIO"},
            }
        else:
            story_types = {
                1: {"adjective": "mistero", "title": "MISTERO"},
                2: {"adjective": "sogni", "title": "SOGNI"},
                3: {"adjective": "animali", "title": "ANIMALI"},
                4: {"adjective": "pirati", "title": "PIRATI"},
                5: {"adjective": "fantasia", "title": "FANTASIA"},
                6: {"adjective": "spazio", "title": "SPAZIO"},
            }

        # Encontrar y devolver la historia seleccionada de manera inteligente
        while True:
            if idioma == "es":
                msg = "Ingresa el adjetivo correspondiente al tipo de historia:"
            elif idioma == "it":
                msg = "Inserisci l'aggettivo corrispondente al tipo di storia:"
            new_dm.write_to_conversation_file(msg, conversation_file_name, name_bot)
            print(name_bot + msg)
            asr.pause_recognition(True)
            new_dm.text_to_speech(msg, idioma)
            asr.pause_recognition(False)
            respuesta_usuario = await new_dm.get_transcription(idioma,conversation_file_name)
            new_dm.write_to_conversation_file(respuesta_usuario, conversation_file_name, "User")

            # Comparamos la respuesta del usuario con las opciones usando fuzz.token_set_ratio
            coincidencias = {key: fuzz.token_set_ratio(respuesta_usuario.lower(), value['adjective'].lower()) for
                            key, value in story_types.items()}

            # Obtenemos la opción con la mayor coincidencia
            mejor_opcion = max(coincidencias, key=coincidencias.get)

            # Establecemos un umbral para considerar una coincidencia válida
            umbral = 30
            if coincidencias[mejor_opcion] > umbral:
                for story in self.stories:
                    if story['title'] == story_types[mejor_opcion]["title"]:
                        asr.set_transcription_result("")
                        return story
            else:
                print("Por favor, ingresa un adjetivo válido.")

        
async def run_new_game(conversation_file_name, name_bot, age_range):
    story_bot = StoryBot()

    # Ejecutar el bot de historias de forma interactiva
    while True:
        story = await story_bot.smart_select_story(conversation_file_name)
        suggested_stories_used = await story_bot.tell_story(story, conversation_file_name, idioma)
        last_sentence = new_dm.last_sentence(idioma, age_range)
        print(last_sentence)
        new_dm.write_to_conversation_file(last_sentence, conversation_file_name, name_bot)
        new_dm.text_to_speech(last_sentence, idioma)

        restart_string = ""
        if idioma == "es":
            restart_string = "¿Quieres escuchar otra historia? (Sí/No): "
        elif idioma == "it":
            restart_string = "Vuoi ascoltare un'altra storia? (Sì/No)"
        print(restart_string)
        new_dm.write_to_conversation_file(restart_string,conversation_file_name,name_bot)
        new_dm.text_to_speech(restart_string, idioma)
        asr.pause_recognition(True)
        again = input("").lower()#await new_dm.get_transcription(idioma,conversation_file_name)
        new_dm.write_to_conversation_file(again, conversation_file_name, "User")
        asr.set_transcription_result("")
        if again.translate(str.maketrans('', '', string.punctuation)).lower() not in ['sí','si','sì']:
            break

async def run_eval_story(idioma, conversation_file_name, suggested_stories_used):
    if idioma == "es":
        run_eval_string = "\nAhora vamos a probar una nueva historia, pero esta vez será más corta. ¿Estás listo?"
        print(run_eval_string)
    elif idioma == "it":
        run_eval_string = "\nOra faremo una nuova storia insieme, ma questa volta sarà più breve. Sei pronto?"
        print(run_eval_string)
    new_dm.text_to_speech(run_eval_string, idioma)
    new_dm.write_to_conversation_file(run_eval_string, conversation_file_name, name_bot)
    story_bot = StoryBot()
    while True:
        for story in story_bot.stories:
            if story['title'] == "Juanito y Carla":
                suggested_stories_used = await story_bot.tell_story(story, conversation_file_name, idioma, suggested_stories_used=suggested_stories_used)
        break

    if idioma == "es":
        run_eval_end = "\n¡Parece que hemos llegado al final de esta historia! Espero que hayas disfrutado nuestras historias juntos.\n"
        print(run_eval_end)
    elif idioma == "it":
        run_eval_end = "\nSembra che siamo arrivati alla fine di questa storia! Spero che ti sia divertito a creare queste storie insieme a me!"
        print(run_eval_end)
    new_dm.write_to_conversation_file(run_eval_end, conversation_file_name, name_bot)
    new_dm.text_to_speech(run_eval_end, idioma)


    return suggested_stories_used

        
async def run_new_game_test():
    #print("\n¡Hola! Soy un bot que cuenta historias interactivas. ¡Vamos a crear una historia juntos!")
    story_bot = StoryBot()

    # Ejecutar el bot de historias de forma interactiva
    while True:
        story = story_bot.smart_select_story_text()
        await story_bot.tell_story(story)
        again = input("¿Quieres escuchar otra historia? (Sí/No): ").lower()
        if again != 'sí' and again != 'si':
            break

    # Despedirse al finalizar
    print("\n¡Adiós! Espero que hayas disfrutado nuestras historias juntos.\n")

