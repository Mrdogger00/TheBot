from aiogram import Bot, Dispatcher, Router
from dotenv import load_dotenv
import os
import asyncio
from handlers import rt
from sqdb import engine, Base

load_dotenv()
TOKEN=os.getenv("BOT_TOKEN")



async def main():
    Base.metadata.create_all(engine)

    bot=Bot(token=TOKEN)
    dp=Dispatcher()
    dp.include_router(rt)

    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
