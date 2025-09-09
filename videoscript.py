from datetime import datetime
from voiceover import VoiceOver
from moviepy.editor import AudioFileClip

# voiceover class refactored

# Constants
# TO DO: Depreciate constants into voiceover class
MAX_WORDS_PER_COMMENT: int = 100
MIN_COMMENTS_FOR_FINISH: int = 8
MIN_DURATION: int = 20
MAX_DURATION: int = 100


class VideoScript:
    """
    Videoscript Is thie main script object datatype &
    contains pointers to required Audio & Video Files


    Contains the Script File, Image FIle and Render Duration 
    Of All On Screen Objects & Audio

    """

    def __init__(self,
                 url: str,
                 title: str,
                 fileId: str,
                 file_path: str,
                 audioClip: AudioFileClip
                 ):

        file_path = ""

        bit_rate: int = 0
        # totalDuration: float = 0
        print("file id debug: ", fileId)
        # Initialize voiceover class
        # voiceover = VoiceOver()

        # title screenshot file path
        self.titleSCFile: str
        self.fileId: str = fileId
        # Pointer to voiceover class
        self.voiceover = VoiceOver()

        self.fileName: str = f"{datetime.today().strftime('%Y-%m-%d')}-{fileId}"
        self.url = url
        self.title = title

        # create lifetimes for class variables
        self.file_path = file_path
        self.audioClip = audioClip

        "Holds frame data"
        self.frames = []

        " Holds subclass data for the comments videos"
        self.frame: ScreenshotScene = None

        # creates the title
        # bug: (1) creates tag and title objects twice?
        self.titleAudioClip: AudioFileClip = self.voiceover.createVoiceOver(
            "title", self.fileName, title)

        # Tag Items
        # note: ScreenShot File Cut in the Dime4nsion of ScreenShot Objects
        self.TagscreenShotFile: str = "YTBanner2.png"
        self.WaterTag: AudioFileClip = self.voiceover.createVoiceOver(
            "tag", self.fileName, "Thanks for 170 Subs! ma Ninja's .Video Game Link In Bio, support a small youtuber!")
        self.TagDuration: float = 0

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

    def addCommentScene(self, text: str, commentId) -> bool:
        """
        Adds Comment Scene As an object within
        the videoscript scene

        """
        print(f'adding comment {commentId} scene')
        # Get the word count
        wordCount = len(text.split())
        print(f"Word Count is : {wordCount}")

        if (wordCount > MAX_WORDS_PER_COMMENT):
            return True

        # create comment voice over for comments
        audioClip = self.voiceover.createVoiceOver(
            commentId, self.getFileName(), text)

        audioClipDuration = self.voiceover.duration

        # Create A screenshot comment scene instance
        # Saves Comments Information to Sub Class List
        self.frame = ScreenshotScene(
            text,
            commentId,
            audioClip
        )

        self.frame.setAudioClipDuration(audioClipDuration)

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
    """
    Screen Shot Data Structure as an Object 
    Containing Audio, Text and Audio duration data
    """

    text: str = ""
    screenShotFile: str = ""
    commentId: str = ""
    audioClip: AudioFileClip
    audioClipDuration: float

    def __init__(self, text: str, commentId: str, audioClip: AudioFileClip) -> None:
        self.text = text
        self.commentId = commentId
        self.audioClip = audioClip
        self.audioClipDuration: float = 0

    def setAudioClipDuration(self, duration: float):
        """Assign audio clip and duration safely"""
        self.audioClipDuration = duration

    # def getAudioDuration(self) -> float:
    #    """Getter for audio clip duration"""
    #    return self.audioClipDuration
