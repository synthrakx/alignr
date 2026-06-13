import wave
import pyaudio
import pyttsx3
import requests
import re
from faster_whisper import WhisperModel

SYSTEM = """You are the AI receptionist for Raj's Dental Clinic.
Clinic hours: Monday-Saturday 9 AM to 7 PM.
Services: cleanings, fillings, extractions, whitening.
Keep responses under 25 words. No emojis. No special characters.
If someone wants to book: ask name, day, and phone number."""

MODEL_NAME = "qwen3-baby:latest"
MIC_INDEX = 1
RATE = 16000
CHUNK = 1024

whisper = WhisperModel("tiny", device="cpu", compute_type="int8")

history = []

def clean_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def speak(text: str):
    text = clean_text(text)
    print(f"AI: {text}\n")
    e = pyttsx3.init()
    e.setProperty("rate", 165)
    e.setProperty("volume", 0.9)
    e.say(text)
    e.runAndWait()
    e.stop()

def record_wav(filename="temp.wav", seconds=5):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=MIC_INDEX,
        frames_per_buffer=CHUNK,
    )
    print(f"Recording {seconds}s... speak now")
    frames = []
    for _ in range(int(RATE / CHUNK * seconds)):
        frames.append(stream.read(CHUNK, exception_on_overflow=False))
    stream.stop_stream()
    stream.close()
    sample_width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()
    wf = wave.open(filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

def transcribe_file(filename="temp.wav") -> str:
    segments, _ = whisper.transcribe(filename, language="en", beam_size=1)
    return " ".join(s.text for s in segments).strip()

def chat(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})
    r = requests.post("http://localhost:11434/api/chat", json={
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": SYSTEM}] + history,
        "stream": False,
    }, timeout=120)
    r.raise_for_status()
    reply = r.json()["message"]["content"].strip()
    history.append({"role": "assistant", "content": reply})
    return reply

def main():
    print("=== Raj's Dental Clinic — AI Receptionist ===")
    print("Press Enter then speak. Say 'bye' to stop.\n")

    speak("Thank you for calling Raj's Dental Clinic. How can I help you today?")

    while True:
        input("Press Enter to speak...")
        record_wav(seconds=8)
        user_text = transcribe_file()
        print(f"You: {user_text}\n")

        if not user_text:
            speak("Sorry, I didn't catch that. Could you repeat?")
            continue
        if any(x in user_text.lower() for x in ["bye", "goodbye", "end"]):
            speak("Thank you for calling. Have a wonderful day!")
            break

        reply = chat(user_text)
        speak(reply)

if __name__ == "__main__":
    main()