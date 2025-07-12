import logging
from config import Config
from database import Database
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.types import ParseMode
from pyrogram.errors import FloodWait
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("TelegramBot.log"),
        logging.StreamHandler()
    ]
)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=Config.BOT_SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={"root": "plugins"},
        )
        self.log = logging.getLogger(__name__)

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()
            self.log.info(f"{me.first_name} with for pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
            self.id = me.id
            self.username = me.username
            self.first_name = me.first_name
            self.set_parse_mode(ParseMode.DEFAULT)
            text = "**๏[-ิ_•ิ]๏ bot restarted !**"
            self.log.info(text)
            success = failed = 0
            try:
                users = await db.get_all_frwd()
                async for user in users:
                    chat_id = user['user_id']
                    try:
                        await self.send_message(chat_id, text)
                        success += 1
                        await asyncio.sleep(0.5)
                    except FloodWait as e:
                        await asyncio.sleep(e.value + 1)
                        await self.send_message(chat_id, text)
                        success += 1
                    except Exception as e:
                        self.log.error(f"Failed to send message to {chat_id}: {str(e)}")
                        failed += 1
                if (success + failed) != 0:
                    await db.rmve_frwd(all=True)
                    self.log.info(f"Restart message status success: {success} failed: {failed}")
            except Exception as e:
                self.log.error(f"Failed to process notify users: {str(e)}")
        except Exception as e:
            self.log.error(f"Bot failed to start: {str(e)}")
            raise

db = Database(Config.DATABASE_URI, Config.DATABASE_NAME)
app = Bot()
app.run()
