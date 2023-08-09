from datetime import datetime
from moviepy.editor import AudioFileClip
import pyttsx3  # for voiceovers
import os
import subprocess
import ffmpeg
import math
# from mutagen.mp3 import MP3
import time

# Constants
MAX_WORDS_PER_COMMENT = 200
MIN_COMMENTS_FOR_FINISH = 8
MIN_DURATION = 20
MAX_DURATION = 58


class VideoScript:

    def __init__(self,
                 url: str,
                 title: str,
                 fileId,
                 file_path,
                 audioClip: AudioFileClip
                 ):

        # title: str = ""
        fileName: str = ""
        titleSCFile = ""
        titleAudioDuration: float
        # url: str = ""

        # Holds frame data
        frames = []

        # Holds subclass data for the comments videos
        frame = []

        file_path = ""

        titleAudioClip = AudioFileClip
        # audioClip = AudioFileClip

        bit_rate: int = 0
        totalDuration: float = 0

        # Initialize voiceover class
        voiceover = VoiceOver()

        # Pointer to voiceover class
        # Bug: If not created first, breaks line 59 self.titleAudioClip. Bad code implementation from the main fork
        self.voiceover = voiceover

        self.fileName = f"{datetime.today().strftime('%Y-%m-%d')}-{fileId}"
        self.url = url
        self.title = title

        # create lifetimes for class variables
        self.file_path = file_path
        self.audioClip = audioClip

        self.frames = []
        self.frame = []

        # Set default duration
        self.duration: float = 0  # Audio Clip duration
        self.totalDuration: float = totalDuration  # Audio Clip duration

        self.titleAudioDuration: float = 0

        # Create Title Audio clip using voiceover pointer class
        # Bug : Creates an unnecessary loop seeing as the voiceover class can be called DIrectly
        # Bug: Skips the initilization phaze of the class which fails to build necessary classes for the Object
        self.titleAudioClip = self.__createVoiceOver("title", title)

    def canBeFinished(self) -> bool:
        return_value_2: bool = (len(self.frames) > 0) and (
            self.totalDuration > MIN_DURATION)
        # for debug purposes only
        print(
            f"can Be Finished : {return_value_2} , min duration: {self.totalDuration }")
        return return_value_2

    def canQuickFinish(self) -> bool:
        return_value: bool = (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (
            self.totalDuration > MIN_DURATION)
        # for debug purposes only
        print(f"can Quick finish debug : {return_value}")
        return return_value
        # return True

    # Adds Comment Scene As a subclass
    def addCommentScene(self, text, commentId) -> bool:
        print('adding comment scene')
        # Get the word count
        wordCount = len(text.split())
        print(wordCount)

        if (wordCount > MAX_WORDS_PER_COMMENT):
            return True

        # Saves Comments Information to Sub Class List
        self.frame: self.ScreenShotScene = ScreenshotScene(
            text,
            commentId,
            self.__createVoiceOver(commentId, text)
        )

        # create comment voice over for comments
        self.frame.audioClip = self.__createVoiceOver(commentId, text)
        self.frame.audioClipDuration = self.duration
        print(f"frame debug: {self.frames} ")  # for debug purposes only

        # if (frame.audioClip == None):
        #    return True
        self.frames.append(self.frame)
        return True

    def getDuration(self) -> float:
        return self.totalDuration

    def getFileName(self):
        return self.fileName

    def getAudioDuration(self):
        return self.duration

    # Call Create VoiceOVer from main script using Voiceover Class

    def __createVoiceOver(self, name, text) -> AudioFileClip:
        "LOGIC FOR CREATING VOICEOVER FILES"

        # Debug VOiceover class
        print(f" Voiceover Object Debug:{self.voiceover}")
        print(f"Duration Debug: {self.duration}")

        "LOGIC FOR CREATING TITLE AND COMMENT VOICEOVERS"
        if name != "title":
            # Creates a VoiceOver using pytts
            # Returns a Tuple containing an Audio Clip file and it's duration as floats
            # Set User Preferences
            self.voiceover.engine.setProperty("voice", "english-us")

            audioClip, self.duration = self.voiceover.create_voice_over_linux(
                f"{self.fileName}-{name}", text)

        if name == "title":

            # Set User Preferences
            self.voiceover.engine.setProperty("voice", "english_rp")

            audioClip, self.titleAudioDuration = self.voiceover.create_voice_over_linux(
                f"{self.fileName}-{name}", text)

        # Store the Audio duration to the class
        # Unless the totalDUration class is't created because the Init() methoid isnt called on creation
        self.totalDuration += float(self.duration)

        # Display Total DUration
        print(f"Total Duration {self.totalDuration}")

        # Error checker 2
        # Bug 1 :
        # - Shouldn't return None Object. Instead, Loop Again.
        if (self.getDuration() + float(self.duration) > MAX_DURATION):
            duration_calc = self.getDuration() + float(self.duration)

            print(
                f" Duration Calc : {duration_calc} > Max Duration: {MAX_DURATION}So,Returns a None Object")

            return None

        return audioClip


class ScreenshotScene:
    text = ""
    screenShotFile = ""
    commentId = ""
    audioClip: AudioFileClip
    audioClipDuration: float

    def __init__(self, text, commentId, audioClip) -> None:
        self.text = text
        self.commentId = commentId
        self.audioClip = audioClip
        self.audioClipDuration: float = 0


class VoiceOver:

    """
        It includes three TTS(Text-to-Speech) engines:

        sapi5 : provides the male and female voice in Windows
        nsss : provides the male and female voice in MAC-OS
        espeak : provides the male and female voice in every other environment

    """

    def __init__(self):
        # To DO:
        # (1) Implement Proper Engine Loop (done)
        # (2) Implement gender and voice changes as Class parameters

        voiceoverDir = "Voiceovers"
        engine = pyttsx3.init("espeak", True)

        # Voice Types
        voices = engine.getProperty("voices")

        # Voice Rate
        rate = engine.getProperty("rate")

        # Volume
        volume = engine.getProperty("volume")

        filePath: str = ''

        confirmed_files: list[str] = ['']
        mp3_files: list[str] = []
        created_files: list[str] = []

        bit_rate: int = engine.getProperty("rate")

        duration: float = 0
        audioFile = ""  # Holds the Output stream for the Audio File
        audioName: str = ""  # Audio File name
        sizeBytes: int = 0
        Debug = False
        format: str = ".mp3"  # audio file format

        "Initialize Lifetimes"

        self.engine = engine
        self.voices = voices
        self.rate = rate
        self.volume = volume
        self.voiceoverDir = voiceoverDir

        self.filePath = filePath
        self.confirmed_files = confirmed_files
        self.created_files = created_files
        self.created_files = mp3_files
        self.bit_rate = bit_rate
        self.duration = duration

        self.audioFile = audioFile
        self.audioName = audioName
        self.sizeBytes = sizeBytes
        self.Debug = Debug
        self.format = format

        # All MP3 Files in Directory
        self.mp3_files = mp3_files

    """
    - Generates Voice over
    - Runs as a Loop in main.py
    - Generates Audio clip and stores generated clip data in Class Variables

    """

    def create_voice_over_linux(self, fileName, text):
        func = Functions()
        args = "whoami"
        UserName = func.call_terminal(args)

        print(f"Creating Voicever :{ fileName} for user {UserName}")
        print(f"VoiceOver Engine Object {self.engine} for {fileName}")

        absolute_path = f"/home/{UserName}/RedditVideoGenerator"
        concat_filePath = f"{absolute_path}/{self.voiceoverDir}/{fileName}{self.format}"

        self.filePath = concat_filePath  # .encode('unicode_escape').decode()

        self.engine.save_to_file(text, self.filePath)

        #   self.engine.runAndWait()

        if (self.locate_or_generate_mp3() == True):

            # Store File
            self.created_files.append(self.filePath)

            self.duration = self.get_durationV2()  # self.filePath

            # for debug purposes
            print(
                f"Duration debug 2: {self.duration} / Path: {self.filePath} / Cr8ted Files: {self.created_files}")

            # Loads the Generated audo clip && returns it
            # Breaks here because audio file isnt generated
            # filePath # audioName
            return AudioFileClip(self.filePath), self.duration

    # Locates of Generates the Voiceover file
    def locate_or_generate_mp3(self) -> bool:
        """
        Bugs: 

        While loop on line 315 works but has no continuatity in the prgramming logic
        """
        x = 0
        # A general purpose debugger for
        print("locating & Saving all .wav files in root dir")

        # Search the "Voiceovers" subdirectory
        voiceovers_dir = os.path.join(".", "Voiceovers")

        for file in os.listdir(voiceovers_dir):
            if file.endswith(self.format):
                self.mp3_files.append(os.path.join(voiceovers_dir, file))

        # Checks if current file exists
        # Buggy Condiional
        # Runs As Loop
        while not os.path.isfile(self.filePath):

            print(f"File not found at path:{self.filePath}, generating ")

            # For Debug Purposes only
            print(
                f' CHecking for  Audio File{x} times >>>>>{os.path.isfile(self.filePath)}')
            x += 1

            self.engine.runAndWait()  # Introduces a stuck bug into the program loop
            # self.engine.startLoop(True)
            time.sleep(2)
            print("Sleeping for 2 Seconds")

        # After file is generated
        if os.path.isfile(self.filePath):
            print(f" Generated: {self.filePath}")

            return True

        # Save Files to Global Class Array
        if not self.filePath in self.confirmed_files:
            # append confirmed file path to list
            self.confirmed_files.append(self.filePath)
            return True

        # Debug Conditional
        if self.Debug:
            # Get Audio File
            in_stream = ffmpeg.input(self.filePath)

            # Copy it
            out_stream = ffmpeg.output(in_stream, str(
                "testing--" + self.filePath), f="wav")

            # Let FFmpeg process audio file for debugging
            out_stream.run()

        return False

    # Gets the Duration of the VoiceOver file and Saves it to VideoScript Class
    def get_duration(mp3_file_path: str) -> float:
        func = Functions()
        args = ("ffprobe", "-show_entries",
                "format=duration", "-i", mp3_file_path)

        # Runs an FFProbe Command using the Host Computer's Terminal
        string = func.call_terminal(args)

        # if string != "": # <- Depreciated
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

 # Gets the Duration of the VoiceOver file and Saves it to VideoScript Class
    def get_durationV2(self) -> float:
        try:
            # Audio Format debug
            return int(math.ceil(float(ffmpeg.probe(self.filePath)['format']["duration"])))
        except ffmpeg.Error as error:
            print(f"ffmpeg Error: {str(error)}")

    def get_durationV3(self, wav_file_path) -> float:
        try:
            # Copy the Wav file using ffmpeg input

            audio = WAVE(wav_file_path)
            print(f"Duration Debug 3: {audio.info.length}")

            return audio.info.length
        except Exception as e:
            print(f"Error: {str(e)}")

    def languages(self):
        # Print sout the Voice ID for All Languages supported by pyttsx3
        """
        Supported Languages

            0-afrikaans
            1-aragonese
            2-bulgarian
            3-bengali
            4-bosnian
            5-catalan
            6-czech
            7-welsh
            8-german
            9-greek
            10-default
            11-english
            12-en-scottish
            13-english-north
            14-english_rp
            15-english_wmids
            16-english-us
            -esperanto
            -spanish
            -spanish-latin-am
            -estonian
            -basque-test
            -Persian+English-UK
            -Persian+English-US
            -finnish
            -french-Belgium
            -french
            -irish-gaeilge
            -greek-ancient
            -gujarati-test
            -hindi
            -croatian
            -hungarian
            -armenian
            -armenian-west
            -interlingua
            -indonesian
            -icelandic
            -italian
            -georgian
            -kannada
            -kurdish
            -latin
            -lingua_franca_nova
            -lithunian
            -latvian
            -macedonian
            -malayalam
            -malay
            -nepali
            -dutch
            -norwegian
            -punjabi
            -polish
            -brazil
            -romanian
            -russian
            -slovak
            -albanian
            -serbian
            -swedish
            -swahili-test
            -tamil
            -telugu-test
            -turkish
            -vietnam
            -vietnam_hue
            -vietnam_sgn
            -Mandarin
            -cantonese

        """
        for i in self.voices:
            print(i, i.id)

        for q in self.voices:
            print(q)


class Functions:
    def __init__(self):
        pass

    def call_terminal(self, args) -> str:
        "Makes An Argument  Call to Terminal"

        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output: str = popen.stdout.read().decode("utf-8").strip()

        return output
