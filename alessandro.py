import os
import azure.cognitiveservices.speech as speechsdk
import time
import json
import requests
import pandas as pd
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractiveSummaryAction
)
from dotenv import load_dotenv

load_dotenv("env.txt")


def ask_google(text_to_ask):
    api_key = os.environ.get('API_GOOGLE_KEY')
    query = text_to_ask

    url = "https://kgsearch.googleapis.com/v1/entities:search"

    # Parámetros de la consulta
    params = {
        "query": query,
        "key": api_key,
        "limit": 1,  # Puedes ajustar el límite según tus necesidades
        "languages": "es"
    }

    # Realizar la solicitud a la API
    response = requests.get(url, params=params)
    data = response.json()

    # Procesar la respuesta
    if "itemListElement" in data and len(data["itemListElement"]) > 0:
        result = data["itemListElement"][0]["result"]
        description = result["detailedDescription"]["articleBody"]
        if description:
            return description
    else:
    print("Lo siento, no puedo ayudarte porque no tengo información sobre:" {query})


def ask_alessandro(ask_input):
    if "Alessandro" in ask_input:
            #analyze the content
               
            
        else None


def from_mic(speech_config):
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="es-BO")
    print("Ask Alessandro.")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        assistent_result = ask_alessandro(result.reason)
        return assistent_result
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")


speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
text_speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('TEXT_SPEECH_KEY'), region=os.environ.get('TEXT_SPEECH_REGION'))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

from_mic(speech_config)