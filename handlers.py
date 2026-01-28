from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import random

from sqdb import User, Admin, engine, UserFactory

with open("factories.json", "r", encoding="utf-8") as f:
    FACTORIES = json.load(f)

def user_exists(tg_id):
    with Session(engine) as session:
        user=session.scalars(select(User).where(User.tg_id == tg_id)).first()
        if user:
            return True
        
        user=User(
            tg_id=tg_id,
            money=200,
            farm_time=datetime.utcnow(),
            name="bro"
        )
        session.add(user)
        session.commit()
        return user

def is_admin(tg_id):
    with Session(engine) as session:
        stmt = select(Admin).where(Admin.tg_id == tg_id)
        admin = session.scalars(stmt).first()
        return admin is not None

def user_time_left(tg_id, farm_time):
    with Session(engine) as session:
        stmt = select(User).where(User.tg_id == tg_id)
        user = session.scalars(stmt).first()
        if user:
            elapsed = datetime.utcnow() - user.farm_time
            remaining = timedelta(hours=8)  - elapsed
            return remaining
        return None

def get_session():
    return Session(engine)

def collect_factories(session, tg_id: int) -> str:
    user = session.get(User, tg_id)
    if not user:
        return "You are not registered in the database."
    factories=session.scalars(select(UserFactory).where(UserFactory.user_id == user.tg_id)).all()

    if not factories:
        return "You have no factories."

    now = datetime.utcnow()
    lines = []
    total_earned = 0
    for uf in factories:
        factory_info = FACTORIES.get(uf.factory_name)
        print(factory_info) ###debug
        if not factory_info:
            continue

        cooldown = timedelta(minutes=factory_info["cooldown_time"])
        elapsed = now - uf.last_used
        cycles= elapsed // cooldown
        
        if cycles<=0:
            continue

        earned = cycles * random.randint(factory_info["min_profit"], factory_info["max_profit"])

        total_earned += earned
        uf.last_used += cycles * cooldown
        print(cycles, earned) ###debug

        lines.append(f"{factory_info['name']}: + {earned} coins.")
        
        if total_earned==0:
            return "No factories are ready for collection yet."

    user.money += total_earned
    session.commit()
    
    lines.append(f"Total collected: {total_earned} coins.\nCurrent coins amount: {user.money}")
    if not lines:
        return "No factories are ready for collection yet."
    return "\n".join(lines)



mysession=get_session()


rt=Router()

@rt.message(Command("start"))
async def cmd_start(message: Message):
    user_exists(str(message.from_user.id))
    await message.answer("Welcome to The Bot!")

@rt.message(Command("farm"))
async def farm(message: Message):
#    await message.answer("farming...")
    tg_id = str(message.from_user.id)
    stmt = select(User).where(User.tg_id == tg_id)
    user = mysession.scalars(stmt).first()
    time_left = user_time_left(tg_id, None)
    if time_left is None:
        new_user = User(
            tg_id=tg_id,
            name=message.from_user.full_name,
            money=0,
            farm_time=datetime.utcnow()
        )
        mysession.add(new_user)
        mysession.commit()
        time_left = timedelta(0)
    if time_left <= timedelta(0):
        randcoin = random.randint(50, 150)
        user.money += randcoin
        user.farm_time = datetime.utcnow()
        mysession.commit()
        await message.answer(f"You have farmed {randcoin} coins!\nCurrent coins amount: {user.money}")
    elif time_left > timedelta(0):
        hours, remainder = divmod(int(time_left.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
    await message.answer(f"You need to wait {hours}h {minutes}m {seconds}s before farming again.")

@rt.message(Command("collect"))
async def collect(message: Message):
    text = collect_factories(mysession, message.from_user.id)
    print(text)
    await message.answer(text) #чо text пустий блять

# admin commands

@rt.message(Command("sreset")) 
async def sreset(message: Message):
    tg_id = str(message.from_user.id)
    if not is_admin(tg_id):
        await message.answer("You cannot use this command")
        return
    stmt = select(User).where(User.tg_id == tg_id)
    user = mysession.scalars(stmt).first()
    if user:
        user.farm_time = datetime.utcnow() - timedelta(hours=8)
        mysession.commit()
        await message.answer("Your farm time has been reset.")
    else:
        await message.answer("You are not registered in the database.")