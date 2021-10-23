from discord.ext import commands


class TooManyPrefixes(commands.UserInputError):
    pass


class PrefixTooLong(commands.BadArgument):
    pass


class PrefixNotFound(commands.BadArgument):
    pass


class DuplicatePrefix(commands.BadArgument):
    pass


class UsedOnSelf(commands.BadArgument):
    pass


class MissingArgument(commands.MissingRequiredArgument):
    pass


class TooManyUsers(commands.BadArgument):
    pass


class InvalidEndpoint():
    pass


class NSFWEndpoint:
    pass
