# Humaint Conversational Agent
## Este repositorio contiene el código fuente para el proyecto "Humaint Conversational Agent", que tiene como objetivo proporcionar un agente conversacional para temer interacciones éticas con usuarios (principalmente niños) a través de dos métodos principales: mediante el modelo de lenguaje GPT de OpenAI y mediante historias predefinidas.

## Contenidos
1. [Instalación](#instalacion)
2. [Archivos principales](#archivos-principales)
3. [Uso](#uso)
4. [Contribuir](#contribuir)

## Instalación <a name="instalacion"></a>
Para instalar las dependencias necesarias para este proyecto, primero asegúrese de tener instalado Python 3.8 o posterior. Luego, puede instalar las dependencias con:

`pip install -r requirements.txt`

Por otro lado, para el soporte GPU de fast-whisper, se requiere la instalación de CUDA v11.x con CUBLAS v11.x, CUDNN 8.x y ZLIB_DLL
ver guías de instalación [aquí](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)

## Archivos Principales <a name="archivos-principales"></a>
El repositorio contiene los siguientes archivos principales:

- dialogmodule.py: Es el programa principal para la interacción basada en ChatGPT.
- new_dialogmodule.py: Es el programa principal para la interacción basada en historias predefinidas.
- ASR_module.py: Módulo responsable de la integración de Whisper (reconocimiento de voz).
- new_story.py: Proporciona funcionalidades específicas para la creación de historias predefinidas.
- historias.json: Archivo que contiene las historias predefinidas utilizadas en el programa del punto 2.
- requirements.txt: Requisitos para el proyecto.

## Uso <a name="uso"></a>
Antes de ejecutar los programas, asegúrate de tener configuradas todas las credenciales y permisos necesarios para utilizar los servicios de OpenAI, Google Cloud Dialogflow y Google Text to Speech.

Para iniciar la interacción basada en ChatGPT, ejecuta:

`python dialogmodule.py`

Para iniciar la interacción basada en historias predefinidas, ejecuta:

`python new_dialogmodule.py`


## Contribuir <a name="contribuir"></a>
Las contribuciones son siempre bienvenidas. Antes de hacer cualquier contribución, por favor, asegúrese de leer las directrices y el código de conducta.

## Licencia


## Contacto
Si tiene alguna pregunta o problema, no dude en abrir un issue en este repositorio.


