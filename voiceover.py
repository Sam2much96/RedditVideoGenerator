"""
Voiceover.py

Features:
(1) Records reddit posts using libespeak text to speech on linux
(2) Uses pyttsx3

Bugs:
(1) Voice over creation logic hangs on linux devices, the logic would need reworking
(2) Class Object gets converted to string object sometime during run
(3) Eleven labs api costs too much, replace voiceover api with Coqui TTS 88mb model : https://chatgpt.com/c/68bac41f-03ec-832e-b0cf-d795a39b8490
"""

# from gtts import gTTS  # type: ignore
# import pyttsx3  # for voiceovers
from TTS.api import TTS
from moviepy.editor import AudioFileClip
import os
import subprocess
import ffmpeg
import math
# from mutagen.mp3 import MP3
import time
import traceback  # for debugging function stack
import configparser
# from elevenlabs import save  # type: ignore
# from elevenlabs.client import ElevenLabs  # type: ignore

# Constants
MAX_WORDS_PER_COMMENT: int = 150
MIN_COMMENTS_FOR_FINISH: int = 8
MIN_DURATION: int = 20
MAX_DURATION: int = 92


class VoiceOver:

    """
        It includes three TTS(Text-to-Speech) engines:

        sapi5 : provides the male and female voice in Windows
        nsss : provides the male and female voice in MAC-OS
        espeak : provides the male and female voice in every other environment


    """
    # TO DO: Modify Voiceover script to be a stand alone script
    # Implement Type Safety

    def __init__(self):

        self.voiceoverDir = "Voiceovers"
        os.makedirs(self.voiceoverDir, exist_ok=True)

        self.filePath: str = ""
        self.confirmed_files: list[str] = []
        self.created_files: list[str] = []
        self.mp3_files: list[str] = []

        self.duration: float = 0
        self.totalDuration: float = 0
        self.titleAudioDuration: float = 0
        self.audioFile = ""
        self.audioName: str = ""
        # self.format: str = ".mp3"

    def get_duration(mp3_file_path: str) -> float:
        """
        Gets the Duration of the VoiceOver file and Saves it to VideoScript Class

        """

        func = Functions()
        args = ("ffprobe", "-show_entries",
                "format=duration", "-i", mp3_file_path)

        # Runs an FFProbe Command using the Host Computer's Terminal
        string = func.call_terminal(args)

        if string is not None:
            # for debug purposes only
            print(f" duration debug 1: {string}")

            # find the start and end index of the float value
            start_index = string.find('duration=') + len('duration=')
            end_index = string.find('\n', start_index)

            # extract the float value
            float_value = float(string[start_index:end_index])
            # print (f" duration debug 2: {float_value}") # for debug purposes only

            return float_value

    def getTotalDuration(self) -> float:
        return self.totalDuration
 # Gets the Duration of the VoiceOver file and Saves it to VideoScript Class

    def createVoiceOver(self, name: str, fileName: str, text: str) -> AudioFileClip:
        """
        Create VoiceOver Function

            Features: 
            (0) Wraps the gTTS voiceover wrapper for videoscript.py
            (1) Call Create VoiceOVer from main script using Voiceover Class
            (2) pass in the path as a parameter
            (3) returns an audio clip file

            Bugs:
            (1) Creates multiple class instace per voice over and is memory wastefull
        """
        model_name = "tts_models/en/ljspeech/tacotron2-DDC"
        tts = TTS(model_name=model_name, progress_bar=True,
                  gpu=False)  # ElevenLabs(api_key=api_key)
        # print("TTS debug: ", tts)

        @staticmethod
        def get_durationV2(filepath: str) -> float:
            try:
                # Audio Format debug
                return int(math.ceil(float(ffmpeg.probe(filepath)['format']["duration"])))
            except ffmpeg.Error as error:
                print(f"ffmpeg Error: {str(error)}")

        def create_voice_over_linux(self, fileName: str, text: str) -> tuple[AudioFileClip, float]:
            """
            Create voiceover with gTTS and return AudioFileClip

            """
            voiceoverDir = "Voiceovers"
            # filepath = ""
            concat_filePath = os.path.join(
                voiceoverDir, f"{fileName}.mp3")

            filePath = concat_filePath

            print("first check if file already exists in a previous failed run")
            print(f"🔊 Creating Voiceover: {fileName} / {filePath}")
            # traceback.print_stack(limit=5)  # limit avoids huge dumps

            # Documentations:
            # (1) https://github.com/elevenlabs/elevenlabs-python?tab=readme-ov-file
            # Generate TTS with elevenLabs
            # audio = TTS.text_to_speech.convert(
            #    text=text,
            #    voice_id="JBFqnCBsd6RMkjVDRZzb",
            #    model_id="eleven_flash_v2_5",
            #    output_format="mp3_44100_128"
            # )

            tts.tts_to_file(text=text, file_path=filePath)

            # save(audio, filePath)

            # tts.save(filePath)

            # Register as created
            # self.created_files.append(self.filePath)
            duration = get_durationV2(filepath=filePath)

            return AudioFileClip(filePath), duration

        print(f"Duration Debug: {self.duration} / name : {name}")

        "LOGIC FOR CREATING TITLE AND COMMENT VOICEOVERS"
        # Refactored
        "General Logic"

        "Title Logic"
        if name == "title":

            audioClip, self.titleAudioDuration = create_voice_over_linux(
                name, f"{fileName}-{name}", text)

            "Tag Logic"
        elif name == "tag":

            audioClip, self.TagDuration = create_voice_over_linux(
                name, f"{fileName}-{name}", text)

        else:

            audioClip, self.duration = create_voice_over_linux(
                name, f"{fileName}-{name}", text)

        # Store the Audio duration to the class
        # Unless the totalDUration class is't created because the Init() methoid isnt called on creation
        self.totalDuration += float(self.duration)

        # Display Total DUration
        print(f"Total Duration {self.totalDuration}")

        # Error checker 2
        # BUG :
        # - Shouldn't return None Object. Instead, Loop Again.
        if (self.getTotalDuration() + float(self.duration) > MAX_DURATION):
            duration_calc = self.getTotalDuration() + float(self.duration)

            print(
                f" Duration Calc : {duration_calc} > Max Duration: {MAX_DURATION}So,Returns a None Object")

            return None

        return audioClip


class Functions:
    def __init__(self):
        pass

    def call_terminal(self, args) -> str:
        "Makes An Argument  Call to Terminal"

        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output: str = popen.stdout.read().decode("utf-8").strip()

        return output
