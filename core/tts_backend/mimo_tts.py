import base64
from pathlib import Path
import requests
import json
from core.utils import load_key, except_handler

# ------------
# Xiaomi MiMo v2.5 TTS (OpenAI-compatible chat/completions format)
# docs: https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5
# ------------
BASE_URL = "https://api.xiaomimimo.com/v1/chat/completions"
MODEL = "mimo-v2.5-tts"
# preset voices: zh -> 冰糖 茉莉 苏打 白桦 ; en -> Mia Chloe Milo Dean ; default -> mimo_default
VOICE_LIST = ["冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean", "mimo_default"]

@except_handler("Failed to generate audio using Xiaomi MiMo TTS", retry=3, delay=1)
def mimo_tts(text, save_path):
    API_KEY = load_key("mimo_tts.api_key")
    voice = load_key("mimo_tts.voice")
    style = load_key("mimo_tts.style")

    # assistant message carries the text to synthesize; optional user message gives a style instruction
    messages = []
    if style:
        messages.append({"role": "user", "content": style})
    messages.append({"role": "assistant", "content": text})

    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "audio": {"format": "wav", "voice": voice}
    })

    # MiMo accepts the api-key header; also send the OpenAI-style bearer for compatibility
    headers = {
        "api-key": API_KEY,
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    speech_file_path = Path(save_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.post(BASE_URL, headers=headers, data=payload)
    response.raise_for_status()
    response_data = response.json()

    audio_b64 = response_data["choices"][0]["message"]["audio"]["data"]
    with open(speech_file_path, "wb") as f:
        f.write(base64.b64decode(audio_b64))
    print(f"Audio saved to {speech_file_path}")

if __name__ == "__main__":
    mimo_tts("Hi! Welcome to VideoLingo!", "test.wav")
