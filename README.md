# Reddit Video Generator

This project is further explained in [this video](https://youtu.be/ZmSb3LZDdf0)

This program generates a .mp4 video automatically by querying the top post on the
r/askreddit subreddit, and grabbing several comments. The workflow of this program is:

- Install dependencies from requirements.txt (up to 3 gb)
- Make a copy of config.example.ini and rename to config.ini
- Register with Reddit to create an application [here](https://www.reddit.com/prefs/apps/) and copy the credentials
- Use the credentials from the previous step to update config.ini (lines 22 -> 24)

Now, you can run `python main.py` to be prompted for which post to choose. Alternatively,
you can run `python main.py <reddit-post-id>` to create a video for a specific post.

# Coqui TTS

Coqui TTS use example : tts --text "Hello world, this is Coqui TTS running offline!" --model_name tts_models/en/ljspeech/tacotron2-DDC --out_path hello.wav
