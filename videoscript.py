from datetime import datetime
from voiceover import VoiceOver
from moviepy.editor import AudioFileClip


# Constants
MAX_WORDS_PER_COMMENT = 150
MIN_COMMENTS_FOR_FINISH = 8
MIN_DURATION = 20
MAX_DURATION = 200


class VideoScript:
    """
    THE MAIN SCRIPT OBJECT OF THIS CODEBASE.
    CONTAINS POINTERS TO REQUIRED AUDIO & VIDEO FILES
    RETURNS INFO TOO
    
    """

    def __init__(self,
                 url: str,
                 title: str,
                 fileId,
                 file_path,
                 audioClip: AudioFileClip
                 ):


        file_path = ""

     
        bit_rate: int = 0
        totalDuration: float = 0

        # Initialize voiceover class
        voiceover = VoiceOver()

        # Pointer to voiceover class
        # Bug: If not created first, breaks line 59 self.titleAudioClip. Bad code implementation from the main fork
        self.voiceover = voiceover

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

        # Set default duration
        self.duration: float = 0  # Audio Clip duration
        self.totalDuration: float = totalDuration  # Audio Clip duration

        self.titleAudioDuration: float = 0

        # Create Title Audio clip using voiceover pointer class
        # Bug : Creates an unnecessary loop seeing as the voiceover class can be called DIrectly
        # Bug: Skips the initilization phaze of the class which fails to build necessary classes for the Object
        self.titleAudioClip : AudioFileClip = self.__createVoiceOver("title", title)



        """
        Adds Water Tag Scene As a subclass
        
        """
    
        #Tag Items
        # ScreenShot File Cut in the Dime4nsion of ScreenShot Objects
        self.TagscreenShotFile : str = "YTBanner2.png"
        self.WaterTag : AudioFileClip = self.__createVoiceOver("tag","Let's Take This Channel To 1000 Subs! hashtag Subscribe Now, my Neeg!")
        self.TagDuration : float = 0

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

    """
    Adds Comment Scene As a subclass
    
    """
    def addCommentScene(self, text, commentId) -> bool:
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

    def getFileName(self) -> str:
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
        
        "General Logic"
        if name != "title" or "tag":
            # Creates a VoiceOver using pytts
            # Returns a Tuple containing an Audio Clip file and it's duration as floats
            # Set User Preferences
            self.voiceover.engine.setProperty("voice", "english-us")

            audioClip, self.duration = self.voiceover.create_voice_over_linux(
                f"{self.fileName}-{name}", text)

        "Title Logic"
        if name == "title":

            # Set User Preferences
            self.voiceover.engine.setProperty("voice", "english_rp")

            audioClip, self.titleAudioDuration = self.voiceover.create_voice_over_linux(
                f"{self.fileName}-{name}", text)

        "Tag Logic"
        if name == "tag":
            # Set User Preferences
            self.voiceover.engine.setProperty("voice", "Persian+English-US")

            audioClip, self.TagDuration = self.voiceover.create_voice_over_linux(
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


