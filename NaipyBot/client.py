# Discord 라이브러리
import discord
from discord import Intents
from discord.ext import commands
from discord import app_commands
from discord.ext.commands.context import Context
from discord.embeds import Embed

# 설정값은 여기서 가져옵니다. ex) 토큰 등등
from config import NaipyBotConfig

# Naipy 라이브러리
from naipy import model
from naipy.client import Search, Translation
from naipy.error import HTTPException


class naipy:
    search = Search()
    translation = Translation()


# 권한 설정
intents = Intents.default()
intents.message_content = True

# 접두사 설정
bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)

# 봇이 로그인 성공시 실행되는 이벤트
@bot.event
async def on_ready():
    print("로그인성공")
    bot.tree.copy_global_to(guild=discord.Object(id=1037635967831523388))
    await bot.tree.sync(guild=discord.Object(id=1037635967831523388))


# 이미지검색
@bot.command(name="이미지")
async def search(ctx: Context, word: str):
    data: model.ImageNaipy = await naipy.search.image(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(title=data.title)
    embed.set_image(url=data.link)
    return await ctx.reply(embed=embed)


# 블로그 검색
@bot.command(name="블로그")
async def blog(ctx: Context, word: str):
    data: model.BlogNaipy = await naipy.search.blog(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(
        title=data.title.replace("<b>", "**").replace("</b>", "**"),
        url=data.link,
        description=data.description.replace("<b>", "**").replace("</b>", "**"),
    )
    embed.set_author(name=data.bloggername, url="https://" + data.bloggerlink)
    return await ctx.reply(embed=embed)


# 도서 검색
@bot.command(name="도서")
async def book(ctx: Context, word: str):
    data: model.BookNaipy = await naipy.search.book(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(title=data.title, url=data.link)
    embed.set_image(url=data.image)
    embed.add_field(name=f"Author", value=f"`{data.author}`", inline=False)
    embed.add_field(name=f"Description", value=f"{data.description}", inline=False)
    embed.add_field(name=f"Price(할인가)", value=f"`{data.discount}원`", inline=False)
    embed.add_field(name=f"Publisher(출판사)", value=f"`{data.publisher}`", inline=False)
    return await ctx.reply(embed=embed)


# 백과사전 검색
@bot.command(name="백과사전")
async def encyc(ctx: Context, word: str):
    data: model.EncycNaipy = await naipy.search.encyc(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(
        title=data.title.replace("<b>", "**").replace("</b>", "**"), url=data.link
    )
    embed.set_image(url=data.thumbnail)
    embed.add_field(
        name=f"Description",
        value=f"{data.description.replace('<b>', '**').replace('</b>', '**')}",
        inline=False,
    )
    return await ctx.reply(embed=embed)


# 카페글 검색
@bot.command(name="카페글")
async def cafearticle(ctx: Context, word: str):
    data: model.CafearticleNaipy = await naipy.search.cafearticle(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(
        title=data.title.replace("<b>", "**").replace("</b>", "**"), url=data.link
    )
    embed.add_field(
        name=f"Description",
        value=f"{data.description.replace('<b>', '**').replace('</b>', '**')}",
        inline=False,
    )
    embed.add_field(
        name=f"Cafe", value=f"[{data.cafename}](<{data.cafeurl}>)", inline=False
    )
    return await ctx.reply(embed=embed)


# 지식인 검색
@bot.command(name="지식인")
async def kin(ctx: Context, word: str):
    data: model.KinNaipy = await naipy.search.kin(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(
        title=data.title.replace("<b>", "**").replace("</b>", "**"), url=data.link
    )
    embed.add_field(
        name=f"Description",
        value=f"{data.description.replace('<b>', '**').replace('</b>', '**')}",
        inline=False,
    )
    return await ctx.reply(embed=embed)


# 쇼핑 검색
@bot.command(name="쇼핑")
async def shop(ctx: Context, word: str):
    data: model.ShopNaipy = await naipy.search.shop(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(
        title=data.title.replace("<b>", "**").replace("</b>", "**"), url=data.link
    )
    if data.lprice == "":
        lprice = "없음"
    else:
        lprice = format(int(data.lprice), ",") + "원"
    if data.hprice == "":
        hprice = "없음"
    else:
        hprice = format(int(data.hprice), ",") + "원"
    embed.add_field(name=f"최저가", value=f"`{lprice}`", inline=False)
    embed.add_field(name=f"최고가", value=f"`{hprice}`", inline=False)
    embed.set_image(url=data.image)
    return await ctx.reply(embed=embed)


# 전문자료 검색
@bot.command(name="전문자료")
async def doc(ctx: Context, word: str):
    data: model.DocNaipy = await naipy.search.doc(word)  # Naipy 데이터 가져옴
    embed: Embed = Embed(
        title=data.title.replace("<b>", "**").replace("</b>", "**"), url=data.link
    )
    embed.add_field(
        name=f"Description",
        value=f"{data.description.replace('<b>', '**').replace('</b>', '**')}",
        inline=False,
    )
    return await ctx.reply(embed=embed)


# 언어인식
@bot.tree.context_menu(name="언어인식")
async def detects(interactions: discord.Interaction, word: discord.Message):
    try:
        data: model.DetectNaipy = await naipy.translation.detect(
            word.content
        )  # Naipy 데이터 가져옴
    except HTTPException:
        return await interactions.response.send_message(
            "지원하지 않는 메세지형식입니다.", ephemeral=True
        )
    embed: Embed = Embed()
    embed.add_field(name="입력한 글자", value=f"`{word.content}`", inline=False)
    embed.add_field(name="해당 글자의 언어", value=f"`{data.langCode}`", inline=False)
    return await interactions.response.send_message(embed=embed, ephemeral=True)

# 번역
@bot.tree.context_menu(name="한국어로 번역")
async def detects(interactions: discord.Interaction, word: discord.Message):
    try:
        data: model.N2mtNaipy = await naipy.translation.translation(
            word.content, "ko"
        )  # Naipy 데이터 가져옴
    except HTTPException:
        return await interactions.response.send_message(
            "지원하지 않는 메세지형식입니다.", ephemeral=True
        )
    embed: Embed = Embed()
    embed.add_field(
        name=f"{data.srcLangType} → {data.tarLangType}",
        value=f"`{word.content}` → `{data.translatedText}`",
    )
    return await interactions.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="영어로 번역")
async def detects(interactions: discord.Interaction, word: discord.Message):
    try:
        data: model.N2mtNaipy = await naipy.translation.translation(
            word.content, "en"
        )  # Naipy 데이터 가져옴
    except HTTPException:
        return await interactions.response.send_message(
            "지원하지 않는 메세지형식입니다.", ephemeral=True
        )
    embed: Embed = Embed()
    embed.add_field(
        name=f"{data.srcLangType} → {data.tarLangType}",
        value=f"`{word.content}` → `{data.translatedText}`",
    )
    return await interactions.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="일본어로 번역")
async def detects(interactions: discord.Interaction, word: discord.Message):
    try:
        data: model.N2mtNaipy = await naipy.translation.translation(
            word.content, "ja"
        )  # Naipy 데이터 가져옴
    except HTTPException:
        return await interactions.response.send_message(
            "지원하지 않는 메세지형식입니다.", ephemeral=True
        )
    embed: Embed = Embed()
    embed.add_field(
        name=f"{data.srcLangType} → {data.tarLangType}",
        value=f"`{word.content}` → `{data.translatedText}`",
    )
    return await interactions.response.send_message(embed=embed, ephemeral=True)


# 로그인
bot.run(NaipyBotConfig.token)
