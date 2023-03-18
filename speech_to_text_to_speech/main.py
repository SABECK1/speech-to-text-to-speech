import asyncio
import logging
import pynput
import httpcore
import httpx
import speech_recognition as sr
import translatepy.translators
from voicevox import Client

# Setup of the Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", 'w', 'utf-8'),
        logging.StreamHandler()
    ]
)

r = sr.Recognizer()
RECORD_KEY = '+'


def show_mic_list():
    # Shows all microphone inputs/outputs - needs to be changed to only inputs
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        print(i, microphone_name)


def get_user_input():
    # Gets the user input to choose the mic for input
    chosen_microphone = input('Choose your microphone using its Index or "Default": ')
    return chosen_microphone


def get_mic():
    # Gets executed recursively if no correct input is given
    chosen_microphone = get_user_input()
    if chosen_microphone.upper() == "DEFAULT":
        return None
    try:
        sr.Microphone.list_microphone_names()[int(chosen_microphone)]
    except ValueError:
        print("Not a valid choice!")
        chosen_microphone = get_mic()
    return int(chosen_microphone)


async def get_translation():
    # Gets translation to give to Voicevox
    with sr.Microphone(device_index=chosen_mic) as source:
        logging.info("Adjusting...")
        r.adjust_for_ambient_noise(source)
        logging.info("Now listening")
        audio_data = r.listen(source)
        logging.info("Recognizing...")
        try:
            text = r.recognize_google(audio_data, language="de")
            translation = gtranslate.translate(text, "Japanese", source_language='de')
            logging.info('Recognized input: {} | Translation: {}'.format(text, translation))
            return translation.result
        except:
            logging.error("Unknown Translation")
            await get_translation()


async def synthesize(speaker: int):
    # Synthesizes the final voice
    async with Client() as client:
        try:
            audio_query = await client.create_audio_query(await get_translation(), speaker=speaker)
            logging.info("Synthesizing...")
            with open("voice.wav", "wb") as f:
                f.write(await audio_query.synthesis(speaker=speaker))
        except (httpcore.ConnectError, ConnectionRefusedError, OSError, httpx.ConnectError):
            logging.error("Connection refused")
        else:
            logging.info("Finished synthesizing")


async def get_speaker(send_speaker: bool):
    async with Client() as client:
        speakers_list = await client.fetch_speakers()
    if send_speaker:
        for i, speaker in enumerate(speakers_list):
            print(i, speaker.name)

    speaker = input("Please specify which speaker you want to use: ")
    try:
        speakers_list[int(speaker)]
    except ValueError:
        print("Not a valid speaker!")
        await get_speaker(send_speaker=False)
    return int(speaker)





def keyboard_input():
    # Starts a keyboard listener - may cause inputlag
    def on_press(key):
        global running
        try:
            if key.char == RECORD_KEY:
                running = not running
                logging.info(f"Set running to {running}")
        except AttributeError:
            pass

    listener = pynput.keyboard.Listener(
        on_press=on_press
    )
    listener.start()


show_mic_list()
chosen_mic = get_mic()
gtranslate = translatepy.translators.GoogleTranslate()
keyboard_input()
speaker = asyncio.run(get_speaker(True))
running = False
while True:
    if running:
        asyncio.run(synthesize(speaker))
