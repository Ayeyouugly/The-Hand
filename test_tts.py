import dashscope
from dashscope.audio.tts import SpeechSynthesizer
import os
from dotenv import load_dotenv

load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

ref_audio = r"c:/Users/yeabsira/Desktop/THE HAND/assets/audio/my_voice.wav"
ref_text = "**"
text = "Testing one two three."

# Let's see what happens with different kwargs
try:
    with open(ref_audio, "rb") as f:
        audio_data = f.read()

    result = SpeechSynthesizer.call(
        model='qwen3-tts-vc-2026-01-22',
        text=text,
        sample_rate=24000,
        format='wav',
        prompt_text=ref_text,
        prompt_audio=ref_audio # Can be file URL or path
    )
    print("dir:", dir(result))
    print("vars:", vars(result))
    if result.get_audio_data() is not None:
        print("Audio length:", len(result.get_audio_data()))
except Exception as e:
    print("EXCEPTION:", e)
