from pyrogram import Client, filters
from pyrogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from Source.picwish import task_start, task_process
from pyrogram.errors import exceptions
from traceback import format_exc
from re import match
import mysqlm as db
import logging
from Config import config
import os

# creating app
app = Client(name='enhancer',
             api_hash=config.api_hash,
             api_id=config.api_id,
             bot_token=config.token)


# ------------------- FILTERS -------------------

# creating filter for check if user is in the channels
async def join(_, bot: Client, query: Message):
    user_id = query.from_user.id
    file = open(r'Config/channels.txt', 'r')
    channels = list(map(lambda x: x.replace('\n', ''), file.readlines()))
    channels_buttons = []
    if not channels:
        return True
    for channel_data in channels:
        channel_id, channel_name = channel_data.split(',')
        channels_buttons.append([InlineKeyboardButton(
            channel_name, url=f'https://t.me/{channel_id}')])
    else:
        # This is the submit button for after the user joins the channel
        channels_submit_button = [[InlineKeyboardButton(
            'جوین شدم ✅', url='https://t.me/AIReminiRoBot?start')]]

        # this is buttons markup for channels
        markup_channels = InlineKeyboardMarkup(
            channels_buttons + channels_submit_button)
        file.close()
    try:
        for channel in channels_buttons:
            channel_url = channel[0].url.replace('https://t.me/', '@')
            await bot.get_chat_member(
                chat_id=channel_url, user_id=user_id)
        return True

    # this except is for users that not joined the channels
    except exceptions.bad_request_400.UserNotParticipant:
        user_name = query.chat.first_name
        await bot.send_message(
            chat_id=user_id,
            text=f"""
سلام {user_name} خوش اومدی 🌹
برای استفاده از ربات باید عضو کانال  ها زیر بشی""",
            reply_markup=markup_channels)
        return False


# crating filter
join_filter = filters.create(join)


async def last_process(_, bot: Client, query: Message):
    user_id = query.from_user.id
    last_process_time, now_time = await db.read_last_processing(user_id)
    now_time = now_time.replace(tzinfo=None)
    time = 40
    if last_process_time is None:
        return True
    else:
        different = (last_process_time - now_time).seconds

        if different >= time:
            return True
        else:
            text = f'شما یک پردازش ناتمام دارید لطفا {time - different} ثانیه منتظر بمانید.'
            await bot.send_message(user_id, text)
            return False


last_process_filter = filters.create(last_process)


# ------------------- FILTERS -------------------


# ------------------- COMMANDS -------------------

@app.on_message(filters.command('start') & filters.private)
async def start(bot: Client, message: Message):
    chat_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username
    text = f"""
سلام {name} خوش اومدی 🌹

➕ با من به راحتی به از عکس هات رو بهتر کن

🔸 برای شروع کافیه که گزینه مورد نظرت رو انتخاب کنی :
"""
    buttons = [
        [KeyboardButton('🖼 بهبود کیفیت تصویر')],
        [KeyboardButton('🖼 حذف پس زمینه')]
    ]
    markup_buttons = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await bot.send_message(chat_id, text, reply_markup=markup_buttons)
    await db.add_user(chat_id, name, username)
    await db.set_step(chat_id, 'start')


# --------- ADMIN COMMANDS ---------

@app.on_message(filters.command('channels') & filters.user(config.admin_id))
async def users(_, message: Message):
    text = message.text.replace('/channels\n', '')
    # message.text must be this
    """
/channels
CHANNEL ID,CHANNEL NAME
    """

    with open(r'Config/channels.txt', 'w') as file:
        file.write(text)
    await message.reply_text('Channels successfully changed!')


@app.on_message(filters.command('users') & filters.user(config.admin_id))
async def users(_, message: Message):
    result = await db.all_users()
    await message.reply_text(result)


@app.on_message(filters.command('send') & filters.user(config.admin_id))
async def users(bot: Client, message: Message):
    text = message.text.replace('/send\n', '')
    # message.text must be this
    """
/send
YOUR MESSAGE
    """
    result = await db.all_users(count=False)
    counter = 0
    for user_id in result:
        try:
            await bot.send_message(int(user_id[0]), text)
            counter += 1
        except exceptions.UserIsBlocked:
            continue
    await bot.send_message(config.admin_id, f'Successful!\n{counter} message sent')


# --------- ADMIN COMMANDS ---------

# ------------------- COMMANDS -------------------


# ------------------- USER MESSAGES -------------------

@app.on_message(filters.text & filters.private & join_filter)
async def messages(bot: Client, message: Message):
    chat_id = message.from_user.id
    text = message.text

    step = await db.get_step(chat_id)

    commands = [
        [r'🔙 بازگشت', r'.+', start],
        [r'🖼 بهبود کیفیت تصویر', r'.+', enhancer],
        [r'👤 بهبود چهره|🖼 بهبود کامل', r'.+', enhancer_type],
        [r'🖼 حذف پس زمینه', r'.+', remove_background],
        [r'PNG|JPG', r'.+', remove_background_type]
    ]

    for pattern, required_step, callback in commands:
        if match(pattern, text) and match(required_step, step):
            await callback(bot, message)
            break


async def enhancer(bot: Client, message: Message):
    chat_id = message.from_user.id
    buttons = [[KeyboardButton('👤 بهبود چهره'), KeyboardButton('🖼 بهبود کامل')],
               [KeyboardButton('🔙 بازگشت')]]
    markup_buttons = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await bot.send_message(chat_id, 'لطفا یکی از موارد زیر را انتخاب کنید ⬇️', reply_markup=markup_buttons)


async def enhancer_type(bot: Client, message: Message):
    chat_id = message.from_user.id
    text = message.text

    if text == '🖼 بهبود کامل':
        await db.set_type(chat_id, 'clean')
    elif text == '👤 بهبود چهره':
        await db.set_type(chat_id, 'face')
    buttons = [[KeyboardButton('🔙 بازگشت')]]
    markup_buttons = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await bot.send_message(chat_id, 'لطفا تصویر مورد نظر خود را ارسال کنید', reply_markup=markup_buttons)
    await db.set_step(chat_id, 'enhance')


async def remove_background(bot: Client, message: Message):
    chat_id = message.from_user.id
    buttons = [[KeyboardButton('PNG'), KeyboardButton('JPG')],
               [KeyboardButton('🔙 بازگشت')]]
    markup_buttons = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await bot.send_message(chat_id, 'لطفا یکی از فرمت های زیر را انتخاب کنید ⬇️', reply_markup=markup_buttons)


async def remove_background_type(bot: Client, message: Message):
    chat_id = message.from_user.id
    text = message.text
    if text == 'PNG':
        await db.set_type(chat_id, 'PNG')
    elif text == 'JPG':
        await db.set_type(chat_id, 'JPG')
    buttons = [[KeyboardButton('🔙 بازگشت')]]
    markup_buttons = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await bot.send_message(chat_id, 'لطفا تصویر مورد نظر خود را ارسال کنید', reply_markup=markup_buttons)
    await db.set_step(chat_id, 'removeBG')


@app.on_message(filters.photo & filters.private & join_filter & last_process_filter)
async def photo(bot: Client, message: Message):
    chat_id = message.from_user.id
    step = await db.get_step(chat_id)
    if step == 'enhance' or step == 'removeBG':
        try:
            category = step
            msg = await bot.send_message(chat_id, '📥 در حال دریافت اطلاعات...')
            await db.add_last_processing(chat_id)
            type_ = await db.get_type(chat_id)
            user_photo = await bot.download_media(message)
            try:
                task_id = await task_start(user_photo, category, type_)
                new_photo = await task_process(task_id, category)
            except ValueError:
                formatted_exc = format_exc()
                if 'successfully changed the token' in formatted_exc:
                    task_id = await task_start(user_photo, category, type_)
                    new_photo = await task_process(task_id, category)
                else:
                    raise RuntimeError

            await bot.edit_message_text(chat_id, msg.id, '📥 در حال ارسال اطلاعات...')
            if type_ == 'PNG':
                await bot.send_document(chat_id, new_photo, caption='👤 | Enhanced by @AIReminiRoBot')
            else:
                await bot.send_photo(chat_id, new_photo, caption='👤 | Enhanced by @AIReminiRoBot')
            await bot.delete_messages(chat_id, msg.id)
            os.remove(user_photo)
            os.remove(new_photo)
        except RuntimeError:
            await bot.send_message(chat_id, ' متاسفانه پردازش تصویر شما ناموفق بود!')

    else:
        await bot.send_message(chat_id, 'متوجه نشدم!')


# ------------------- USER MESSAGES -------------------


if __name__ == '__main__':
    try:
        logging.basicConfig(filename='errors.log', level=logging.ERROR,
                            format='%(asctime)s %(levelname)s: %(message)s')
        print('Bot is Alive')

        app.run()
    except Exception as e:
        logging.error(str(e))
