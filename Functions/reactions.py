import discord

emotes = [":Upvote:523277460624769025", ":Downvote:523277460637351951"]


async def upvote_downvote_reactions(channel, message):
    try:
        for x in emotes:
            await message.add_reaction(x)
    except discord.Forbidden:
        return await channel.send(
            "It appears that I cannot add reactions to the above message. Please correct this."
        )
