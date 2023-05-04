from datetime import datetime
from moviepy.editor import AudioFileClip
# import voiceover
import pyttsx3  # for voiceovers
import os
import subprocess
import ffmpeg
# from mutagen.mp3 import MP3
import time
MAX_WORDS_PER_COMMENT = 100
MIN_COMMENTS_FOR_FINISH = 4
MIN_DURATION = 20
MAX_DURATION = 58


class VideoScript:
    title: str = ""
    fileName: str = ""
    titleSCFile = ""
    titleAudioDuration: int = 0
    url = ""
    totalDuration = 0

    # Holds frame data
    frames = []

    # Holds subclass data for the comments videos
    frame = []

    file_path = ""

    titleAudioClip = AudioFileClip
    audioClip = AudioFileClip

    bit_rate: int = 0

    def __init__(self, url, title, fileId, file_path, audioClip):
        self.fileName = f"{datetime.today().strftime('%Y-%m-%d')}-{fileId}"
        self.url = url
        self.title = title

        # create lifetimes for class variables
        self.file_path = file_path
        self.audioClip = audioClip

        # Create Title Audio clip
        self.titleAudioClip = self.__createVoiceOver("title", title)

        self.frames = []
        self.frame = []

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

    def addCommentScene(self, text, commentId) -> bool:
        # Get the word count

        wordCount = len(text.split())
        print(wordCount)

        if (wordCount > MAX_WORDS_PER_COMMENT):
            return True

        # Saves Comments Information to Sub Class List
        self.frame = ScreenshotScene(
            text,
            commentId,
            self.__createVoiceOver(commentId, text)
        )

        # create comment voice over for comments
        self.frame.audioClip = self.__createVoiceOver(commentId, text)

        print(f"frame debug: {self.frames}")  # for debug purposes only

        # if (frame.audioClip == None):
        #    return True
        # self.frames.append(frame)
        return True

    def getDuration(self):
        return self.totalDuration

    def getFileName(self):
        return self.fileName

    def __createVoiceOver(self, name, text) -> AudioFileClip:

        # Creates a VoiceOver using pytts
        audioClip = VoiceOver.create_voice_over(
            VoiceOver, f"{self.fileName}-{name}", text)

        # Error checker 2
        if (self.totalDuration + audioClip.duration > MAX_DURATION):
            return None
        self.totalDuration += audioClip.duration
        return audioClip


class ScreenshotScene:
    text = ""
    screenShotFile = ""
    commentId = ""
    audioClip: AudioFileClip

    def __init__(self, text, commentId, audioClip) -> None:
        self.text = text
        self.commentId = commentId
        self.audioClip = audioClip


class VoiceOver:

    # To DO:
    # (1) Implement Proper Engine Loop (done)
    # (2) Implement gender and voice changes as Class parameters

    voiceoverDir = "Voiceovers"
    engine = pyttsx3.init("espeak", True)
    filePath: str = ''

    confirmed_files: list[str] = ['']
    mp3_files: list[str] = []
    created_files: list[str] = []

    bit_rate: int = engine.getProperty("rate")
    # duration : float =

    def __init__(self, engine):

        self.engine = engine
        self.voiceoverDir = voiceoverDir
        # self.engine.runAndWait()
        self.engine.startLoop(True)
        self.filePath = filePath
        self.confirmed_files = confirmed_files
        self.created_files = created_files
        self.created_files = mp3_files
        self.bit_rate = bit_rate
        self.duration = self.get_durationV2(self.filePath)

    # Generates Voice over
    # To Do:
    # Runs as a Loop in main.py
    # Generates Audio clip and stores generated clip data in Class Variables

    def create_voice_over(self, fileName, text) -> AudioFileClip:
        print(f"Creating Voicever :{ fileName}")
        self.filePath = f"{self.voiceoverDir}/{fileName}.mp3"

        self.engine.save_to_file(text, self.filePath)

        if (self.locate_or_generate_mp3(self)):

            # Store File
            self.created_files.append(self.filePath)

            # try :
            #    # store Audio clip duration
            #    self.duration = MP3(self.filePath).info.length
            # except Exception as err:
            #    print (err)

            self.duration = self.get_durationV2(self.filePath)

            # Return audo clip
            return AudioFileClip(self.filePath)

    def locate_or_generate_mp3(self) -> bool:
        # A general purpose debugger for
        print("locating & Saving all .mp3 files in root dir")

        # Search the "Voiceovers" subdirectory
        voiceovers_dir = os.path.join(".", "Voiceovers")

        for file in os.listdir(voiceovers_dir):
            if file.endswith(".mp3"):
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

            # Breaks here

            # self.engine.runAndWait()
            # print(f" Mp3 files debug: {self.mp3_files}")
            return True

        if not self.filePath in self.confirmed_files:
            # append confirmed file path to list
            self.confirmed_files.append(self.filePath)
            return True
        return True

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
            print(f" duration debug 1: {string}")  # for debug purposes only

            # find the start and end index of the float value
            start_index = string.find('duration=') + len('duration=')
            end_index = string.find('\n', start_index)

            # extract the float value
            float_value = float(string[start_index:end_index])
            # print (f" duration debug 2: {float_value}") # for debug purposes only

            return float_value

 # Gets the Duration of the VoiceOver file and Saves it to VideoScript Class
    def get_durationV2(mp3_file_path: str) -> float:
        try:
            return ffmpeg.probe(mp3_file_path)['format']['duration']

        except ffmpeg.Error as error:
            print(f"Error: {str(error)}")
