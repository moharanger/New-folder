import asyncio

from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup

from KNMusic import app
from KNMusic.misc import db
from KNMusic.utils.database import (get_active_chats, get_lang,
                                    get_served_users, is_music_playing)
from KNMusic.utils.formatters import seconds_to_min
from KNMusic.utils.inline import stream_markup_timer, telegram_markup_timer
from strings import get_string

from ..admins.callback import wrong

checker = {}


async def timer():
    while not await asyncio.sleep(1):
        active_chats = await get_active_chats()
        for chat_id in active_chats:
            if not await is_music_playing(chat_id):
                continue
            playing = db.get(chat_id)
            if not playing:
                continue
            file_path = playing[0]["file"]
            if "index_" in file_path or "live_" in file_path:
                continue
            duration = int(playing[0]["seconds"])
            if duration == 0:
                continue
            db[chat_id][0]["played"] += 1


asyncio.create_task(timer())


async def markup_timer():
    while not await asyncio.sleep(2):
        active_chats = await get_active_chats()
        for chat_id in active_chats:
            try:
                if not await is_music_playing(chat_id):
                    continue
                playing = db.get(chat_id)
                if not playing:
                    continue
                duration_seconds = int(playing[0]["seconds"])
                if duration_seconds == 0:
                    continue
                try:
                    mystic = playing[0]["mystic"]
                    markup = playing[0]["markup"]
                except:
                    continue
                try:
                    check = wrong[chat_id][mystic.message_id]
                    if check is False:
                        continue
                except:
                    pass
                try:
                    language = await get_lang(chat_id)
                    _ = get_string(language)
                except:
                    _ = get_string("en")
                try:
                    buttons = (
                        stream_markup_timer(
                            _,
                            playing[0]["vidid"],
                            chat_id,
                            seconds_to_min(playing[0]["played"]),
                            playing[0]["dur"],
                        )
                        if markup == "stream"
                        else telegram_markup_timer(
                            _,
                            chat_id,
                            seconds_to_min(playing[0]["played"]),
                            playing[0]["dur"],
                        )
                    )
                    await mystic.edit_reply_markup(
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                except:
                    continue
            except:
                continue


asyncio.create_task(markup_timer())

APP = app.username


async def send_message_to_chats():
    users = await get_served_users()
    served_users = [int(user["user_id"]) for user in users]
    try:
        for chat_id in served_users:
            try:
                await app.forward_messages(chat_id, "TemanDemus_Id", 4)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                pass
    except Exception:
        pass


async def continuous_broadcast():
    while not await asyncio.sleep(43200):
        # while True:
        if APP == "TemanDemus_Id":
            try:
                await send_message_to_chats()
            except Exception:
                pass
        # await asyncio.sleep(43200)


asyncio.create_task(continuous_broadcast())
