#!/bin/python
#This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#           (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#                  but WITHOUT ANY WARRANTY; without even the implied warranty of
#                     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#                        GNU General Public License for more details.
#
#                               You should have received a copy of the GNU General Public License
#                                  along with this program.  If not, see <https://www.gnu.org/licenses/>.



import discord
from discord.ext import commands
from random import choice
import string
from discord.ext.commands.cooldowns import BucketType
import asyncio
import youtube_dl
import pafy
import datetime
from discord_slash import cog_ext, SlashContext
x = datetime.datetime.now()
from ult import *
class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0: return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5


    @commands.command()
    async def pause(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            ctx.voice_client.pause()
            await ctx.send("*Paused -* ⏸️")

    @commands.command()
    async def resume(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            ctx.voice_client.resume()
            await ctx.send("*Resuming -* ▶️")
    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def oskip(self, ctx):
                commandd = "oskip"
                print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
                print(x)
                print(" ")
                await ctx.send("skipping")
                ctx.voice_client.stop()
                await self.check_queue(ctx)
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def join(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            commandd = "join"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            if ctx.author.voice is None:
                return await ctx.send("You are not connected to a voice channel, please connect to the channel you want the bot to join.")

            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()

            await ctx.author.voice.channel.connect()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leave(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            commandd = "leave"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            if ctx.voice_client is not None:
                return await ctx.voice_client.disconnect()

            await ctx.send("I am not connected to a voice channel.")

    @commands.command()
    async def play(self, ctx, *, song=None):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            commandd = "play"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            if song is None:
                return await ctx.send("You must include a song to play.")

            if ctx.voice_client is None:
                return await ctx.send("I must be in a voice channel to play a song.")

            # handle song where song isn't url
            if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
                await ctx.send("Searching for song, this may take a few seconds.")

                result = await self.search_song(1, song, get_url=True)

                if result is None:
                    return await ctx.send("Sorry, I could not find the given song, try using my search command.")

                song = result[0]

            if ctx.voice_client.source is not None:
                queue_len = len(self.song_queue[ctx.guild.id])

                if queue_len < 10:
                    self.song_queue[ctx.guild.id].append(song)
                    return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {queue_len+1}.")

                else:
                    return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")

            await self.play_song(ctx, song)
            await ctx.send(f"Now playing: {song}")
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *, song=None):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            commandd = "search"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            if song is None: return await ctx.send("You forgot to include a song to search for.")

            await ctx.send("Searching for song, this may take a few seconds.")

            info = await self.search_song(5, song)

            embed = discord.Embed(title=f"Results for '{song}':", description="*You can use these URL's to play an exact song if the one you want isn't the first result.*\n", colour=discord.Color.green())

            amount = 0
            for entry in info["entries"]:
                embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
                amount += 1

            embed.set_footer(text=f"Displaying the first {amount} results.")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else: # display the current guilds queue
            commandd = "queue"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            if len(self.song_queue[ctx.guild.id]) == 0:
                return await ctx.send("There are currently no songs in the queue.")

            embed = discord.Embed(title="Song Queue", description="", colour=discord.Color.green().dark_gold())
            i = 1
            for url in self.song_queue[ctx.guild.id]:
                embed.description += f"{i}) {url}\n"

                i += 1

            embed.set_footer(text="Thanks for using me!")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def adskip(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            commandd = "adskip"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            await ctx.send("skipping")
            ctx.voice_client.stop()
            await self.check_queue(ctx)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skip(self, ctx):
        if await get_mute(ctx.author) != 0:
            await ctx.send("You are blacklisted from the bot")
        else:
            commandd = "skip"
            print(f"{ctx.author.name}, {ctx.author.id} used command "+commandd+" used at ")
            print(x)
            print(" ")
            if ctx.voice_client is None:
                return await ctx.send("I am not playing any song.")

            if ctx.author.voice is None:
                return await ctx.send("You are not connected to any voice channel.")

            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                return await ctx.send("I am not currently playing any songs for you.")

            poll = discord.Embed(title=f"Vote to Skip Song by - {ctx.author.name}#{ctx.author.discriminator}", description="**80% of the voice channel must vote to skip for it to pass.**", colour=discord.Color.blue())
            poll.add_field(name="Skip", value=":white_check_mark:")
            poll.add_field(name="Stay", value=":no_entry_sign:")
            poll.set_footer(text="Voting ends in 15 seconds.")

            poll_msg = await ctx.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions
            poll_id = poll_msg.id

            await poll_msg.add_reaction(u"\u2705") # yes
            await poll_msg.add_reaction(u"\U0001F6AB") # no

            await asyncio.sleep(15) # 15 seconds to vote

            poll_msg = await ctx.channel.fetch_message(poll_id)

            votes = {u"\u2705": 0, u"\U0001F6AB": 0}
            reacted = []

            for reaction in poll_msg.reactions:
                if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                    async for user in reaction.users():
                        if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                            votes[reaction.emoji] += 1

                            reacted.append(user.id)

            skip = False

            if votes[u"\u2705"] > 0:
                if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.79: # 80% or higher
                    skip = True
                    embed = discord.Embed(title="Skip Successful", description="***Voting to skip the current song was succesful, skipping now.***", colour=discord.Color.green())

            if not skip:
                embed = discord.Embed(title="Skip Failed", description="*Voting to skip the current song has failed.*\n\n**Voting failed, the vote requires at least 80% of the members to skip.**", colour=discord.Color.red())

            embed.set_footer(text="Voting has ended.")

            await poll_msg.clear_reactions()
            await poll_msg.edit(embed=embed)

            if skip:
                ctx.voice_client.stop()
                await self.check_queue(ctx)




def setup(bot):
    bot.add_cog(music(bot))
