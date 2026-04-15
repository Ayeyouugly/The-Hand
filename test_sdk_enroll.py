import os
import asyncio
import logging
from dotenv import load_dotenv
import dashscope
from dashscope.audio.tts_v2 import VoiceEnrollmentService

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
dashscope.api_key = api_key
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

import httpx
import logging
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

REF_AUDIO = r"c:/Users/yeabsira/Desktop/THE HAND/assets/audio/my_voice.wav"
svc = VoiceEnrollmentService(api_key=api_key)

print("Trying SDK enrollment...")
try:
    voice_id = svc.create_voice(
        target_model="qwen3-tts-vc-2026-01-22",
        prefix="testvc",
        url=f"file://{REF_AUDIO}"
    )
    print("SUCCESS Voice ID:", voice_id)
except Exception as e:
    print("EXCEPTION:", e)
