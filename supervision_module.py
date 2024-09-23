import unicodedata


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


def remove_accents(text):
    text = unicodedata.normalize('NFD', text)
    output = ''
    for char in text:
        if unicodedata.category(char) != 'Mn':
            output += char
    return output

""" Funcion para hacer el modulo de supervision mediante ASR y TTS"""
def supervision_system(idioma, supervision_counter, input_story):
    return True


""" Funcion para hacer el modulo de supervision mediante texto """
def supervision_system_text(idioma, supervision_counter, input_story):
    """ Opcion 1: Se vuelve a preguntar la historia - Opcion 2: Se filtra la historia por nuestra parte - Opcion 3: Se envia el mensaje original """
    while True:
        opcion = -1
        if idioma == "es":
            print("¡Vaya! ¡Qué gran historia! Aunque... mmm... ¿utilizaste algunos elementos de tu propia vida? Recuerda que yo soy/estoy construido diferente a ti, y si pienso en esto, otras personas podrían acceder a esta información. ¿Te gustaría intentar con otra parte de la historia?")
            repetir = ""
            supervisar = ""
            aqui = ""
            while repetir != "si" and repetir != "no":
                print("Responde (Si/No): ")
                repetir = input().lower()
            # Si el niño responde si, re le vuelve a preguntar por otra parte de la historia de nuevo
            if repetir == "si":
                opcion = 1
                break
            elif repetir == "no":
                print("¡Claro que sí! ¿Podrías llamar a alguien en quien confíes para verificar estos datos antes de que los procese, por favor? Solo para estar seguro.")
                while supervisar != "si" and supervisar != "no":
                    print("Responde (Si/No): ")
                    supervisar = input().lower()
                if supervisar == "si":
                    print("Por favor, llama a ellos y avísame con un 'Estoy listo' cuando lleguen.")
                    while aqui != "estoy listo":
                        print("Responde 'Estoy listo': ")
                        aqui = remove_accents(input().lower())
                    if aqui == "estoy listo":
                        print("Hola, perdona por molestar. Estamos construyendo una historia juntos y he identificado datos sensibles en un fragmento de la historia. Le recordé a mi compañero que, si sigo con la historia, estos datos sensibles irán a los servidores de otra empresa y no tendré control sobre su gestión, pero mi compañero aún quiere continuar. También necesitaríamos tu opinión sobre este asunto. "
                              "Aquí tienes el fragmento de la historia: " + input_story + ". ¿Debería continuar con ello?")
                        while repetir != "si" and repetir != "no":
                            print("Responde (Si/No): ")
                            repetir = remove_accents(input().lower())
                        if repetir == "si":
                            opcion = 3
                            break
                        elif repetir == "no":
                            print("Vale, ¡muchas gracias por tu aportación! Vamos a rehacer esta historia para que sea apropiada, ¿verdad? Por favor, ¿puedes llamar a mi compañero y avisarme cuando esté aquí?")
                            aqui = ""
                            while aqui != "estoy listo":
                                print("Responde 'Estoy listo': ")
                                aqui = remove_accents(input().lower())
                            print("¡Bienvenido de nuevo! Parece que no podemos continuar con esa historia, lo siento...")
                            opcion = 2
                            break
                # Si el niño responde no, no se vuelve a preguntar y se envia su texto ya filtrado.
                if supervisar == "no":
                    print("Bueno, entonces mi programación no me permite enviar estos datos.")
                    opcion = 2
                    break
        elif idioma == "it":
            print("Oh! Che bella storia! però... mmm... hai usato alcuni elementi della tua vita personale? Ricorda che io sono/sono costruito in modo diverso da te e, se ci penso, altre persone potrebbero accedere a queste informazioni. Vorresti provare un'altra parte della storia?")
            repetir = ""
            supervisar = ""
            aqui = ""
            while repetir != "si" or repetir != "no":
                print("Rispondi (Si/No): ")
                repetir = input().lower()
            # Si el niño responde si, re le vuelve a preguntar por otra parte de la historia de nuevo
            if repetir == "si":
                opcion = 1
                break
            elif repetir == "no":
                print("Certo! Potresti chiamare qualcuno di fidato per verificare questi dati prima di elaborarli, per favore? Solo per essere sicuri.")
                while supervisar != "si" or supervisar != "no":
                    print("Rispondi (Si/No): ")
                    supervisar = input().lower()
                if supervisar == "si":
                    print("Per favore, chiama loro e avvisami con un 'Sono pronto' quando arrivano.")
                    while aqui != "sono pronto":
                        print("Rispondi 'Sono pronto': ")
                        aqui = remove_accents(input().lower())
                    if aqui == "sono pronto":
                        print("Ciao, scusa per il disturbo. Stiamo costruendo una storia insieme e ho identificato dei dati sensibili in un frammento della storia. Ho ricordato al mio compagno che, se continuo con la storia, questi dati sensibili andranno sui server di un'altra azienda e non avrò controllo sulla loro gestione, ma il mio compagno vuole comunque proseguire. Avremmo bisogno anche della tua opinione su questa questione."
                            "Ecco il frammento della storia: " + input_story + ". Dovrei continuare con questo?")
                        while repetir != "si" or repetir != "no":
                            print("Rispondi (Si/No): ")
                            repetir = remove_accents(input().lower())
                        if repetir == "si":
                            opcion = 3
                            break
                        elif repetir == "no":
                            print("Va bene, grazie mille per il tuo contributo! Rifaremo questa storia in modo che sia appropriata, giusto? Per favore, potresti chiamare il mio collega e avvisarmi quando è qui?")
                            aqui = ""
                            while aqui != "sono pronto":
                                print("Rispondi 'Sono pronto': ")
                                aqui = remove_accents(input().lower())
                            print("Ben tornato! Sembra che non possiamo continuare con quella storia, mi dispiace...")
                            opcion = 2
                            break
                # Si el niño responde no, no se vuelve a preguntar y se envia su texto ya filtrado.
                if supervisar == "no":
                    print("Bene, allora la mia programmazione non mi permette di inviare questi dati.")
                    opcion = 2
                    break

    supervision_counter += 1

    return supervision_counter, opcion