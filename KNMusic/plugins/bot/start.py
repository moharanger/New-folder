import asyncio
import logging
import time

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL
from config.config import OWNER_ID
from KNMusic import Telegram, YouTube, app
from KNMusic.misc import SUDOERS, _boot_
from KNMusic.plugins.play.playlist import del_plist_msg
from KNMusic.plugins.sudo.sudoers import sudoers_list
from KNMusic.utils.database import (add_served_chat, add_served_user,
                                    blacklisted_chats, get_assistant, get_lang,
                                    get_userss, is_on_off,
                                    is_served_private_chat)
from KNMusic.utils.decorators.language import LanguageStart
from KNMusic.utils.formatters import get_readable_time
from KNMusic.utils.functions import MARKDOWN, WELCOMEHELP
from KNMusic.utils.inline import alive_panel, private_panel, start_pannel
from KNMusic.utils.note_funcs import send_notes
from strings import get_string

from .help import help_parser

loop = asyncio.get_running_loop()


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    message.chat.id
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            if config.START_IMG_URL:
                text, keyboard = await help_parser(message.from_user.mention)
                return await message.reply_photo(
                    photo=START_IMG_URL,
                    caption=text,
                    reply_markup=keyboard,
                )
            else:
                return await message.reply_text(
                    text=_["help_1"],
                    reply_markup=keyboard,
                )
        if name[0:4] == "song":
            await message.reply_text(_["song_2"])
            return
        if name == "mkdwn_help":
            await message.reply(
                MARKDOWN,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        if name == "greetings":
            await message.reply(
                WELCOMEHELP,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        if name.startswith("note_"):
            try:
                (
                    _,
                    Gchat_id,
                    text,
                ) = name.split("_", 2)
                logging.info(f"{Gchat_id} {text}")
                await send_notes(message, Gchat_id, text)
            except Exception as e:
                logging.exception(e)

        if name[0:3] == "sta":
            m = await message.reply_text("🔎 ғᴇᴛᴄʜɪɴɢ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ sᴛᴀᴛs.!")
            stats = await get_userss(message.from_user.id)
            tot = len(stats)
            if not stats:
                await asyncio.sleep(1)
                return await m.edit(_["ustats_1"])

            def get_stats():
                msg = ""
                limit = 0
                results = {}
                for i in stats:
                    top_list = stats[i]["spot"]
                    results[str(i)] = top_list
                    list_arranged = dict(
                        sorted(
                            results.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    )
                if not results:
                    return m.edit(_["ustats_1"])
                tota = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10:
                        continue
                    if limit == 0:
                        videoid = vidid
                    limit += 1
                    details = stats.get(vidid)
                    title = (details["title"][:35]).title()
                    if vidid == "telegram":
                        msg += f"🔗[ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇs ᴀɴᴅ ᴀᴜᴅɪᴏs]({config.SUPPORT_GROUP})  played {count} ᴛɪᴍᴇs\n\n"
                    else:
                        msg += f"🔗 [{title}](https://www.youtube.com/watch?v={vidid})  played {count} times\n\n"
                msg = _["ustats_2"].format(tot, tota, limit) + msg
                return videoid, msg

            try:
                videoid, msg = await loop.run_in_executor(None, get_stats)
            except Exception as e:
                print(e)
                return
            thumbnail = await YouTube.thumbnail(videoid, True)
            await m.delete()
            await message.reply_photo(photo=thumbnail, caption=msg)
            return
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            await asyncio.sleep(1)
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                message.from_user.mention
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} baru saja memulai bot <code>list sudo </code>\n\n : {sender_id}\nUser name: {sender_name}",
                )
            return
        if name[0:3] == "lyr":
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = config.lyrical
            lyrics = lyrical.get(query)
            if lyrics:
                await Telegram.send_split_text(message, lyrics)
                return
            else:
                await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ʟʏʀɪᴄs.")
                return
        if name[0:3] == "del":
            await del_plist_msg(client=client, message=message, _=_)
            await asyncio.sleep(1)
        if name[0:3] == "inf":
            m = await message.reply_text("🔎 ғᴇᴛᴄʜɪɴɢ ɪɴғᴏ!")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = f"""
🔍__ᴠɪᴅᴇᴏ ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ__

❇️ᴛɪᴛʟᴇ: {title}

⏳ᴅᴜʀᴀᴛɪᴏɴ: {duration} Mins
👀ᴠɪᴇᴡs: `{views}`
⏰ᴘᴜʙʟɪsʜᴇᴅ ᴛɪᴍᴇ: {published}
🎥ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ: {channel}
📎ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ: [ᴠɪsɪᴛ ғʀᴏᴍ ʜᴇʀᴇ]({channellink})
🔗ᴠɪᴅᴇᴏ ʟɪɴᴋ: [ʟɪɴᴋ]({link})
"""
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🎥 ᴡᴀᴛᴄʜ ", url=f"{link}"),
                        InlineKeyboardButton(text="🔄 ᴄʟᴏsᴇ", callback_data="close"),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=key,
            )
            await asyncio.sleep(1)
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} baru saja memulai botb<code>Info video </code>\n\nUser ID: {sender_id}\nUser name {sender_name}",
                )
    else:
        try:
            await app.resolve_peer(OWNER_ID[0])
            OWNER_ID[0]
        except:
            pass
        out = private_panel(_)
        b = await message.reply_sticker(
            "CAACAgUAAxkBAAJ4tWaLZcUbwKzfkYDlGloILp06LVm6AAKCBwAC_-3QVE3JW0_6oFU9HgQ"
        )
        if config.START_IMG_URL:
            try:
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_1"].format(app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
            except:
                await message.reply_text(
                    text=_["start_1"].format(app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
        else:
            await message.reply_text(
                text=_["start_1"].format(app.mention),
                reply_markup=InlineKeyboardMarkup(out),
            )
        await b.delete()
        if await is_on_off(config.LOG):
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            return await app.send_message(
                config.LOG_GROUP_ID,
                f"{message.from_user.mention} memulai bot \n\nUser ID : {sender_id}\nUser name: {sender_name}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    out = alive_panel(_)
    uptime = int(time.time() - _boot_)
    message.chat.id
    if config.START_IMG_URL:
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=_["start_7"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )
    else:
        await message.reply_text(
            text=_["start_7"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(message.chat.id):
            await message.reply_text(
                "mode pribadi bot ini telah diaktifkan hanya pemilik saya yang dapat menggunakan ini jika Anda ingin menggunakan ini dalam obrolan Anda, jadi katakan kepada pemilik saya untuk mengotorisasi obrolan Anda"
            )
            return await app.leave_chat(message.chat.id)
    else:
        await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if member.id == app.id:
                chat_type = message.chat.type
                if chat_type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_5"])
                    return await app.leave_chat(message.chat.id)
                if chat_id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_6"].format(
                            f"https://t.me/{app.username}?start=sudolist"
                        )
                    )
                    return await app.leave_chat(chat_id)
                userbot = await get_assistant(message.chat.id)
                out = start_pannel(_)
                await message.reply_text(
                    _["start_2"].format(
                        app.mention,
                        userbot.username,
                        userbot.id,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
            if member.id in config.OWNER_ID:
                return await message.reply_text(
                    _["start_3"].format(app.mention, member.mention)
                )
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_4"].format(app.mention, member.mention)
                )
            return
        except:

            return


__MODULE__ = "Bots"
__HELP__ = """<blockquote><b>

/stats - Gᴇᴛ Tᴏᴘ 𝟷𝟶 Tʀᴀᴄᴋs Gʟᴏʙᴀʟ Sᴛᴀᴛs, Tᴏᴘ 𝟷𝟶 Usᴇʀs ᴏғ ʙᴏᴛ, Tᴏᴘ 𝟷𝟶 Cʜᴀᴛs ᴏɴ ʙᴏᴛ, Tᴏᴘ 𝟷𝟶 Pʟᴀʏᴇᴅ ɪɴ ᴀ ᴄʜᴀᴛ ᴇᴛᴄ ᴇᴛᴄ.

/sudolist - Cʜᴇᴄᴋ Sᴜᴅᴏ Usᴇʀs ᴏғ Yᴜᴋᴋɪ Mᴜsɪᴄ Bᴏᴛ

/lyrics [Mᴜsɪᴄ Nᴀᴍᴇ] - Sᴇᴀʀᴄʜᴇs Lʏʀɪᴄs ғᴏʀ ᴛʜᴇ ᴘᴀʀᴛɪᴄᴜʟᴀʀ Mᴜsɪᴄ ᴏɴ ᴡᴇʙ.

/song [Tʀᴀᴄᴋ Nᴀᴍᴇ] ᴏʀ [YT Lɪɴᴋ] - Dᴏᴡɴʟᴏᴀᴅ ᴀɴʏ ᴛʀᴀᴄᴋ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴍᴘ𝟹 ᴏʀ ᴍᴘ𝟺 ғᴏʀᴍᴀᴛs.

/player -  Gᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ Pʟᴀʏɪɴɢ Pᴀɴᴇʟ.

c sᴛᴀɴᴅs ғᴏʀ ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ.

/queue ᴏʀ /cqueue - Cʜᴇᴄᴋ Qᴜᴇᴜᴇ Lɪsᴛ ᴏғ Mᴜsɪᴄ.</b></blockquote>"""
