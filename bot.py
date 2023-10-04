#Modules (pip3 install discord.py)(pip3 install asyncio)(pip3 install flask_discord)
import discord
from discord.ext import commands
import asyncio


#Variables
intents = discord.Intents.default()
bot=commands.Bot(command_prefix='!!',intents=intents)
AUTHTOKEN=""
bot.msgbackup=[]
bot.updatelist=[]

#Starting the bot
@bot.event
async def on_ready():
    print("Bot is now online, please type !!start to begin the bot(only do this once)")

#Force Invite
from flask_discord import DiscordOAuth2Session

discord = DiscordOAuth2Session()

def get_app():
    app = Flask(__name__)

    app.secret_key = b"random bytes representing flask secret key"
    # OAuth2 must make use of HTTPS in production environment.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.
    app.config["DISCORD_CLIENT_ID"] =  ""   # Discord client ID.
    app.config["DISCORD_CLIENT_SECRET"] = ""                # Discord client secret.
    app.config["DISCORD_REDIRECT_URI"] = ""                 # URL to your callback endpoint.
    app.config["DISCORD_BOT_TOKEN"] = ""                    # Required to access BOT resources.

    discord.init_app(app)

    return app

#Checking for update messages
@bot.event
async def on_message(message):
    if message.author==bot.user:
        return
    await bot.process_commands(message)
    if message.channel.id == bot.updatechannel.id:
        for server in bot.updatelist:
            embed = discord.Embed(title=message.author.name + '#' + message.author.discriminator,description=str(message.created_at), color=0x00ff00)
            embed.add_field(name="Message:", value=message.content, inline=False)
            embed.add_field(name="Channel", value="#" + message.channel.name, inline=False)
            embed.add_field(name="URL:", value=message.jump_url, inline=False)
            await server.send(embed=embed)



#Beginning setup
@bot.command()
async def setup(ctx,guildid):
    #Old Guild Data

    bot.guild=bot.get_guild(int(guildid))
    bot.emojilist = bot.guild.emojis
    bot.members = bot.guild.members
    bot.roles = bot.guild.roles
    bot.tchannels = bot.guild.text_channels
    bot.vchannels = bot.guild.voice_channels
    for channel in bot.tchannels:
        async for message in channel.history(oldest_first=True):
            embed = discord.Embed(title=message.author.display_name+"#"+message.author.discriminator, description=str(message.created_at),color=0x00ff00)
            embed.add_field(name="Message:", value=message.content, inline=False)
            embed.add_field(name="Channel", value="#" + channel.name, inline=False)
            embed.add_field(name="URL:", value=message.jump_url, inline=False)
            for msg in bot.msgbackup:
                if msg not in bot.msgbackup:
                    bot.msgbackup.append(embed)
    #Setting up backups
    bot.backupchannel = await ctx.guild.create_text_channel('backups-bot')
    for member in ctx.guild.members:
        if member != bot.user:
            await bot.backupchannel.set_permissions(member, read_messages=True, send_messages=False)
    await ctx.send("Began setting up")
    await ctx.send("Began octohourly backups")
    #Auto Backups
    while True:
        # Server Backup
        bot.guild = bot.get_guild(int(guildid))
        bot.emojilist = bot.guild.emojis
        bot.members = bot.guild.members
        bot.roles = bot.guild.roles
        bot.tchannels = bot.guild.text_channels
        bot.vchannels = bot.guild.voice_channels
        for channel in bot.tchannels:
            async for message in channel.history(oldest_first=True):
                embed = discord.Embed(title=message.author.display_name, description=str(message.created_at),
                                      color=0x00ff00)
                embed.add_field(name="Message:", value=message.content, inline=False)
                embed.add_field(name="Channel", value="#" + channel.name, inline=False)
                embed.add_field(name="URL:", value=message.jump_url, inline=False)
                if embed not in bot.msgbackup:
                    bot.msgbackup.append(embed)
        await asyncio.sleep(28800)

#Manual Backup
@bot.command()
async def backup(ctx):
    bot.emojilist = bot.guild.emojis
    bot.members = bot.guild.members
    bot.roles = bot.guild.roles
    bot.tchannels = bot.guild.text_channels
    bot.vchannels = bot.guild.voice_channels
    for channel in bot.tchannels:
        async for message in channel.history(oldest_first=True):
            embed = discord.Embed(title=message.author.display_name, description=str(message.created_at),color=0x00ff00)
            embed.add_field(name="Message:", value=message.content, inline=False)
            embed.add_field(name="Channel", value="#" + channel.name, inline=False)
            embed.add_field(name="URL:", value=message.jump_url, inline=False)
            if embed not in bot.msgbackup:
                bot.msgbackup.append(embed)
    await ctx.channel.send('backedup!')


#Add a beta update channel
@bot.command()
async def updateadd(ctx,channelid):
    bot.updatelist.append(bot.get_channel(int(channelid)))
    await ctx.send(f"added beta channel: #{bot.get_channel(int(channelid)).name} to update list")

#Add a source channel
@bot.command()
async def updateset(ctx,updateid):
    bot.updatechannel=bot.get_channel(int(updateid))
    await ctx.send(f"Set source channel to: #{bot.updatechannel.name} to update list")


#Replicate old server
@bot.command()
async def replicate(ctx):
    await ctx.send("Began Replicating!")
    for role in bot.roles:
        if role.name=="@everyone":
            continue
        roletemp = await ctx.guild.create_role(name=role.name, permissions=role.permissions, colour=role.colour,hoist=role.hoist, mentionable=role.mentionable)

    for tchannel in bot.tchannels:
        tchanneltemp = await ctx.guild.create_text_channel(tchannel.name, overwrites=tchannel.overwrites,
                                                           slowmode_delay=tchannel.slowmode_delay, nsfw=tchannel.nsfw)
        for member in bot.members:
            perms = tchannel.permissions_for(member)
            # await tchanneltemp.set_permissions(member, overwrite=tchannel.overwrites, permissions=perms)
    for vchannel in bot.vchannels:
        vchanneltemp = await ctx.guild.create_voice_channel(vchannel.name, overwrites=vchannel.overwrites)
        for member in bot.members:
            perms = vchannel.permissions_for(member)
            # await vchanneltemp.set_permissions(member, perms)
    for member in bot.members:
        app.put(f"https://discord.com/api/guilds/{ctx.guild.id}/members/{member.id}")
    for msg in bot.msgbackup:
        try:
            await bot.backupchannel.send(embed=msg)
        except:
            pass
        print(msg)



bot.run(AUTHTOKEN)