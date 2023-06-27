import discord
import ts3
import os

# Discord bot token
DISCORD_TOKEN = 'discord_bot_token'

# Teamspeak 3 information
TS3_SERVER_IP = 'ts3_server_ip'
TS3_USERNAME = 'bot_username'
TS3_PASSWORD = 'bot_password'
TARGET_CHANNEL_ID = 12345  # ID of the Teamspeak 3 channel that the bot will record audio from

# Folder where recordings will be saved
SAVE_FOLDER = '/path/to/save/folder'

# Create a Teamspeak 3 connection
ts3conn = ts3.query.TS3Server(TS3_SERVER_IP)

# Create a Discord client
client = discord.Client()

@client.event
async def on_ready():
    print('Discord bot is ready.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!start_record'):
        # Start recording audio in Teamspeak 3
        ts3conn.clientupdate(client_id=client['clid'], client_input_hardware=True)

        await message.channel.send('Ses kaydı başlatıldı.')

    elif message.content.startswith('!stop_record'):
        # Stop recording audio in Teamspeak 3
        ts3conn.clientupdate(client_id=client['clid'], client_input_hardware=False)

        await message.channel.send('Ses kaydı durduruldu.')

        # Save the recording
        recording_path = client['client_unique_identifier'] + '.wav'
        os.rename(recording_path, os.path.join(SAVE_FOLDER, recording_path))

    elif message.content.startswith('!list_channels'):
        # List the Teamspeak 3 channels and users
        response = ts3conn.send_command('channellist')

        channel_users = {}
        for channel in response.data:
            channel_id = channel['cid']
            channel_name = channel['channel_name']

            # List the users in the channel
            response = ts3conn.send_command(f'channelclientlist cid={channel_id}')
            users = [client['client_nickname'] for client in response.data]
            channel_users[channel_name] = users

        # Send the list of channels and users to Discord
        response_message = "Teamspeak 3 Odaları ve Kullanıcıları:\n"
        for channel, users in channel_users.items():
            response_message += f"{channel}: {', '.join(users)}\n"

        await message.channel.send(response_message)

    elif message.content.startswith('!help'):
        # List all available commands
        commands = [
            '!start_record - Starts recording audio in Teamspeak 3.',
            '!stop_record - Stops recording audio in Teamspeak 3.',
            '!list_channels - Displays the Teamspeak 3 channels and users.',
            '!help - Shows all available commands for the bot.'
        ]

        # Send the list of commands to Discord
        response_message = "Bot üzerinde çalışan komutlar:\n"
        response_message += '\n'.join(commands)
        await message.channel.send(response_message)

client.run(DISCORD_TOKEN)