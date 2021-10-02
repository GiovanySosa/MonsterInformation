import discord
from discord.ext import commands
from mcpe_query.query import Query
import os
from dotenv import load_dotenv
import asyncio
from mcstats import mcstats
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='.', help_command=None)


@bot.command(description='Add a suggestion for this community!')
async def suggest(ctx, *, suggestion):
    await ctx.channel.purge(limit=1)
    channel = discord.utils.get(ctx.guild.text_channels, name='sugerencias')
    message = ctx.message

    suggestEmbed = discord.Embed(colour=0xFF0000)
    suggestEmbed.set_author(name=f'Sugerido por {ctx.message.author}', icon_url=f'{ctx.author.avatar_url}')
    suggestEmbed.add_field(name='Nueva sugertencia!', value=f'{suggestion}')


    msg = await channel.send(embed=suggestEmbed)
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    await message.delete()


@bot.command(name="help", description="ve la lista de comandos")
async def help(ctx):
    embed = discord.Embed(title="comandos disponible [ . ]", description=f"`lista de todos los comandos`",
                          color=discord.Color.blue())

    embed.set_footer(text=f"requerido por {ctx.author}", icon_url=ctx.author.avatar_url)

    embed.add_field(name='administracion', value='`say`, `anuncio`,`user`,`status`,`tempmute`,`lff`')

    embed.add_field(name='moderacion', value='`mute` ,`unmute` , `tempmute`, `kick`, `ban`')


    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    game = discord.Game('Minecraft')
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print('Bot cargado')

    
@bot.command()
async def status(ctx,):
    host = "youripdomain"
    port = 19132
    q = Query(host, port)
    data = q.query()
    
    a= "mc.monsternetwork.club"
    b= 19132

    online = data.num_players
    max = data.max_players
    jugadores = str(data.players)
    
    
    channel = discord.utils.get(ctx.guild.text_channels, name='⌨｜comandos')

    embed = discord.Embed(title="MonsterNetwork", description=f"**IP:** {a} **PUERTO:** {b}",color=discord.Color.random())
    
    embed.add_field(name="KitMap:", value=f"**ACTIVOS:** {online} **de** {max} \n \n **JUGADORES:** {jugadores[0:900]}", inline=False)
    
    embed.add_field(name="**invita a tus amigos**", value='[**TOCA AQUI PARA INVITAR**](https://discord.com/invite/MonsterHCF)')
    
    embed.set_footer(text=f" **juega y divierte te!!** ")

    await channel.send(embed=embed)
    await ctx.send(f"checa el canal de comandos")
    print(jugadores)


@bot.command(name="user",
             help="Mira la informacion de un miembro",
             brief="[Mira la informacion de un miembro]")
async def some_function_random_ctx(ctx, member: discord.Member):
    try:
        user_info_embed = discord.Embed(colour=0xff00ff).set_author(
            name=f"{member}", icon_url=member.avatar_url)
        user_info_embed.add_field(name=f"Entro a el servidor {ctx.guild}",
                                  value=member.joined_at)
        user_info_embed.add_field(name="Rol mas alto", value=member.top_role)
        user_info_embed.add_field(name="Creo su cuenta de discord",
                                  value=member.created_at)
        user_info_embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=user_info_embed)
    except:
        await ctx.send("Una excepcion ocurrio...")
    finally:
        await ctx.send(
            "informacion obtenida con exito, si no es asi, puede que haya ocurrido un error."
        )



@bot.command(name="kick", alieses="kickea a un usuario del servidor", brief="[expulsar a un miembro del servidor]")
async def kick(ctx, *, member: discord.Member, reason=None):
    if ctx.message.author.guild_permissions.administrator:
        await member.kick(reason=reason)
        await ctx.send(f'usuario {member} ha sido expulsado')


@bot.command(description="Desmutea a un usuario", brief="[comando para desmutear a un usuario muteado]")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await member.send(f" haz sido muteado por: - {ctx.guild.name}")
    embed = discord.Embed(title="desmuteado", description=f" desmuteado-{member.mention}",
                          colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)


@bot.command(description="Mutea a un miembro.", brief="[mutea a un usuario]")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True,
                                          read_messages=False)
    embed = discord.Embed(title="muteado", description=f"{member.mention} haz sido muteado",
                          colour=discord.Colour.light_gray())
    embed.add_field(name="razon:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" haz sido muteado por: {guild.name} razon: {reason}")


@bot.command(description="comando para mutear temporalmente", brief="[mutea temporalmente]")
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, time):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    tempmute = int(time[0]) * time_convert[time[-1]]
    await ctx.message.delete()
    await member.add_roles(muted_role)
    embed = discord.Embed(description=f"{member.display_name} haz sido muteado temporalmente por {time}",
                          color=discord.Color.green())
    await ctx.send(embed=embed, delete_after=60)
    await asyncio.sleep(tempmute)
    await member.remove_roles(muted_role)


@bot.command(name="ban", alieses="banea a un usuario del servidor", brief="[banear a un miembro del servidor]")
async def ban(ctx, *, member: discord.Member, reason=None):
    if ctx.message.author.guild_permissions.administrator:
        await member.ban(reason=reason)

        ban = discord.Embed(title="BANEADO", description=f" {member} ha sido baneado", colour=discord.Colour.blue())

        await ctx.send(embed=ban)

@bot.command(name='anuncio', alises=['anuncio'], brief="[comando solo para admins]")
async def anuncio(ctx, *, text):
    if ctx.message.author.guild_permissions.administrator:
        message = ctx.message
        embed = discord.Embed(title='  ', description=f"{text}", colour=discord.Colour.blue())
    await message.delete()
    await ctx.send(embed=embed)



@bot.command(name='say', alises=['say'], brief="[comando solo para admins]")
async def say(ctx, *, text):
    if ctx.message.author.guild_permissions.administrator:
        message = ctx.message
    await message.delete()
    await ctx.send(f"{text}")



@bot.command()
async def ip(ctx):
    a = "```❍━━━━❑❒❖❑❒━━━━❍❖❑❒━━━━❍ \n \n ip: mc.monsternetwork.club \n Port:19132 (DEFAULT) \n \n • Recuerda que puedes unirte por cualquiera de estas 2 ip \n ❍━━━━❑❒❖❑❒━━━━❍❖❑❒━━━━❍```"
    await ctx.send(a)

@bot.command()
async def tienda(ctx):
    tienda = discord.Embed(title="MonsterNetwork", description=f"**IP:** ip **PUERTO:** port",color=discord.Color.random())
    tienda.add_field(name="**¿QUIERES COMPRAR UN RANGO?**",value='[**TOCA AQUI PARA IR A LA TIENDA**](url)')
    await ctx.send(embed=tienda)
bot.run(TOKEN)
