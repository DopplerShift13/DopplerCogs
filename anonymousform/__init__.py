from .anonymousform import AnonymousForm

async def setup(bot):
    await bot.add_cog(AnonymousForm(bot))