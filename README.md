# Humaint Conversational Agent
## This repository contains the code for the project Cas4Kids, which objective is to build a conversational agent for ethic interactions with users (mainly children) by using two methods: 
- Using OpenAi's GPT language model
- Using predefined stories.

## Contents
1. [Instalation](#instalation)
2. [Main files](#main-files)
3. [Use](#use)
4. [Contribute](#contribute)

## Instalation <a name="instalation"></a>
To install the necessary dependencies for this project, ensure first that you have installed Python 3.8 or later versions. Then, you can install all the dependencies by running:

`pip install -r requirements.txt`

Apart from that, for the GPU support of Faster Whisper, the installation of CUDA v11.x with CUBLAS v11.x, CUDNN 8.x and ZLIB_DLL is required. See installation guides [here](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)

## Main Files <a name="main-files"></a>
The repository contains the following files:

- dialogmodule.py: Main program for the interaction based on ChatGPT.
- new_dialogmodule.py: Main program for the interaction based on predefined stories.
- ASR_module.py: Module responsible for the integration with Whisper (Speech recognition).
- new_story.py: Gives specific functionalities for the creation of predefined stories.
- historias.json: File containing the predefined stories.
- requirements.txt: Requirements of the project.

## Use <a name="use"></a>
Before executing the programs, ensure you have all the credentials configured and all the permissions required to use OpenAI's services, Google Cloud DialogFlow and Google TTS
We cannot share over this repository the secrets to the Dialogflow instance for this project. You can either build them yourself or write to jrc-humaint@ec.europa.eu

To start the interaction based on ChatGPT, execute:

`python dialogmodule.py`

To start the interaction based on predefined stories, execute:

`python new_dialogmodule.py`
