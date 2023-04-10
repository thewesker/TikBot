import discord
import os
import ffmpeg
from dotenv import load_dotenv 
from downloader import download
from compressionMessages import getCompressionMessage
from validator import extractUrl, isSupportedUrl

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # Ignore our own messages
    if message.author == client.user:
        return

    fileName = ""
    duration = 0
    messages = ""

    # Do special things in DMs
    if(type(message.channel) is discord.DMChannel):
        if message.content.startswith('🎵'):
            url = message.content.replace('🎵', '')
            downloadResponse = download(url)
            fileName = downloadResponse['fileName']
            duration = downloadResponse['duration']
            messages = downloadResponse['messages']

            print("Downloaded: " + fileName + " For User: " + str(message.author))

            if(messages.startswith("Error")):
          ##      await message.author.send('TikBot has failed you. Consider berating my human if this was not expected.\nMessage: ' + messages)
                return

            audioFilename = "audio_" + fileName + ".mp3"
            ffmpeg.input(fileName).output(audioFilename, **{'b:a': '320k', 'threads': '1'}).run()
            with open(audioFilename, 'rb') as fp:
                await message.author.send(file=discord.File(fp, str(audioFilename)))
            # Delete the compressed and original file
            os.remove(fileName)
            os.remove(audioFilename)
        else:
            await message.author.send('👋')

        return

    # Only do anything in TikTok channels
  #  if(not message.channel.name.startswith("tik-tok")):
   #     return

    # Be polite!
  #  if message.content.startswith('$hello'):
   #     await message.channel.send('Hello!')

    # Extract and validate the request 
    extractResponse = extractUrl(message.content)
    url = extractResponse["url"]
    messages = extractResponse['messages']
    if(messages.startswith("Error")):
     ##   await message.channel.send('TikBot encountered an error determing a URL. Consider berating my human if this was not expected.\nMessage: ' + messages)
        return

  #  print("Got URL: " + url + " For User: " + str(message.author))
    if('🤖' not in message.content):
        # Validate unless we've been reqeuested not to
        validateResponse = isSupportedUrl(url)
        messages = validateResponse['messages']
        if(messages.startswith("Error")):
      ##      await message.channel.send('TikBot encountered an error validating the URL. Consider berating my human if this was not expected.\nMessage: ' + messages)
            return
        if(validateResponse['supported'] == 'false'):
            # Unsupported URL, return silently without doing anything
            return
    ARCHIVE_CHANNEL = int(os.getenv('ARCHIVE'))
    channel = client.get_channel(ARCHIVE_CHANNEL)
    sent_message = await message.channel.send("Downloading and processing video now. It will be available to view in " + str(channel.mention) + " soon. If it's a long video, the length may be shortened.")
    await sent_message.delete(delay=3)
    downloadResponse = download(url)
    fileName = downloadResponse['fileName']
    duration = downloadResponse['duration']
    messages = downloadResponse['messages']

    print("Downloaded: " + fileName + " For User: " + str(message.author))

    if(messages.startswith("Error")):
    ##    await message.channel.send('TikBot has failed you. Consider berating my human if this was not expected.\nMessage: ' + messages)
        return

    # Check file size, if it's small enough just send it!
    fileSize = os.stat(fileName).st_size
    message_author = str(message.author)
    vid_details = "Video posted by <@!" + str(message.author.id) + "> at " + str(message.created_at) + " in " + str(message.channel.mention) + " " + str(message.jump_url)
    if(fileSize < 8000000):
        with open(fileName, 'rb') as fp:
            print(vid_details)
            channel = client.get_channel(ARCHIVE_CHANNEL)
            video_archive_msg = await channel.send(vid_details, file=discord.File(fp, str(fileName)))
            vid_msg_id = await message.channel.send("Video archived: " + str(video_archive_msg.jump_url))
            await vid_msg_id.delete(delay=300)
        os.remove(fileName)

    else:
        # We need to compress the file below 8MB or discord will make a sad
      #  compressionMessage = getCompressionMessage()
    #    await channel.send(compressionMessage)
        print("Duration = " + str(duration))
        # Give us 7MB files with VBR encoding to allow for some overhead
        bitrateKilobits = 0
        if(duration != 0):
            bitrateKilobits = (7000 * 8)/duration
            bitrateKilobits = round(bitrateKilobits)
        else:
            bitrateKilobits = 800
        print("Calced bitrate = " + str(bitrateKilobits))
        ffmpeg.input(fileName).output("small_" + fileName, **{'b:v': str(bitrateKilobits) + 'k', 'b:a': '64k', 'fs': '8M', 'threads': '4'}).run()
        with open("small_" + fileName, 'rb') as fp:
            channel = client.get_channel(ARCHIVE_CHANNEL)
            print(vid_details)
            video_archive_msg = await channel.send(vid_details, file=discord.File(fp, str("small_" + fileName)))
            vid_msg_id = await message.channel.send("Video archived: " + str(video_archive_msg.jump_url))
            await vid_msg_id.delete(delay=60)
        # Delete the compressed and original file
        os.remove(fileName)
        os.remove("small_" + fileName)


client.run(os.getenv('TOKEN'))
