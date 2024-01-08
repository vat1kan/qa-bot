import asyncio
import logging
import time
import os
import sys
from typing import Any, Dict
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Formating import Point, DescriptFormating, StepsFormating, PlatformFormating, about_text, dict_values

TOKEN = os.getenv('TOKEN')

br_router = Router()
ids = []

class Report(StatesGroup):
    media_file = State()
    title = State()
    description = State()
    steps = State()
    severity = State()
    environment = State()

@br_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Report.media_file)
    msg = await message.answer("Reporting started. Upload your media file:")
    global chat_id
    chat_id = message.chat.id
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Command("cancel"))
@br_router.message(F.text.casefold() == "/cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    ids.append(message.message_id)
    await state.clear()
    for id in ids: 
        await bot.delete_message(chat_id, id)
    ids.clear()
    cancel = await message.answer("Reporting cancelled.")
    time.sleep(3)
    await bot.delete_message(chat_id, cancel.message_id)

@br_router.message(Command("info"))
@br_router.message(F.text.casefold() == "/info")
async def info(message: Message)-> None:
    msg = await message.answer(f"{about_text()}")
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Command("dict"))
@br_router.message(F.text.casefold() == "/dict")
async def info (message: Message)->None:
    msg = await message.answer(dict_values())
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Report.media_file)
async def process_media(message: Message, state: FSMContext) -> None:
    await state.update_data(media_file=message)
    await state.set_state(Report.title)
    msg = await message.answer("Enter bug report title.")
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Report.title)
async def process_title (message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(Report.description)
    msg = await message.answer("Enter bug description.")
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Report.description)
async def process_description (message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(Report.steps)
    msg = await message.answer("Enter steps to bug reproduce.")
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Report.steps)
async def process_steps (message: Message, state: FSMContext) -> None:
    await state.update_data(steps=message.text)
    await state.set_state(Report.severity)
    msg = await message.answer("Enter the severity of the bug.")
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Report.severity)
async def process_severity (message: Message, state: FSMContext) -> None:
    await state.update_data(severity=message.text)
    await state.set_state(Report.environment)
    msg = await message.answer("Specify the environment in which the bug is detected.")
    ids.extend((message.message_id, msg.message_id))

@br_router.message(Report.environment)
async def process_environment (message: Message, state: FSMContext) -> None:
    data = await state.update_data(environment=message.text)
    await show_summary(message=message, data=data)
    ids.append(message.message_id)
    await state.clear()

@br_router.message(Report.environment)
async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    try:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text='Delete', callback_data='clear'))
        
        media_file = data.get("media_file")

        values = [data.get('title'), data.get('description'), data.get('steps'), data.get('severity'), data.get('environment')]
        titles = ['Название: ','\n\nОписание:\n','\n\nШаги воспроизведения:\n','\nСерьезность\n','\n\nПлатформа:\n']
        funcs = [Point, DescriptFormating, StepsFormating, Point, PlatformFormating]
        skips = ['pass', 'пасс', 'пас', '...']
        br_text = ""

        for i in range(len(values)):
            if values[i] not in skips:
                br_text += f"<b>{titles[i]}</b>{''.join(funcs[i](values[i]))}"

        if media_file.photo:
            msg = await bot.send_photo(message.chat.id, media_file.photo[-1].file_id, caption=f"{br_text}", reply_markup=builder.as_markup())
            ids.append(msg.message_id)
        elif media_file.video:
            msg = await bot.send_video(message.chat.id, media_file.video.file_id, caption=f"{br_text}", reply_markup=builder.as_markup())
            ids.append(msg.message_id)
        else:
            msg = await message.answer(f"{br_text}", reply_markup=builder.as_markup())
            ids.append(msg.message_id)
        print(f"messages id: \n\n{ids}\n\n")
    except Exception as e:
        await message.answer(text=f"<b>Some error occurred. Debug message:</b>\n\n<code>{e}</code>", parse_mode='html')

@br_router.callback_query()
async def clear(callback_query: types.CallbackQuery) -> Any:
    try:
        for id in ids: 
            await bot.delete_message(chat_id, id)
        ids.clear()
    except Exception as e:
        print(f"Some error: {e}")

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(br_router)
    await dp.start_polling(bot)

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())