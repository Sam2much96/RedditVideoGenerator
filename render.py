import reddit
import screenshot
from videoscript import VoiceOver, VideoScript

from moviepy.editor import *


import time
import random
import configparser
import sys
import math


from os import listdir, system
from os.path import isfile, join



class Render:
    """
    RUNS THE RENDER SCRIPT FOR THE MAIN VIDEO LOOP, 
    CONTAINING POINTERS TO ALL REQUIRED SUB CLASSES
      AND ELEMENTS
    
            Bugs:
        (1)



    Features:

    TO-DO:
        (1) Implement Threads
        (2) Re-Factor Voiceover Again
    
    """


    def __init__(self):
        
        


        # Final Video Size
        self.w: int = 0
        self.h: int = 0

        # Load User Config Files
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.outputDir = self.config["General"]["OutputDirectory"]

        self.startTime = time.time()
        self.script : VideoScript = None

    
    
    """
    Creates Regular Video Posts
    """
    def createVideo(self):

        # Get script from reddit
        # If a post id is listed, use that. Otherwise query top posts
        if (len(sys.argv) == 2):

            # Creates a Video Script Class from A Reddit Post Content ID
            self.script = reddit.getContentFromId(self.outputDir, sys.argv[1])
        else:
            # Auto Selects Content

            postOptionCount = int(self.config["Reddit"]["NumberOfPostsToSelectFrom"])

            # Creates a Video Script Class
            self.script = reddit.getContent(self.outputDir, postOptionCount)
   
        fileName = self.script.getFileName()

        # Create screenshots for Video Script Object
        screenshot.getPostScreenshots(fileName, self.script)

        # Setup background clip
        bgDir = self.config["General"]["BackgroundDirectory"]
        bgPrefix = self.config["General"]["BackgroundFilePrefix"]
        bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
        bgCount = len(bgFiles)

        # Selects a randomized Background Clip Number
        bgIndex = random.randint(0, bgCount-1)
        backgroundVideo = VideoFileClip(
            filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4",
            audio=False).subclip(0, self.script.getDuration())
        w, h = backgroundVideo.size

        print(f" Background Video Resolution: {w} x {h}")

        # Renders Video
        # A function within a class
        # This method is called below
        def __createClip(screenShotFile, audioClip, marginSize, audioClipDuration: float) -> ImageClip:
            # save each audio clip file name
            # save each audio clip duration using Wave method
            print(f" Script Debug : {self.script}")  # for debug purposes only

            imageClip : ImageClip = ImageClip(
                screenShotFile,
                duration=audioClipDuration
            ).set_position(("center", "center"))
            imageClip = imageClip.resize(width=(w-marginSize))
            videoClip = imageClip.set_audio(audioClip)
            videoClip.fps = 1
            return videoClip

        def float2int(x) -> int:
            #COnverts a float to int else returns an int

            #print(type(x))
            if x is float:
                return int(math.ceil(x))
            if x is int:
                return x

        # Create video clips
        print("Editing clips together...")

        print(
            f"Title Duration debug 1: {float2int(self.script.titleAudioDuration)}")

        print(
            f"Title Duration debug 2: {self.script.titleAudioDuration}")
        # Holds all Generated CLips
        clips = []
        marginSize = int(self.config["Video"]["MarginSize"])

        """
            Title Screen
         
        These code blocs access sub classes variables
        Variables used below are : screenShotFile, audioClip, marginSize, audioClipDuration: float
        
        Bug: 
        
            (1) titleAudioDuration is a none (fixed).
                -with a Longer Max Comment Constant
            (2) Renders at a fixed 24 FPS for optimized performance
        """


        clips.append(
            __createClip(
                self.script.titleSCFile,
                self.script.titleAudioClip,
                marginSize,
                self.script.titleAudioDuration
            ))

        # print(f"Title Audio Duration debug 2: {script.titleAudioDuration}")

        print("Handling Comments")

        # Comments
        # These code blocs access sub classes vaariables
        # referencees the franes sub list in VideoScript Class
        for comment in self.script.frames:
            print(
                f"Comments Audio Duration debug: {comment.audioClipDuration}")

            clips.append(
                __createClip(
                    comment.screenShotFile,
                    comment.audioClip,
                    marginSize,
                    comment.audioClipDuration

                ))

        print("Adding Tag")

        clips.append(
                __createClip(
                    self.script.TagscreenShotFile,
                    self.script.WaterTag,
                    marginSize,
                    self.script.TagDuration
                ))

        # Merge clips into single track
        # Sets screenshot position on Clip
        # "center", "center" - FOr center Position
        # "center", "top" - For Top Position
        # Documentation : https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html?highlight=set_position#moviepy.video.VideoClip.ImageClip.set_position
        contentOverlay = concatenate_videoclips(
            clips).set_position(lambda t: ('center', 1050))

        # Compose background/foreground
        final = CompositeVideoClip(
            clips=[backgroundVideo, contentOverlay],
            size=backgroundVideo.size).set_audio(contentOverlay.audio)
        final.duration = self.script.getDuration()
        final.set_fps(backgroundVideo.fps)

        # Display Video Render Size Features
        self.w = final.w
        self.h = final.h

        # Resize Video Render Size
        final = final.resize(float(self.config["Video"]["Quality"]))

        print(
            f" Videofile Resolution reduced from {self.w} x {self.h} to {final.w} x {final.h}")

        # Write output to file
        print("Rendering final video...")
        bitrate = self.config["Video"]["Bitrate"]
        threads = self.config["Video"]["Threads"]
        outputFile = f"{self.outputDir}/{fileName}.mp4"

        # Render Video

        final.write_videofile(
            outputFile,
            codec='mpeg4',
            threads=threads,
            bitrate=bitrate,
            fps=24
        )

        # system(call)

        print(f"Video completed in {time.time() - self.startTime}")

        # VLC
        # Preview in VLC for approval before uploading
        # if (config["General"].getboolean("PreviewBeforeUpload")):
        #    vlcPath = config["General"]["VLCPath"]
        #    p = subprocess.Popen([vlcPath, outputFile])-
        #    print("Waiting for video review. Type anything to continue")
        #    wait = input()
        call = f"vlc {outputFile}"
        print(call)

        system(call)

        print("Video is ready to upload!")
        print(f"Title: {self.script.title}  File: {outputFile}")
        endTime = time.time()
        print(f"Total time: {endTime - self.startTime}")

        # Python Preview
        # final.ipython_display(width=self.w)

