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
MAX_WORDS_PER_COMMENT = 100
MIN_COMMENTS_FOR_FINISH = 4
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

    # Call Creatyte VoiceOVer from main script
    def __createVoiceOver(self, name, text) -> AudioFileClip:
        "LOGIC FOR CREATING VOICEOVER FILES"

        # Debug VOiceover class
        print(self.voiceover)
        print(f"Duration Debug: {self.duration}")

        if name != "title":
            # Creates a VoiceOver using pytts
            # Returns a Tuple containing an Audio Clip file and it's duration as floats
            audioClip, self.duration = self.voiceover.create_voice_over_linux(
                f"{self.fileName}-{name}", text)

        if name == "title":
            audioClip, self.titleAudioDuration = self.voiceover.create_voice_over_linux(
                f"{self.fileName}-{name}", text)

        # Store the Audio duration to the class
        # Unless the totalDUration class is't created because the Init() methoid isnt called on creation
        self.totalDuration += float(self.duration)

        # Display Total DUration
        print(f"Total Duration {self.totalDuration}")

        # Error checker 2
        if (self.getDuration() + float(self.duration) > MAX_DURATION):
            print(1111111)
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

    def __init__(self):
        # To DO:
        # (1) Implement Proper Engine Loop (done)
        # (2) Implement gender and voice changes as Class parameters

        voiceoverDir = "Voiceovers"
        engine = pyttsx3.init("espeak", True)  # pyttsx3.init("sapi5", True)
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
        self.voiceoverDir = voiceoverDir
        # self.engine.runAndWait()
        # self.engine.startLoop(True)
        self.filePath = filePath
        self.confirmed_files = confirmed_files
        self.created_files = created_files
        self.created_files = mp3_files
        self.bit_rate = bit_rate
        self.duration = duration  # self.get_durationV2(self.filePath)

        self.audioFile = audioFile
        self.audioName = audioName
        self.sizeBytes = sizeBytes
        self.Debug = Debug
        self.format = format

        # All MP3 Files in Directory
        self.mp3_files = mp3_files

    # Generates Voice over
    # Runs as a Loop in main.py
    # Generates Audio clip and stores generated clip data in Class Variables

    # -> AudioFileClip, float:
    def create_voice_over_linux(self, fileName, text):

        print(f"Creating Voicever :{ fileName}")
        print(self.engine)
        absolute_path = r"/home/samuel/RedditVideoGenerator"
        concat_filePath = f"{absolute_path}/{self.voiceoverDir}/{fileName}{self.format}"

        self.filePath = concat_filePath  # .encode('unicode_escape').decode()

        self.engine.save_to_file(text, self.filePath)

        #   self.engine.runAndWait()

        if (self.locate_or_generate_mp3()):

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
        # A general purpose debugger for
        print("locating & Saving all .wav files in root dir")

        # Search the "Voiceovers" subdirectory
        voiceovers_dir = os.path.join(".", "Voiceovers")

        for file in os.listdir(voiceovers_dir):
            if file.endswith(self.format):
                self.mp3_files.append(os.path.join(voiceovers_dir, file))

        # Checks if current file exists
        while not os.path.isfile(self.filePath):
            print(f"File not found at path: {self.filePath}, generating ")

            self.engine.runAndWait()
            # self.engine.startLoop(True)
            time.sleep(5)

        # After file is generated
        if os.path.isfile(self.filePath):
            print(f" Generated: {self.filePath}")

            return True

        if not self.filePath in self.confirmed_files:
            # append confirmed file path to list
            self.confirmed_files.append(self.filePath)
            return True

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
        args = ("ffprobe", "-show_entries",
                "format=duration", "-i", mp3_file_path)
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()

        # convert bytes to string
        string = output.decode('utf-8')

        if string != "":
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
