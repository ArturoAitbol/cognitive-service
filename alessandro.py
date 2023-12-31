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
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from dotenv import load_dotenv

load_dotenv("env.txt")

def analyze_text(text_input: str):
    # analyze text
    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create a Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    # Contruct request
    request = AnalyzeTextOptions(text=text_input)

    # Analyze text
    try:
        response = client.analyze_text(request)
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
            raise
        print(e)
        raise

    if response.hate_result:
        print(f"Hate severity: {response.hate_result.severity}")
        hate_severity = response.hate_result.severity
    if response.self_harm_result:
        print(f"SelfHarm severity: {response.self_harm_result.severity}")
        selfharm_severity = response.self_harm_result.severity
    if response.sexual_result:
        print(f"Sexual severity: {response.sexual_result.severity}")
        sexual_severity = response.sexual_result.severity
    if response.violence_result:
        print(f"Violence severity: {response.violence_result.severity}")
        violence_severity = response.violence_result.severity
    if hate_severity > 0 or selfharm_severity > 0 or sexual_severity > 0 or violence_severity > 0:
        return True
    else:
        return False

#Summary entity: 
key_sum = os.environ.get('LANGUAGE_KEY')
endpoint_sum = os.environ.get('LANGUAGE_ENDPOINT')
# Autenticarse
def authenticate_client():
    ta_credential = AzureKeyCredential(key_sum)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint_sum, 
            credential=ta_credential)
    return text_analytics_client

client = authenticate_client()

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
    try:
        result = data["itemListElement"][0]["result"]
        description = result["detailedDescription"]["articleBody"]
        if("Person" not in result["@type"]):
            return None
        else:
            return description
    except Exception:
        return None

# Ejemplo para resumir texto
def extractive_summarization(client, documents):
    document = [documents]
    poller = client.begin_analyze_actions(
        document,
        actions=[
            ExtractiveSummaryAction(max_sentence_count=1)
        ],
    )
    document_results = poller.result()
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        resumen = ""
        if extract_summary_result.is_error:
            print("Error: '{}' - Mensaje: '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
            return None
        else:
            resumen = resumen + "{}".format(" ".join([sentence.text for sentence in extract_summary_result.sentences]))
    # Remove first Alessandro aperance in the resumen. This works in case you asked info about Alessandro Volta or Alessandro Del Piero 
    resumen = resumen.replace("Alessandro", "", 1)
    return resumen

# Example function for recognizing entities from text
def entity_recognition(client, documents):
    try:
        documents = [documents]
        result = client.recognize_entities(documents = documents)[0]

        # print("Named Entities:\n")
        for entity in result.entities:
            if entity.category == 'Person':
                return entity
        return None
    except Exception as err:
        # print("Encountered exception. {}".format(err))
        return None
    
def text_to_speech(description):
    # Leer respuesta
    speech_config.speech_synthesis_voice_name='es-BO-MarceloNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(description).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech to text: [{}]".format(description))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


def ask_alessandro(ask_input):
    if "Alessandro" in ask_input:
        #analyze the content
        is_offensive = analyze_text(ask_input)
        if is_offensive == False :
            client = authenticate_client()
            resumen = extractive_summarization(client, ask_input)
            if (resumen is not None):
                entity = entity_recognition(client, resumen)
                # print(entity)
                if entity is not None:
                    data_list = []
                    # for entity in entities:
                    data_list.append([entity.text, entity.category, entity.confidence_score])
                    columns = ['Name','Category','Confidence Score']
                    df = pd.DataFrame(data_list, columns=columns)

                    figuras_publica = df[df['Category'] == 'Person'].iloc[0].Name
                    description = ask_google(figuras_publica)
                    if description is not None:
                        return description
                    else:
                        return 'Lo siento, la entidad no es una figura pública.'
                else:
                    return 'Lo siento, soy un asistente únicamente orientado a darte información sobre figuras públicas.'
            else:
                return 'Lo siente, no pude sintetizar la instrucción'
        else:
            return 'Lo siento, no puedo ayudarte porque he detectado contenido ofensivo en tu pregunta.'
    else: return 'Para activar el asitente, inicia tu pregunta llamando a Alessandro'


def from_mic(speech_config):
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="es-BO")
    print("Ask Alessandro.")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        assistent_result = ask_alessandro(result.text)
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

response = from_mic(speech_config)
print(response)
text_to_speech(response)