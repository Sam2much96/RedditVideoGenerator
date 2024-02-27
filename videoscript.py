from datetime import datetime
from voiceover import VoiceOver
from moviepy.editor import AudioFileClip

# voiceover class refactored

# Constants
# TO DO: Depreciate constants into voiceover class
MAX_WORDS_PER_COMMENT : int = 150
MIN_COMMENTS_FOR_FINISH : int = 8
MIN_DURATION : int = 20
MAX_DURATION : int = 200


class VideoScript:
    """
    VIDEOSCRIPT IS THE MAIN SCRIPT OBJECT OF THIS CODEBASE.
    CONTAINS POINTERS TO REQUIRED AUDIO & VIDEO FILES
    RETURNS INFO TOO

    Contains the Script File, Image FIle and Render Duration 
    Of All On Screen Objects & Audio
    
    """

    def __init__(self,
                 url: str,
                 title: str,
                 fileId : str,
                 file_path : str,
                 audioClip: AudioFileClip
                 ):


        file_path = ""

     
        bit_rate: int = 0
        #totalDuration: float = 0

        # Initialize voiceover class
        #voiceover = VoiceOver()

        # title screenshot file path
        self.titleSCFile : str 
        self.fileId : str = fileId
        # Pointer to voiceover class
        # Bug: If not created first, breaks line 59 self.titleAudioClip. Bad code implementation from the main fork
        self.voiceover = VoiceOver()

        self.fileName : str = f"{datetime.today().strftime('%Y-%m-%d')}-{fileId}"
        self.url = url
        self.title = title

        # create lifetimes for class variables
        self.file_path = file_path
        self.audioClip = audioClip

        "Holds frame data"
        self.frames = []

        " Holds subclass data for the comments videos"
        self.frame = []

        
        
        #self._ready(self.voiceover, self.title)

    #   def _ready(self, local_voiceover: VoiceOver, title : str) -> None:
        # Create Title Audio clip using voiceover pointer class
        # BUG : Creates an unnecessary loop seeing as the voiceover class can be called DIrectly
        # BUG: Skips the initilization phaze of the class which fails to build necessary classes for the Object
        self.titleAudioClip : AudioFileClip = self.voiceover.createVoiceOver("title",self.fileName, title)



        """
        Adds Water Tag Scene As a subclass
        
        """
    
        #Tag Items
        # ScreenShot File Cut in the Dime4nsion of ScreenShot Objects
        self.TagscreenShotFile : str = "YTBanner2.png"
        self.WaterTag : AudioFileClip = self.voiceover.createVoiceOver("tag",self.fileName,"We're Back! Thanks for 140 subs")
        self.TagDuration : float = 0
    

    def canBeFinished(self) -> bool:
        return_value_2: bool = (len(self.frames) > 0) and (
            self.voiceover.totalDuration > MIN_DURATION)
        # for debug purposes only
        print(
            f"can Be Finished : {return_value_2} , min duration: {self.voiceover.totalDuration }")
        return return_value_2

    def canQuickFinish(self) -> bool:
        return_value: bool = (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (
            self.voiceover.totalDuration > MIN_DURATION)
        # for debug purposes only
        print(f"can Quick finish debug : {return_value}")
        return return_value
        # return True

    """
    Adds Comment Scene As a subclass
    
    """
    def addCommentScene(self, text : str, commentId) -> bool:
        print(f'adding comment {commentId} scene')
        # Get the word count
        wordCount = len(text.split())
        print(f"Word Count is : {wordCount}")

        if (wordCount > MAX_WORDS_PER_COMMENT):
            return True

        # Saves Comments Information to Sub Class List
        self.frame: self.ScreenShotScene = ScreenshotScene(
            text,
            commentId,
            self.voiceover.createVoiceOver(commentId, self.getFileName(),text)
        )

        # create comment voice over for comments
        self.frame.audioClip = self.voiceover.createVoiceOver(commentId, self.getFileName(),text)
        self.frame.audioClipDuration = self.voiceover.duration
        print(f"frame debug: {self.frames} ")  # for debug purposes only

        # if (frame.audioClip == None):
        #    return True
        self.frames.append(self.frame)
        return True


    def getFileName(self) -> str:
        self.fileName = f"{datetime.today().strftime('%Y-%m-%d')}-{self.fileId}"
        return self.fileName

    def getAudioDuration(self) -> float:
        return self.voiceover.duration    


class ScreenshotScene:
    text : str = ""
    screenShotFile : str = ""
    commentId : str = ""
    audioClip: AudioFileClip
    audioClipDuration: float

    def __init__(self, text, commentId, audioClip) -> None:
        self.text = text
        self.commentId = commentId
        self.audioClip = audioClip
        self.audioClipDuration: float = 0


