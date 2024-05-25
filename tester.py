import pathlib
import textwrap
import os

#Importing the AI package
import google.generativeai as genai
#Importing the Speech Recognition package
import speech_recognition as sr
#Importing the text to speech
from gtts import gTTS
#importing sound byte stuff
from io import BytesIO
#importing sound mixer
from pygame import mixer
#for current date stuff
from datetime import date


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('key.env')

# Access the API key
api_key = os.environ['GOOGLE_API_KEY']


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))




genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-pro')

#
chat = model.start_chat()

# Set up the Gemini Pro model
gf = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 128,
    } 

safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

#text to speech function
def speak_text(text, language):
    
    mp3audio = BytesIO() 
    
    tts = gTTS(text, lang=language, tld = 'us')     
    
    tts.write_to_fp(mp3audio)

    mp3audio.seek(0)

    mixer.music.load(mp3audio, "mp3")
    mixer.music.play()

    while mixer.music.get_busy():
        pass
    
    mp3audio.close()

# save conversation to a log file 
def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a", encoding='utf-8') as f:
        f.write(text + "\n")
        f.close 

# define default language to work with the AI model 
defaultlang = "en-EN"

# Main function  
def main():
    #Prompt for language input from User
    print("Hello, the options for languages translation are: ")
    print("'en' - English")
    print("'fr' - French")
    print("'zh-CN' - Mainland Chinese")
    print("'zh-TW' - Taiwanese")
    print("'es' - Spanish")


    language = input("Please enter the language from the choice above: ")

    global today, openaitts, model, chat, defaultlang, gf, safety_settings 
    
    rec = sr.Recognizer()
    mic = sr.Microphone()
    rec.dynamic_energy_threshold = False
    rec.energy_threshold = 400 

    request = '''You are a real-time language translator. 
        Your task is to translate the speech from whatever language spoken to English. 
        Please refrain from adding any words or sentences after you 
        finish the translation, your role is to translate only. '''
    response = chat.send_message(request)   
 
    # while loop for interaction with AI model  
 
    while True:     
        with mic as source1:            
            rec.adjust_for_ambient_noise(source1, duration= 0.5)

            print("Listening ...")
            
            audio = rec.listen(source1, timeout = 20, phrase_time_limit = 30)
            
            # Save the audio to a file on the desktop
            desktop_path = os.path.expanduser("~/Desktop")
            with open(os.path.join(desktop_path, "captured_audio.wav"), "wb") as f:
                f.write(audio.get_wav_data())
                print("Audio saved to desktop as 'captured_audio.wav'")
            

            #FIXME Might need to change the way we interpret audio or use a differnt audio api 
            print(rec.recognize_google(audio, language=language))
            try:                 
               
                request = rec.recognize_google(audio, language=language)
                #request = rec.recognize_wit(audio, key=wit_api_key )
                
                if len(request) < 2:
                    continue 
                    
                if "that's all" in request.lower():
                                               
                    append2log(f"You: {request}\n")
                        
                    speak_text("Bye now")
                        
                    append2log(f"AI: Bye now. \n")                        

                    print('Bye now')

                    continue
                                       
                # process user's request (question)
                
 
                request = f"Translate this to {defaultlang}: {request}!"  
                
                append2log(f"You: {request}\n ")

                print(f"You: {request}\n AI: ")
                response = chat.send_message(request, generation_config=gf, 
                                             safety_settings=safety_settings #, stream=True,
                )

                print(response.text)
                speak_text(response.text.replace("*", ""), language)        

                append2log(f"AI: {response.text } \n")
 
            except Exception as e:
                #print(response)
                continue 

if __name__ == "__main__":
    main()