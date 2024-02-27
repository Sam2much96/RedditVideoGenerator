import os
import re
import praw
import markdown_to_text
import time
from videoscript import VideoScript
import configparser


#TO DO: Save TItle ID
# TO DO : refactor into classes


class Reddit:
    """
    Uses Praw + Reddit API to fetch reddit content as Json
    
    """
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Save User Preferred Config  
        self.CLIENT_ID = config["Reddit"]["CLIENT_ID"]
        self.CLIENT_SECRET = config["Reddit"]["CLIENT_SECRET"]
        self.USER_AGENT = config["Reddit"]["USER_AGENT"]
        self.SUBREDDIT = config["Reddit"]["SUBREDDIT"]

        # Pointer to Reddit class
        self.reddit_praw = self.__getReddit()


    def getContent(self,outputDir : str, postOptionCount : int) -> VideoScript:
        #reddit = self.
        existingPostIds = self.__getExistingPostIds(outputDir)

        now = int(time.time())
        autoSelect = postOptionCount == 0
        posts : list = []

        # for debug purposes only
        #print(posts) # for saving post id and comment id on new reddit ui

        # CUrates the Reddit / Sub Reddit Post
        for submission in self.reddit_praw.subreddit(self.SUBREDDIT).top(time_filter="day", limit=postOptionCount*3):
            if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
                continue
            hoursAgoPosted = (now - submission.created_utc) / 3600
            print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
            posts.append(submission)
            if (autoSelect or len(posts) >= postOptionCount):
                break

        "Collets User Input for Reddit Posts"
        if (autoSelect):
            return self.__getContentFromPost(posts[0])
        else:
            postSelection = int(input("Input: "))
            selectedPost = posts[postSelection]
            return self.__getContentFromPost(selectedPost)


    def getContentFromId(self, outputDir : str, submissionId) -> VideoScript:
        reddit = self.__getReddit()
        existingPostIds = self.__getExistingPostIds(outputDir)

        if (submissionId in existingPostIds):
            print("Video already exists!")
            exit()
        try:
            submission = reddit.submission(submissionId)
        except:
            print(f"Submission with id '{submissionId}' not found!")
            exit()
        return self.__getContentFromPost(submission)


    def __getReddit(self) : # Returns what?
        return praw.Reddit(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            user_agent=self.USER_AGENT
        )


    def __getContentFromPost(self,submission) -> VideoScript:
        """
        CREATES A VIDEOSCRIPT FROM A REDDIT POST
        returns the videoscript class as a return
        """

        # initialize videoscript class

        content: VideoScript = VideoScript(
            submission.url, submission.title,
            submission.id, "", None)

        print(f"Creating video for post: {submission.title}")
        print(f"Url: {submission.url}")
        # print (content)

        failedAttempts = 0
        # Error catchers

        for comment in submission.comments:
            # print(
            #    f" Comments: {markdown_to_text.markdown_to_text(comment.body), comment.id}")

            # Generates Voice Overs for each comment and Stores
            # Their info to Class variables for later use
            addContent: bool = content.addCommentScene(
                markdown_to_text.markdown_to_text(comment.body), comment.id)

            # Nested If's? Code Smell   
            if (addContent == True):
                failedAttempts += 1
                print(
                    f" failed attempts? {failedAttempts}/ add content {addContent}")

            if (content.canQuickFinish()) == True:
                print(22222)
                break
            if (failedAttempts > 3 and content.canBeFinished()):
                print(111111)
                break
            if (failedAttempts == 7):
                break

        # print(f"content debug: {content}")  # content debug
        return content


    def __getExistingPostIds(self,outputDir: str):
        files = os.listdir(outputDir)
        # I'm sure anyone knowledgeable on python hates this. I had some weird
        # issues and frankly didn't care to troubleshoot. It works though...
        # Regex :(
        files = [f for f in files if os.path.isfile(outputDir+'/'+f)]
        return [re.sub(r'.*?-', '', file) for file in files]
