from datetime import datetime
from moviepy.editor import AudioFileClip
import pyttsx3  # for voiceovers
import os
import subprocess
import ffmpeg
from mutagen.wave import WAVE
import time
MAX_WORDS_PER_COMMENT = 100
MIN_COMMENTS_FOR_FINISH = 4
MIN_DURATION = 20
MAX_DURATION = 58


class VideoScript:
    title : str = ""
    fileName : str = ""
    titleSCFile = ""
    titleAudioDuration : int = 0
    url = ""
    totalDuration = 0
   
    # Holds frame data
    frames = []

    # Holds subclass data for the comments videos
    frame = []

    file_path = ""
    
    titleAudioClip = AudioFileClip
    audioClip = AudioFileClip

    bit_rate : int = 0

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
        return_value_2 : bool = (len(self.frames) > 0) and (self.totalDuration > MIN_DURATION)
        print(f"can Be Finished : {return_value_2} , min duration: {self.totalDuration }")  # for debug purposes only
        return return_value_2

    def canQuickFinish(self) -> bool:
        return_value: bool = (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (
            self.totalDuration > MIN_DURATION)
        print(f"can Quick finish debug : {return_value}")  # for debug purposes only
        return return_value
        #return True

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
        #self.frames.append(frame)
        return True

    def getDuration(self):
        return self.totalDuration

    def getFileName(self):
        return self.fileName

    # Call Creatyte VoiceOVer from main script
    def __createVoiceOver(self, name, text) -> AudioFileClip:

        # Creates a VoiceOver using pytts
        audioClip = VoiceOver.create_voice_over_linux(
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
    audioClip : AudioFileClip

    def __init__(self, text, commentId, audioClip) -> None:
        self.text = text
        self.commentId = commentId
        self.audioClip = audioClip


class VoiceOver:

    # To DO: 
    # (1) Implement Proper Engine Loop (done)
    # (2) Implement gender and voice changes as Class parameters

    voiceoverDir = "Voiceovers"
    engine = pyttsx3.init("sapi5", True)
    filePath: str = ''

    confirmed_files: list[str] = ['']
    mp3_files: list[str] = []
    created_files: list[str] = []

    bit_rate : int = engine.getProperty("rate")
    duration : float = 0
    
    audioFile = "" # Holds the Output stream for the Audio File
    audioName : str = "" # Audio File name
    sizeBytes : int = 0
    Debug = False
    format : str = ".wav"# audio file format

    def __init__(self, engine):
        "Initialize Lifetimes"

        self.engine = engine
        self.voiceoverDir = voiceoverDir
        #self.engine.runAndWait()
        self.engine.startLoop(True)
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
    # Generates Voice over
    # Runs as a Loop in main.py
    # Generates Audio clip and stores generated clip data in Class Variables


    def create_voice_over_linux(self, fileName, text) -> AudioFileClip:
        print(f"Creating Voicever :{ fileName}")
        absolute_path = r"C:\RedditVideoGenerator"  
        concat_filePath = f"{absolute_path}\{self.voiceoverDir}\{fileName}{self.format}"
        
        self.filePath = concat_filePath#.encode('unicode_escape').decode()
       
        self.engine.save_to_file(text, self.filePath)

        self.engine.runAndWait()

        
        if (self.locate_or_generate_mp3(self)):

            # Store File
            self.created_files.append( self.filePath)
            
            self.duration = self.get_durationV2(self ,self.filePath)

            print (f"Duration debug 2: {self.duration} / Path: {self.filePath} / Cr8ted Files: {self.created_files}") # for debug purposes

        
            # Loads the Generated audo clip && returns it
            # Breaks here because audio file isnt generated
            return AudioFileClip(self.filePath) # filePath # audioName

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
            
            #self.engine.runAndWait()
            #self.engine.startLoop(True)
            #time.sleep(5)
            

        # After file is generated         
        if os.path.isfile(self.filePath):
            print (f" Generated: {self.filePath}")
           
            return True    

        if not self.filePath in self.confirmed_files:
            # append confirmed file path to list
            self.confirmed_files.append(self.filePath)
            return True
        
        
        if self.Debug:
                 # Get Audio File
            in_stream = ffmpeg.input(self.filePath)

            # Copy it
            out_stream = ffmpeg.output(in_stream, str("testing--" + self.filePath), f="wav")

            # Let FFmpeg process audio file for debugging
            out_stream.run()
            
        
        return False
    
    # Gets the Duration of the VoiceOver file and Saves it to VideoScript Class
    def get_duration( mp3_file_path : str)-> float:
            args=("ffprobe","-show_entries", "format=duration","-i",mp3_file_path)
            popen = subprocess.Popen(args, stdout = subprocess.PIPE)
            popen.wait()
            output = popen.stdout.read()

            # convert bytes to string
            string = output.decode('utf-8')

            if string != "":
                print (f" duration debug 1: {string}") # for debug purposes only
                
                # find the start and end index of the float value
                start_index = string.find('duration=') + len('duration=')
                end_index = string.find('\n', start_index)

                # extract the float value
                float_value = float(string[start_index:end_index])
                #print (f" duration debug 2: {float_value}") # for debug purposes only

                return float_value


     # Gets the Duration of the VoiceOver file and Saves it to VideoScript Class
    def get_durationV2( self ,wav_file_path : str)-> float:
            try:  
                
                
                # Probe it
                stream_info = ffmpeg.probe(wav_file_path)
                
                # Get Audio File info
                #print (stream_info)
                
                #Store Audio file details to class
                self.audioName = stream_info['format']['filename']

                self.bit_rate = int(stream_info['format']['bit_rate'])
                self.sizeBytes = int(stream_info['format']['size'])
               
                # Calculate Audio duration
                
                self.duration = (self.sizeBytes / self.bit_rate) #* 1000
                print (self.duration)
                return self.duration
                
            except ffmpeg.Error as error:
                print(f"ffmpeg Error: {str(error)}")

    def get_durationV3(self,wav_file_path)-> float:
     try:
        # Copy the Wav file using ffmpeg input
        
        audio = WAVE(wav_file_path)
        print(f"Duration Debug 3: {audio.info.length}")

    
        return audio.info.length
     except Exception as e:
        print(f"Error: {str(e)}")

