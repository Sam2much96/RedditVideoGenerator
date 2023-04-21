from datetime import datetime
from moviepy.editor import AudioFileClip
#import voiceover
import pyttsx3 # for voiceovers
import os

MAX_WORDS_PER_COMMENT = 100
MIN_COMMENTS_FOR_FINISH = 4
MIN_DURATION = 20
MAX_DURATION = 58

class VideoScript:
    title = ""
    fileName = ""
    titleSCFile = ""
    url = ""
    totalDuration = 0
    frames = []

    def __init__(self, url, title, fileId) -> None:
        self.fileName = f"{datetime.today().strftime('%Y-%m-%d')}-{fileId}"
        self.url = url
        self.title = title

        # Create Title Audio clip
        self.titleAudioClip = self.__createVoiceOver("title", title)

    def canBeFinished(self) -> bool:
        return (len(self.frames) > 0) and (self.totalDuration > MIN_DURATION)

    def canQuickFinish(self) -> bool:
        return (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (self.totalDuration > MIN_DURATION)

    def addCommentScene(self, text, commentId) -> bool:
        wordCount = len(text.split())
        print (wordCount)

        if (wordCount > MAX_WORDS_PER_COMMENT):
            #print (11111111)
            return True
        frame = ScreenshotScene(text, commentId)
        
        #print (frame) # for debug purposes only

        # create comment voice over
        frame.audioClip = self.__createVoiceOver(commentId, text)
        print (222222)
        print (frame.audioClip)

        if (frame.audioClip == None):
            return True
        self.frames.append(frame)
        return True

    def getDuration(self):
        return self.totalDuration

    def getFileName(self):
        return self.fileName
    
    def __createVoiceOver(self, name, text) -> AudioFileClip: 

        # Bugs out in Production
        file_path = VoiceOver.create_voice_over(VoiceOver,f"{self.fileName}-{name}", text)
        audioClip = AudioFileClip(file_path)
        if (self.totalDuration + audioClip.duration > MAX_DURATION):
            return None
        self.totalDuration += audioClip.duration
        return audioClip

class ScreenshotScene:
    text = ""
    screenShotFile = ""
    commentId = ""

    def __init__(self, text, commentId) -> None:
        self.text = text
        self.commentId = commentId



class VoiceOver:

    voiceoverDir = "Voiceovers"
    engine = pyttsx3.init("espeak", True)
    

    def __init__(self, engine):

        self.engine = engine
        self.voiceoverDir = voiceoverDir

    def create_voice_over(self, fileName, text)-> str:
        print ("Creating Voicever")
        filePath : str = f"{self.voiceoverDir}/{fileName}.mp3"


        self.engine.save_to_file(text, filePath)
        self.engine.runAndWait()


        return filePath
