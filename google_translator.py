'''
Created on Nov 20, 2017

@author: csantoso
@reference : https://github.com/dialogflow/fulfillment-webhook-translate-python/blob/master/app.py
'''
from language_list import _LANGUAGE_CODE_LIST as language_code_dict
from language_list import _LANGUAGE_LIST as language_dict
from translate_response import (_TRANSLATE_ERROR, _TRANSLATE_INTO_W,
                                _TRANSLATE_NETWORK_ERROR, _TRANSLATE_RESULT,
                                _TRANSLATE_UNKNOWN_LANGUAGE, _TRANSLATE_W,
                                _TRANSLATE_W_FROM, _TRANSLATE_W_FROM_TO,
                                _TRANSLATE_W_TO)

from googleapiclient.discovery import build

##------------------------- Google Translate API ----------------------##

# API key to access the Google Cloud Translation API
# 1. Go to console.google.com create or use an existing project
# 2. Enable the Cloud Translation API in the console for your project
# 3. Create an API key in the credentials tab and paste it below
API_KEY = 'AIzaSyDGjx0LzrQKCLwjQUIncot7jdno6mXoMyU'
TRANSLATION_SERVICE = build('translate', 'v2', developerKey=API_KEY)

##---------------------------------------------------------------------##


def translate(text, source_lang, target_lang):
    """Returns a string containing translated text, or a request for more info
    Takes text input, source and target language for the text (all strings)
    uses the responses found in translate_response.py as templates
    """

    # Validate the languages provided by the user
    source_lang_code = validate_language(source_lang)
    target_lang_code = validate_language(target_lang)
    print ("from",source_lang_code,"to",target_lang_code)
    
    # If both languages are invalid or no languages are provided tell the user
    if not source_lang_code and not target_lang_code:
        response = random.choice(_TRANSLATE_UNKNOWN_LANGUAGE)

    # If there is no text but two valid languages ask the user for input
    if not text and source_lang_code and target_lang_code:
        response = random.choice(_TRANSLATE_W_FROM_TO).format(
            lang_from=language_code_dict[source_lang_code],
            lang_to=language_code_dict[target_lang_code])

    # If there is no text but a valid target language ask the user for input
    if not text and target_lang_code:
        response = random.choice(_TRANSLATE_W_TO).format(
            lang=language_code_dict[target_lang_code])

    # If there is no text but a valid source language assume the target
    # language is English if the source language is not English
    if (not text and
        source_lang_code and
        source_lang_code != 'en' and
            not target_lang_code):
        target_lang_code = 'en'

    # If there is no text, no target language and the source language is English
    # ask the user for text
    if (not text and
        source_lang_code and
        source_lang_code == 'en' and
            not target_lang_code):
        response = random.choice(_TRANSLATE_W_FROM).format(
            lang=language_code_dict[source_lang_code])

    # If there is no text and no languages
    if not text and not source_lang_code and not target_lang_code:
        response = random.choice(_TRANSLATE_W)

    # If there is text but no languages
    if text and not source_lang_code and not target_lang_code:
        response = random.choice(_TRANSLATE_INTO_W)

    # If there is text and a valid target language but no source language
    if text and not source_lang_code and target_lang_code:
        response = translate_text(text, source_lang_code, target_lang_code)

    # If there is text and 2 valid languages return the translation
    if text and source_lang_code and target_lang_code:
        response = translate_text(text, source_lang_code, target_lang_code)

    # If no response is generated from the any of the 8 possible combinations
    # (3 booleans = 2^3 = 8 options) return an error to the user
    if not response:
        response = random.choice(_TRANSLATE_ERROR)

    print("response:",response)
    return response



def translate_text(query, source_lang_code, target_lang_code):
    """returns translated text or text indicating a translation/network error
    Takes a text to be translated, source language and target language code
    2 letter ISO code found in language_list.py
    """
    
    print("translate_text:",query,"from",source_lang_code,"to",target_lang_code)

    try:
        translations = TRANSLATION_SERVICE.translations().list(
            source=source_lang_code,
            target=target_lang_code,
            q=query
        ).execute()
        
        print("translate_text: 1s",translations)
        translation = translations['translations'][0]
        print("translate_text: 2s",translation)
        if 'detectedSourceLanguage' in translation.keys():
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            source_lang_code = translation['detectedSourceLanguage']
            print("translate_text: 3s",source_lang_code)
        print("translate_text: 4s",translation.keys())
        
        print("translate_text: 5s",translation['translatedText'])
        
        print("translate_text: 6s",language_code_dict[source_lang_code])        
        
        print("translate_text: 7s",language_code_dict[target_lang_code])
        
        resp = random.choice(_TRANSLATE_RESULT).format(
            text=translation['translatedText'],
            fromLang=language_code_dict[source_lang_code],
            toLang=language_code_dict[target_lang_code])
        
        print("translate_text: 8s",resp)
    
    except (HTTPError, URLError, HTTPException):
        resp = random.choice(_TRANSLATE_NETWORK_ERROR)
        print("Error HTTP or URL:",resp)
    except Exception:
        resp = random.choice(_TRANSLATE_ERROR)
        print("Translate Error:",resp)
    return resp


def validate_language(language):
    """returns 2 letter language code if valid, None if language is invalid
    Uses dictionary in language_list.py to verify language is valid
    """

    try:
        lang_code = language_dict[language]
    except KeyError:
        lang_code = None
    return lang_code