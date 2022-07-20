#=================================================================================================
# Copyright (C) 2022 by szsupunma@Github, < https://github.com/szsupunma >.
# Released under the "GNU v3.0 License Agreement".
# All rights reserved.
#=================================================================================================

import os
import asyncio
import requests
import random
import bs4

from pykeyboard import InlineKeyboard
from pyrogram.errors import UserNotParticipant
from pyrogram import filters, Client
from RandomWordGenerator import RandomWord
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, bad_request_400


from database import (
    get_served_users,
    add_served_user,
    remove_served_user,
    get_served_chats,
    add_served_chat,
    remove_served_chat
)

app = Client(
    "Fake_mail_bot",
    api_hash= os.environ["API_HASH"],
    api_id= int(os.environ["API_ID"]),
    bot_token=os.environ["BOT_TOKEN"]
)

#********************************************************************************
start_text = """
»مرحبًا! {} ،
»يمكنني إنشاء رسائل بريد إلكتروني مؤقتة لك . ارسل /new لإنشاء بريد جديد!

»المزايا 🥳
  
»• لا توجد نطاقات في القائمة السوداء (نطاقات حديثة).
  »• [API] (https://www.1secmail.com/api/v1/) صندوق البريد الإلكتروني الأساسي.
 »• نشط على مدار 24 ساعة (استضافة مدفوعة).

إرسال /domains للحصول على قائمة المجالات المتاحة.

المطور: @G5_F1
"""

CHANNEL_ID = int(os.environ['CHANNEL_ID'])
CHANNEL = os.environ['CHANNEL']
OWNER = int(os.environ['OWNER'])

start_button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👥 Group", url="https://t.me/B_O_S_T_A_T_0"),
                    InlineKeyboardButton("🗣 Channel", url="https://t.me/A_G_R_0")
                ],
		        [
                    InlineKeyboardButton("» المطور «", url="http://t.me/G5_F1"),
                    InlineKeyboardButton("➕Add to Group ➕", url=f"http://t.me/معرف بوتك?startgroup=new")
                ]    
            ]
)

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    try:
       await message._client.get_chat_member(CHANNEL_ID, message.from_user.id)
    except UserNotParticipant:
       await app.send_message(
			chat_id=message.from_user.id,
			text=f"""
🚧 **تم الرفض** {message.from_user.mention}
يجب عليك أن ،
🔹 [انضم إلى قناة التليجرام الخاصة بنا]‌‌(https://t.me/{CHANNEL}).
@A_G_R_0
""")
       return
    name = message.from_user.id
    if message.chat.type != "private":
       await app.send_message(
        name,
        text = start_text.format(message.from_user.mention),
        reply_markup = start_button)
       return await add_served_chat(message.chat.id) 
    else:
        await app.send_message(
    name,
    text = start_text.format(message.from_user.mention),
    reply_markup = start_button)
    return await add_served_user(message.from_user.id) 
    
#********************************************************************************
API1='https://www.1secmail.com/api/v1/?action=getDomainList'
API2='https://www.1secmail.com/api/v1/?action=getMessages&login='
API3='https://www.1secmail.com/api/v1/?action=readMessage&login='
#********************************************************************************

create = InlineKeyboardMarkup(
            [[InlineKeyboardButton("♡ آج‌ــ‌๋ـر ♡", url="https://t.me/A_G_R_0")]])

#********************************************************************************
@app.on_message(filters.command("new"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    m =  await app.send_message(name,text=f"📧 إنشاء بريد إلكتروني مؤقت ....",reply_markup = create)
    rp = RandomWord(max_word_size=8, include_digits=True)
    email = rp.generate()
    xx = requests.get(API1).json()
    domain = random.choice(xx)
    #print(email)
    mes = await app.send_message(
    name, 
    text = f"""
**📬 تم إنشاء عنوان بريدك الإلكتروني!**
📧 **البريد الإلكتروني** : `{email}@{domain}`
📨 **صندوق البريد** : `فارغ`
**بدعم من** : @A_G_R_0 """,
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ تحديث صندوق البريد‌‌ ♻️", callback_data = f"mailbox |{email}|{domain}")]]))
    pi = await mes.pin(disable_notification=True, both_sides=True)
    await m.delete()
    await pi.delete()

async def gen_keyboard(mails, email, domain):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    for mail in mails:
        id = mail['id']
        data.append(
            InlineKeyboardButton(f"{mail['subject']}", f"mail |{email}|{domain}|{id}")
        )
        num += 1
    data.append(
        InlineKeyboardButton(f"♻️ تحديث صندوق البريد‌‌ ♻️", f"mailbox |{email}|{domain}")
    )
    i_kbd.add(*data)
    return i_kbd
 
#********************************************************************************

@app.on_callback_query(filters.regex("mailbox"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain = callback_request.split("|")
    mails = requests.get(f'{API2}{email}&domain={domain}').json()
    if mails == []:
            await query.answer("🤷‍♂️ لم يتم العثور على رسائل!‌‌ 🤷‍♂️")
    else:
        try:
            smail = f"{email}@{domain}"
            mbutton = await gen_keyboard(mails,email, domain)
            await query.message.edit(f""" 
**📬📬 تم إنشاء عنوان بريدك الإلكتروني!**
📧 **البريد الإلكتروني** : `{smail}`
📨 **صندوق البريد** : ✅
**بدعم من** : @A_G_R_0""",
reply_markup = mbutton
)   
        except bad_request_400.MessageNotModified as e:
            await query.answer("🤷‍♂️ لم يتم العثور على رسائل!‌‌ 🤷‍♂️")

#********************************************************************************

@app.on_callback_query(filters.regex("mail"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain, id = callback_request.split("|")
    mail = requests.get(f'{API3}{email}&domain={domain}&id={id}').json()
    froms = mail['from']
    subject = mail['subject']
    date = mail['date']
    if mail['textBody'] == "":
        kk = mail['htmlBody']
        body = bs4.BeautifulSoup(kk, 'lxml')
        txt = body.get_text()
        text = " ".join(txt.split())
        url_part = body.find('a')
        link = url_part['href']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔗 فتح اللينك", url=link)
                ],
                [
                    InlineKeyboardButton("◀️ رجوع", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**من:** `{froms}`
**موضوعات:** `{subject}`   
**التاريخ**: `{date}`
{text}
""",
reply_markup = mbutton
)
    else:
        body = mail['textBody']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("◀️ رجوع", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**من:** `{froms}`
**موضوعات:** `{subject}`   
**التاريخ**: `{date}`
{body}
""",
reply_markup = mbutton
)
#********************************************************************************

@app.on_message(filters.command("domains"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    x = requests.get(f'https://www.1secmail.com/api/v1/?action=getDomainList').json()
    xx = str(",".join(x))
    email = xx.replace(",", "\n")
    await app.send_message(
    name, 
    text = f"""
**{email}**
""",
    reply_markup = create)



#============================================================================================
#Owner commands pannel here
#user_count, broadcast_tool

@app.on_message(filters.command("stats") & filters.user(OWNER))
async def stats(_, message: Message):
    name = message.from_user.id
    served_chats = len(await get_served_chats())
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    served_users = len(await get_served_users())
    served_users = []
    users = await get_served_users()
    for user in users:
        served_users.append(int(user["bot_users"]))

    await app.send_message(
        name,
        text=f"""
🍀 احصائيات الدردشات‌‌ 🍀
🙋‍♂️ المستخدمين : `{len(served_users)}`
👥 الجروبات : `{len(served_chats)}`
🚧 جميع المستخدمين & الجروبات : {int((len(served_chats) + len(served_users)))} """)

async def broadcast_messages(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await remove_served_user(user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await remove_served_user(user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await remove_served_user(user_id)
        return False, "Error"
    except Exception as e:
        return False, "Error"

@app.on_message(filters.private & filters.command("bcast") & filters.user(OWNER) & filters.reply)
async def broadcast_message(_, message):
    b_msg = message.reply_to_message
    chats = await get_served_users() 
    m = await message.reply_text("Broadcast in progress")
    for chat in chats:
        try:
            await broadcast_messages(int(chat['bot_users']), b_msg)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass  
    await m.edit(f"""
Broadcast Completed:.""")    

@app.on_message(filters.command("ads"))
async def ads_message(_, message):
    await message.reply_text(
"""     📮Advertise On Telegram 🚀

Want to promote anything ? 

Rose Bot is here with your basic needs. We work in around 2.5 thousand chats with thousand of userbase. One promotional broadcast reaches to thousands of peoples. 

Want to promote your online business ? Want to get people engagement? We are here!

Promote whatever you want at lowest and affordable prices.

https://telega.io/catalog_bots/szrosebot/card

🔥Your broadcast will reach group also so minimum 50k users see your message.
""")

print("I'm Alive Now!")
app.run()
