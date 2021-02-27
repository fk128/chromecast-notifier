import socket
import hashlib
from google.cloud import texttospeech as tts


def get_ip_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_add = s.getsockname()[0]
    print(ip_add)
    s.close()
    return ip_add


def hashname(message):
    m = hashlib.md5()
    m.update(message.encode('utf-8'))
    return m.hexdigest()


def get_url(text, ip_add, port):
    return f'http://{ip_add}:{port}/wav/{hashname(text)}.wav'


def text_to_wav(voice_name, text, filename):
    language_code = '-'.join(voice_name.split('-')[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name)
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config)

    with open(filename, 'wb') as out:
        out.write(response.audio_content)
