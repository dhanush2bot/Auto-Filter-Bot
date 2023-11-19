import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, __version__
import pyromod.listen
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from aiohttp import web
from database.users_chats_db import db
from web import web_server
from info import LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, PORT, BIN_CHANNEL
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
import time, os
from pyrogram.errors import AccessTokenExpired, AccessTokenInvalid


class Bot(Client):
    def __init__(self):
        super().__init__(
            name='Auto_Filter_Bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        try:
            temp.START_TIME = time.time()
            b_users, b_chats = await db.get_banned()
            temp.BANNED_USERS = b_users
            temp.BANNED_CHATS = b_chats
            await super().start()
            if os.path.exists('restart.txt'):
                with open("restart.txt") as file:
                    chat_id, msg_id = map(int, file)
                try:
                    await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
                except:
                    pass
                os.remove('restart.txt')
            temp.BOT = self
            await Media.ensure_indexes()
            me = await self.get_me()
            temp.ME = me.id
            temp.U_NAME = me.username
            temp.B_NAME = me.first_name
            username = '@' + me.username
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()
            logging.info(f"\n\nBot [{username}] Started!\n\n")
            try:
                await self.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} Restarted! 🤖</b>")
            except:
                logging.error("Make sure bot admin in LOG_CHANNEL, exiting now")
                exit()
            try:
                m = await self.send_message(chat_id=BIN_CHANNEL, text="Test")
                await m.delete()
            except:
                logging.error("Make sure bot admin in BIN_CHANNEL, exiting now")
                exit()
        except AccessTokenExpired:
            logging.error("Access token has expired. Please check your credentials.")
            exit()
        except AccessTokenInvalid:
            logging.error("Access token is invalid. Please check your credentials.")
            exit()
        except Exception as e:
            logging.error(f"An error occurred during bot startup: {e}")
            exit()

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped! Bye...")


app = Bot()
app.run()
