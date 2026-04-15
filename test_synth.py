import os
from dotenv import load_dotenv
import dashscope

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
dashscope.api_key = api_key
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

print("Testing MultiModalConversation...")
try:
    result = dashscope.MultiModalConversation.call(
        model='qwen3-tts-vc-2026-01-22',
        messages=[{"role": "user", "content": [{"text": "Hello world"}]}],
        api_key=api_key,
        # No voice parameter, let's see if it errors
    )
    print("Result attributes:", dir(result))
    if hasattr(result.output, "audio") or hasattr(result, "get_audio_data"):
        print("Success! Got audio.")
    else:
        print("Response:", vars(result))
except Exception as e:
    print("Exception MultiModal:", e)
