import discord
import ts3
import os

# Discord botunuzun token'ını buraya girin
DISCORD_TOKEN = 'discord_bot_token'

# Teamspeak 3 bilgileri
TS3_SERVER_IP = 'ts3_server_ip'
TS3_USERNAME = 'bot_username'
TS3_PASSWORD = 'bot_password'
TARGET_CHANNEL_ID = 12345  # Kayıt yapılacak kanalın ID'si

# Kayıtların kaydedileceği klasör yolu
SAVE_FOLDER = '/path/to/save/folder'

# Teamspeak 3 bağlantısını oluştur
ts3conn = ts3.query.TS3Server(TS3_SERVER_IP)

# Discord botunu başlat
client = discord.Client()

@client.event
async def on_ready():
    print('Discord botu çalışıyor.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!kayit_baslat'):
        # Teamspeak 3'e bağlan
        ts3conn.connect()
        ts3conn.login(client_login_name=TS3_USERNAME, client_login_password=TS3_PASSWORD)

        # İki adet client oluştur
        client1 = ts3conn.clientcreate(client_nickname='BotClient1')
        client2 = ts3conn.clientcreate(client_nickname='BotClient2')

        # İki client'ı hedef kanala taşı
        ts3conn.clientmove(clientid=client1['clid'], cid=TARGET_CHANNEL_ID)
        ts3conn.clientmove(clientid=client2['clid'], cid=TARGET_CHANNEL_ID)

        # Multitrack kayıt özelliğini aç
        ts3conn.clientupdate(client_id=client1['clid'], client_input_hardware=True)
        ts3conn.clientupdate(client_id=client2['clid'], client_input_hardware=True)

        await message.channel.send('Ses kaydı başlatıldı.')

    elif message.content.startswith('!kayit_durdur'):
        # Multitrack kayıt özelliğini kapat
        ts3conn.clientupdate(client_id=client1['clid'], client_input_hardware=False)
        ts3conn.clientupdate(client_id=client2['clid'], client_input_hardware=False)

        # Teamspeak 3 bağlantısını kapat
        ts3conn.logout()

        await message.channel.send('Ses kaydı durduruldu.')

        # Kaydedilen ses kayıtlarını masaüstüne taşı
        client1_recording_path = client1['client_unique_identifier'] + '.wav'
        client2_recording_path = client2['client_unique_identifier'] + '.wav'
        
        os.rename(client1_recording_path, os.path.join(SAVE_FOLDER, client1_recording_path))
        os.rename(client2_recording_path, os.path.join(SAVE_FOLDER, client2_recording_path))

    elif message.content.startswith('!odalar'):
        # Teamspeak 3'e bağlan
        ts3conn.connect()
        ts3conn.login(client_login_name=TS3_USERNAME, client_login_password=TS3_PASSWORD)

        # Teamspeak 3 sunucusundaki tüm odaları al
        response = ts3conn.send_command('channellist')

        # Odaları ve içerisindeki kullanıcıları bul
        channel_users = {}
        for channel in response.data:
            channel_id = channel['cid']
            channel_name = channel['channel_name']

            # Oda içerisindeki kullanıcıları al
            response = ts3conn.send_command(f'channelclientlist cid={channel_id}')
            users = [client['client_nickname'] for client in response.data]
            channel_users[channel_name] = users

        # Teamspeak 3 bağlantısını kapat
        ts3conn.logout()

        # Bulunan odaları ve kullanıcıları Discord'a gönder
        response_message = "Teamspeak 3 Odaları ve Kullanıcıları:\n"
        for channel, users in channel_users.items():
            response_message += f"{channel}: {', '.join(users)}\n"

        await message.channel.send(response_message)

    elif message.content.startswith('!komut'):
        # Komutları al
        commands = [
            '!kayit_baslat - Teamspeak 3 ses kaydını başlatır.',
            '!kayit_durdur - Teamspeak 3 ses kaydını durdurur.',
            '!odalar - Teamspeak 3 odalarını ve kullanıcıları gösterir.',
            '!komut - Bot üzerinde çalışan tüm komutları gösterir.'
        ]

        # Komutları Discord'a gönder
        response_message = "Bot üzerinde çalışan komutlar:\n"
        response_message += '\n'.join(commands)
        await message.channel.send(response_message)

client.run(DISCORD_TOKEN)
