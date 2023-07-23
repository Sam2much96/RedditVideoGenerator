from moviepy.editor import *
import reddit
import screenshot
from videoscript import VoiceOver
import time
import subprocess
import random
import configparser
import sys
import math
from os import listdir
from os.path import isfile, join


class Render:

    def __init__(self):
        # Create Debug Variables for video file
        # (!) Final Clip Size : Vector2

        # Final Video Size
        self.w: int = 0
        self.h: int = 0

        # Load User Config Files
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.outputDir = self.config["General"]["OutputDirectory"]

        self.startTime = time.time()

    def createVideo(self):

        # Get script from reddit
        # If a post id is listed, use that. Otherwise query top posts
        if (len(sys.argv) == 2):

            # Creates a Video Script Class
            script = reddit.getContentFromId(self.outputDir, sys.argv[1])
        else:
            postOptionCount = int(
                self.config["Reddit"]["NumberOfPostsToSelectFrom"])

            # Creates a Video Script Class
            script = reddit.getContent(self.outputDir, postOptionCount)
        fileName = script.getFileName()

        # Create screenshots
        screenshot.getPostScreenshots(fileName, script)

        # Setup background clip
        bgDir = self.config["General"]["BackgroundDirectory"]
        bgPrefix = self.config["General"]["BackgroundFilePrefix"]
        bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
        bgCount = len(bgFiles)

        # Selects a randomized Background Clip Number
        bgIndex = random.randint(0, bgCount-1)
        backgroundVideo = VideoFileClip(
            filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4",
            audio=False).subclip(0, script.getDuration())
        w, h = backgroundVideo.size

        print(f" Background Video Resolution: {w} x {h}")

        # Renders Video
        # A function within a class
        # This method is called below
        def __createClip(screenShotFile, audioClip, marginSize, audioClipDuration: float):
            # save each audio clip file name
            # save each audio clip duration using Wave method
            print(f" Script Debug : {script}")  # for debug purposes only

            imageClip = ImageClip(
                screenShotFile,
                duration=audioClipDuration
            ).set_position(("center", "center"))
            imageClip = imageClip.resize(width=(w-marginSize))
            videoClip = imageClip.set_audio(audioClip)
            videoClip.fps = 1
            return videoClip

        def float2int(x) -> int:
            # COnverts a float to int else returns an int

            print(type(x))
            if x is float:
                return int(math.ceil(x))
            if x is int:
                return x

        # Create video clips
        print("Editing clips together...")

        print(
            f"Title Duration debug 1: {float2int(script.titleAudioDuration)}")

        print(
            f"Title Duration debug 2: {script.titleAudioDuration}")
        # Holds all Generated CLips
        clips = []
        marginSize = int(self.config["Video"]["MarginSize"])

        # Title Screen
        # These code blocs access sub classes variables
        #  Variables used below are : screenShotFile, audioClip, marginSize, audioClipDuration: float
        # Bug: titleAudioDuration is a none

        clips.append(
            __createClip(
                script.titleSCFile,
                script.titleAudioClip,
                marginSize,
                script.titleAudioDuration
            ))

        # print(f"Title Audio Duration debug 2: {script.titleAudioDuration}")

        print("Handling Comments")

        # Comments
        # These code blocs access sub classes vaariables
        # referencees the franes sub list in VideoScript Class
        for comment in script.frames:
            print(
                f"Comments Audio Duration debug: {comment.audioClipDuration}")

            clips.append(
                __createClip(
                    comment.screenShotFile,
                    comment.audioClip,
                    marginSize,
                    comment.audioClipDuration

                ))

        # Merge clips into single track
        contentOverlay = concatenate_videoclips(
            clips).set_position(("center", "center"))

        # Compose background/foreground
        final = CompositeVideoClip(
            clips=[backgroundVideo, contentOverlay],
            size=backgroundVideo.size).set_audio(contentOverlay.audio)
        final.duration = script.getDuration()
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
        final.write_videofile(
            outputFile,
            codec='mpeg4',
            threads=threads,
            bitrate=bitrate
        )
        print(f"Video completed in {time.time() - self.startTime}")

        # VLC
        # Preview in VLC for approval before uploading
        # if (config["General"].getboolean("PreviewBeforeUpload")):
        #    vlcPath = config["General"]["VLCPath"]
        #    p = subprocess.Popen([vlcPath, outputFile])
        #    print("Waiting for video review. Type anything to continue")
        #    wait = input()

        print("Video is ready to upload!")
        print(f"Title: {script.title}  File: {outputFile}")
        endTime = time.time()
        print(f"Total time: {endTime - self.startTime}")

        # Python Preview
        outputFile.ipython_display(width=self.w)


if __name__ == "__main__":

    render = Render()
    render.createVideo()

    "Main Code Loop"
    # try:
    #    render.createVideo()
    # except:
    #    # handle any other type of exception
    #    print("Error: something went wrong")
