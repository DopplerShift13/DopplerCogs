from .anonymousform import AnonymousForm

async def setup(bot):
    cog = AnonymousForm(bot)
    await bot.add_cog(cog)
    await bot.tree.sync()