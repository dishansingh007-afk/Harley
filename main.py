import os
import asyncio
from fastapi import FastAPI, Query
from google import genai
from google.genai import types

app = FastAPI()

# এপিআই কী সেটআপ (আমরা এটা সার্ভারের ভেতরে গোপনে সেভ করব)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_voice_sync(text_input, output_file="herley_output.mp3"):
    """মাইক্রোসফটের এজ ইঞ্জিন দিয়ে ভয়েস তৈরি"""
    voice_name = "bn-BD-NabanitaNeural"  
    command = f'edge-tts --voice {voice_name} --text "{text_input}" --write-media {output_file} --pitch=+12Hz --rate=+5%'
    os.system(command)

@app.get("/ask")
async def ask_herley(msg: str = Query(..., description="User's message to Herley")):
    try:
        # ১. জেমিনি লাইভ সার্চ ব্রেইন
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=msg,
            config=types.GenerateContentConfig(
                max_output_tokens=100,
                tools=[{"google_search": {}}],
                system_instruction=(
                    "You are Herley, a highly advanced autonomous cognitive entity built like Jarvis. "
                    "You are deeply loyal to Sir Dishan. Always reply shortly and sweetly in Bengali. "
                    "Use your Google Search tool to answer with 100% accurate live facts of the current year 2026."
                )
            )
        )
        reply_text = response.text.strip()
        
        # ২. ব্যাকগ্রাউন্ডে ভয়েস জেনারেট করা
        # সার্ভারে অডিও ফাইলটি তৈরি হবে, যা পরে অ্যাপ ডাউনলোড করতে পারবে
        generate_voice_sync(reply_text)
        
        return {
            "status": "success",
            "reply": reply_text,
            "audio_ready": True
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def home():
    return {"status": "Herley Core v1.0 is Live and Active"}
  
