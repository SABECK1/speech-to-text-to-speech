import os
import wave
import pyaudio
SOUNDFILE_NAME = os.getenv("SOUNDFILE_NAME")
async def play_sound():
    chunk = 1024
    f = wave.open(SOUNDFILE_NAME)
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    data = f.readframes(chunk)
    while data:
        stream.write(data)
        data = f.readframes(chunk)
    stream.stop_stream()
    stream.close()