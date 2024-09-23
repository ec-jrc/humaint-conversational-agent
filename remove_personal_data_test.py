import re
import spacy

def eliminar_info_personal(text, language, palabras_prohibidas=None):
    # Patterns for sensitive information
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    password_pattern = r'(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!$%@#£€*?&]{8,}'
    date_pattern = r'\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b'
    dni_pattern = {  # Add or modify patterns for different languages
        'es': r'\b\d{8}[ -]?[A-Z]\b',
        'en': r'\b[A-Z]{2}\d{6}[A-Z]?\b',
        'it': r'\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b'
    }
    address_pattern = {  # Add or modify patterns for different languages
        'es': r'(?:(?:Calle|Avenida|Paseo|Plaza|Carrer)[\w\s.]+(?:[,])?\s*\d{1,5})',
        'en': r'(?:(?:\d{1,5}\s*(?:[A-Za-z]+|[A-Za-z]+\.)\s*)+(?:Avenue|Lane|Road|Street|St|Ct|Drive|Dr|Rd|Ln|Ave))',
        'it': r'(?:(?:Via|Viale|Piazza|Piazzale|Corso)[\w\s.]+(?:[,])?\s*\d{1,5})',
    }
    name_pattern = {  # Add or modify patterns for different languages
        'es': r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
        'en': r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
        'it': r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
    }
    # Check if the language is supported
    if language not in dni_pattern or language not in address_pattern or language not in name_pattern:
        raise ValueError("Language not supported. Please use 'en' (English), 'es' (Spanish) or 'it' (Italian).")
    # Replace sensitive information
    text = re.sub(email_pattern, '', text)
    text = re.sub(password_pattern, '****', text)
    text = re.sub(date_pattern, '****', text)
    text = re.sub(dni_pattern[language], '****', text)
    text = re.sub(address_pattern[language], '****', text)
    text = re.sub(name_pattern[language], '****', text)

    return text

def detectar_rango(texto):
    numeros = re.findall(r'\d+', texto)  # Encuentra todos los números en el string
    rango = ""

    for numero in numeros:
        num = int(numero)
        if 1 <= num <= 7:
            rango = "1-7"
            break
        elif 8 <= num <= 12:
            rango = "8-12"
            break
        elif num > 12:
            rango = "adult"
            break

    return rango
