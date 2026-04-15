import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

REF_AUDIO = r"c:/Users/yeabsira/Desktop/THE HAND/assets/audio/my_voice.wav"
with open(REF_AUDIO, "rb") as f:
    audio_bytes = f.read()
data_uri = f"data:audio/wav;base64,{base64.b64encode(audio_bytes).decode('utf-8')}"

enroll_url = "https://dashscope-intl.aliyuncs.com/api/v1/services/audio/tts/customization"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload3 = {
    "model": "qwen-voice-enrollment",
    "parameters": {
        "target_model": "qwen3-tts-vc-2026-01-22"
    },
    "input": {
        "audio": {
            "data": data_uri
        }
    }
}
r3 = requests.post(enroll_url, json=payload3, headers=headers)
print("TEST 3:")
print("Status:", r3.status_code)
print("Response:", r3.text)

