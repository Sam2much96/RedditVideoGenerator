from moviepy.editor import AudioFileClip, VideoClip
import reddit
import screenshot
from videoscript import  VoiceOver
import time
import subprocess
import random
import configparser
import sys
import math
from os import listdir
from os.path import isfile, join


def createVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if (len(sys.argv) == 2):

        # Creates a Video Script Class
        script = reddit.getContentFromId(outputDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])

        # Creates a Video Script Class
        script = reddit.getContent(outputDir, postOptionCount)
    fileName = script.getFileName()

    # Create screenshots
    screenshot.getPostScreenshots(fileName, script)

    # Setup background clip
    bgDir = config["General"]["BackgroundDirectory"]
    bgPrefix = config["General"]["BackgroundFilePrefix"]
    bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
    bgCount = len(bgFiles)
    bgIndex = random.randint(0, bgCount-1)
    backgroundVideo = VideoFileClip(
        filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4",
        audio=False).subclip(0, script.getDuration())
    w, h = backgroundVideo.size

    # Renders Video
    # This method is called below
    def __createClip(screenShotFile, audioClip, audioClipDuration : int, marginSize):
        # save each audio clip file name
        # save each audio clip duration using Wave method
        print ("fkjdgkndgkljkln") 

        imageClip = ImageClip(
            screenShotFile,
            duration= audioClipDuration
        ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip



    # Create video clips
    print("Editing clips together...")
    
    # Holds all Generated CLips
    clips = []
    marginSize = int(config["Video"]["MarginSize"])
    
    # Title Screen
    # These code blocs access sub classes variables

    clips.append(
        __createClip(
            script.titleSCFile,
            script.titleAudioClip,
             marginSize,
             script.titleAudioDuration
        ))
    
    print (f"Audio Duration debug: {script.titleAudioDuration}")

    # Comments
    # These code blocs access sub classes vaariables 
    # referencees the franes sub list in VideoScript Class
    for comment in script.frames:
        print (f"Audio Duration debug: {comment.audioClipDuration}")

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

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}.mp4"
    final.write_videofile(
        outputFile,
        codec='mpeg4',
        threads=threads,
        bitrate=bitrate
    )
    print(f"Video completed in {time.time() - startTime}")

    # VLC
    # Preview in VLC for approval before uploading
    if (config["General"].getboolean("PreviewBeforeUpload")):
        vlcPath = config["General"]["VLCPath"]
        p = subprocess.Popen([vlcPath, outputFile])
        print("Waiting for video review. Type anything to continue")
        wait = input()

    print("Video is ready to upload!")
    print(f"Title: {script.title}  File: {outputFile}")
    endTime = time.time()
    print(f"Total time: {endTime - startTime}")


if __name__ == "__main__":


   createVideo()

   # "Main Code"
   # try:
   #     createVideo()
   # except:
        # handle any other type of exception
   #     print("Error: something went wrong")
