# Video Archive Discord Bot
 A super simple Discord bot designed for helping you archive videos posted to your channels.
 
 Video Archive Discord Bot will download any video from YouTube, Instagram, Tik Tok, and Reddit linked in a Discord channel it is in, and post the video file directly in a designated archive channel. 
 In cases where the file is too large for Discord's free tier, the video will be compressed to fit first.
 
 # Installation & Usage
 Requirements: Python 3.10
 
 1. Set Discord access token in ```.env``` as ```TOKEN=$yourTokenGoesHere```
 
 2. Make a video archive channel in your discord server.
 
 3. Set Archive channel ID in ```.env``` as ```ARCHIVE=$yourChannelIDGoesHere```. You can get this ID by right clicking on the channel and clicking "Copy ID".
 
 4. Add the bot to the Discord server you wish to run it in.
  
 5. Ensure the bot has permission to post attachments and messages in the channel.
 
 6. Install required packages with ```pip install -r requirements.txt ```
 
 7. Run the bot ```python main.py```
 
 # Notes
 Not recommended to be available as a public bot due to the bandwidth and processing requirements of downloading and encoding videos.
