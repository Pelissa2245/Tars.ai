import os
import sys
import cv2
import base64
import random
import pygame
from gtts import gTTS
import speech_recognition as sr
import google.generativeai as genai

# ====== CONFIGURAÇÃO DA API DO GEMINI ======
# API Key visível no código
API_KEY = "AIzaSyDSautrrY8zzFqO3vQWdyXRXUUU0454iz4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Ignorar mensagens de erro do ALSA
os.environ["PYTHONWARNINGS"] = "ignore"

# Redirecionar stdout e stderr para /dev/null temporariamente para esconder mensagens de C libs (como ALSA)
devnull = os.open(os.devnull, os.O_WRONLY)
sys.stdout.flush()
sys.stderr.flush()
old_stdout = os.dup(1)
old_stderr = os.dup(2)
os.dup2(devnull, 1)
os.dup2(devnull, 2)

# Importações que fazem barulho
try:
    pygame.mixer.init()
finally:
    # Restaurar stdout e stderr
    os.dup2(old_stdout, 1)
    os.dup2(old_stderr, 2)
    os.close(devnull)

# ====== FUNÇÃO PARA FALAR USANDO GTTs + PYGAME ======
def speak(text):
    print(f"TARS: {text}")
    tts = gTTS(text, lang="en", slow=False)
    filename = "response.mp3"
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    if os.path.exists(filename):
        os.remove(filename)

# ====== FUNÇÃO PARA ESCUTAR COMANDO POR VOZ ======
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=10)
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"You: {text}")
            return text.lower()
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None

# ====== FUNÇÃO PARA ENVIAR IMAGEM E TEXTO PARA O GEMINI ======
def take_photo_and_send_to_gemini(user_prompt):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("⚠ Error accessing camera.")
        speak("Camera not found.")
        return

    ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()

    if not ret:
        print("⚠ Failed to capture photo.")
        speak("Failed to capture photo.")
        return

    try:
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        response = model.generate_content([
            {"text": user_prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
        ])

        print(f"TARS: {response.text}")
        speak(response.text)
    except Exception as e:
        print(f"⚠ Error analyzing photo: {e}")
        speak("There was an error analyzing the photo.")

# ====== FUNÇÃO PARA ENVIAR TEXTO AO GEMINI ======
def send_to_gemini(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"Error accessing Gemini API: {e}"

# ====== FUNÇÃO PARA FILTRAR RESPOSTAS ======
def filter_response(response):
    return response.replace("*", "")

# ====== FUNÇÃO PARA TOCAR MÚSICA ======
def play_youtube_music(music_name):
    try:
        if os.path.exists("Interstellar.mp3"):
            speak("Playing music from my repository.")
            pygame.mixer.music.load("Interstellar.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            speak("Interstellar.mp3 not found.")
    except Exception as e:
        speak(f"Error playing music: {e}")

# ====== LOOP PRINCIPAL DO ASSISTENTE ======
if __name__ == "__main__":
    speak("AI Service Online")

    while True:
        command = listen()

        if command and "hello ai" in command:
            speak(random.choice(["You called?", "Huh?!", "Yes?", "Talk"]))

            while True:
                command = listen()
                if command:
                    if "exit" in command or "turn off" in command:
                        speak("Goodbye!")
                        break

                    elif "photo" in command or "analyze my camera" in command:
                        speak("What do you want to know about the photo?")
                        photo_prompt = listen()
                        if photo_prompt:
                            take_photo_and_send_to_gemini(photo_prompt)
                        else:
                            speak("I did not understand the question.")

                    elif "play" in command and "music" in command:
                        play_youtube_music(command)

                    else:
                        short_question = f"Answer in a few words: {command}"
                        ai_response = send_to_gemini(short_question)
                        ai_response_filtered = filter_response(ai_response)
                        print(f"TARS: {ai_response_filtered}")
                        speak(ai_response_filtered)

                    break
                else:
                    speak("I did not hear anything. Please repeat.")

        if command and ("exit" in command or "turn off" in command):
            break