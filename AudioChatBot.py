import os
import wavio
import playsound
import speech_recognition as sr
import sounddevice as sd
from pydub import AudioSegment
from scipy.io.wavfile import write
from pynput import keyboard
from hugchat import hugchat
from hugchat.login import Login
from gtts import gTTS

print("Loading...")

# Configuration
voice_filepath = 'your path to /chatbotfiles/voiceRecording.wav' # Mac Ex: /Users/user/Documents/AudioChatBot/chatbotfiles/voiceRecording.wav
bot_voice_filepath = "your path to /chatbotfiles/bot_voice.mp3" 
username = "your username for huggingchat here"
password = "your password for huggingchat here"
initial_prompt = "your prompt here"
bot_name = "AI Bot"
bot_voice_speed = 1.25 # Can sort of corrupt the audio when at certain values
recording_time = 10


# Signs into huggingchat
sign = Login(username, password) 
cookies = sign.login()

cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)

# Creates a chatbot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

# This will give the bot a starting personality
initial_message = chatbot.query(initial_prompt)
print(str(initial_message)[0])

print("Ready to Record\n")

def talk_to_bot():
    # Recording the voice
    fs = 44100 
    seconds = recording_time

    print("Recording Started...")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait() 

    print("Recording Stopped\n")
    recording = recording.flatten()  
    wavio.write(voice_filepath, recording, fs, sampwidth=2)  # Saves to the set filepath


    # Speech-to-text using the recorded file
    r = sr.Recognizer()
    with sr.AudioFile(voice_filepath) as source:
        try:
            audio_data = r.record(source)
            message = r.recognize_google(audio_data) 
            print(f'You: {message}\n')
        except: 
            print("Recording isn't readable, try again\n") # This will usually be UnknownValueError, but it doesn't accept that as an exception name

    # Sending message to the bot
    bot_message = chatbot.query(message)
    print(f'{bot_name}: {bot_message}\n')

    # Converting bot_message to text-to-speech
    language = "en"
    bot_str_message = str(bot_message)
    bot_voice = gTTS(text=bot_str_message, lang=language, slow=False)
    bot_voice.save(bot_voice_filepath)

    # Modifying audio
    audio = AudioSegment.from_file(bot_voice_filepath, format="mp3")
    final = audio.speedup(playback_speed=bot_voice_speed)
    final.export(bot_voice_filepath, format="mp3")

    # Playing the text-to-speech file
    playsound.playsound(bot_voice_filepath)
    


# Key to start
def on_release(key):
    try:
        if key.char == 'k': 
            talk_to_bot()
    except:
        pass
        
listener = keyboard.Listener(on_release=on_release)
listener.start()

