import pyrogram
from pyrogram import filters, Client
from pyrogram.types import User, InlineKeyboardButton, InlineKeyboardMarkup, Message, Chat, CallbackQuery
from pymongo import MongoClient
import os

#Required Variables
API_ID = os.getenv("APP_ID")
API_HASH = os.getenv("APP_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME", "Warrior-Request")
GRP_LINK = os.getenv("GRP_LINK")
LOG = os.getenv("LOG_ID")
LOG_LINK = os.getenv("LOG_LINK")
GRP_ID = os.getenv("GRP_ID")

#Important Collections and Mongo DB
mongo_client = MongoClient(DB_URL)
db = mongo_client[DB_NAME]
started_users_collection = db["started_users"]
started_users = set()
requests = {}
warrior = GRP_ID[3:]

#Initialising the Bot
print("Tring to Connect to the bot...")
bot = Client(
    "Request Tracker",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)
print("Connected sucessfully")

@bot.on_message(filters.command('start'))
def start(bot, message) -> None:
    user_id = message.from_user.id
    started_users.add(user_id)
    mention = message.from_user.mention
    reply_markup = InlineKeyboardMarkup(
            [
    [
        InlineKeyboardButton("ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/Anime_Warior"),
        InlineKeyboardButton("ʙᴏᴛs ᴄʜᴀɴɴᴇʟ", url="https://t.me/thebotslibrary"),
    ],
    [
                    InlineKeyboardButton("ᴏɴɢᴏɪɴɢ ᴀɴɪᴍᴇ", url = "https://t.me/ongoing_warior"),
                    InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url = "https://t.me/Aakash1230")
        
    ]
            ]
        )
    text = f"Hello {mention} I am a request tracking bot built for @Anime_Warior, to build a private instance of this bot contact the developer!"
    started_users_collection.update_one({"_id": user_id}, {"$set": {"started": True}}, upsert=True)
    bot.send_message(chat_id=message.chat.id,
                             text=text, reply_markup=reply_markup)

@bot.on_message(filters.regex(r"^(\/request|[#]request)"))
async def request_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    me = await bot.get_me()
    BOT_NAME = me.username
    
    if not started_users_collection.find_one({"_id": user_id}):
        await message.reply_text("Please start the bot first.",
                                  reply_markup=InlineKeyboardMarkup([
                                      [InlineKeyboardButton("Start Bot", url=f"t.me/{BOT_NAME}")]
                                  ]))
    else:
        anime_name = message.text.split("#request ")[-1]
        user = message.from_user
        user_tag = f"@{user.username}" if user.username else user.first_name
        
        if not anime_name:
            await message.reply_text("Please provide a anime name to request.")
            return
        
        grp_message = await message.reply_text(
            text=f"Hello {user_tag}, Your Request Has been sent to the admins to reveiw track your request by clicking the below buttons!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Request Logs", url=f"{LOG_LINK}")
                    ]
                ]
            )
        )
        requests[user_id] = {"name": anime_name, "message_id": grp_message.id}
        log_message = await bot.send_message(
            chat_id=LOG,
            text=f"New Request From {user_tag}\n\n {anime_name}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Approve Request", callback_data=f"approve"),
                        InlineKeyboardButton("Reject Request", callback_data=f"reject"),
                        InlineKeyboardButton("Not Available", callback_data=f"unavailable")
                    ],
                    [
                        InlineKeyboardButton("Delete Request", callback_data=f"delete"),
                        InlineKeyboardButton("Request Message", url=f"https://t.me/c/{warrior}/{grp_message.id}")
                    ]
                ]
            )
        )
        
@bot.on_callback_query()
async def query_handler(bot: Client, query: CallbackQuery):
    data = query.data  
    channelID = str(query.message.chat.id)  
    user = await bot.get_chat_member(int(channelID), query.from_user.id)
    print(f"User ID: {query.from_user.id}, Status: {user.status}")
    if user.status == pyrogram.enums.ChatMemberStatus.MEMBER:
         await query.answer(
                            "This Can be done only by Admins..",
                            show_alert = True
                        )
    else:
        if data == "approve":
            result = "APPROVED"
            grpresult = "Your Requested Anime Has Been Uploaded To the channel check it out!"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Approved!", callback_data="None"), InlineKeyboardButton(text="Channel", url="https://t.me/anime_warior")]])
        elif data == "reject":
            result = "REJECTED"
            grpresult = "Sorry, Your Request Has Been Rejected!"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Rejected", callback_data="None")]])
        elif data == "unavailable":
            result = "NOT AVAILABLE"
            grpresult = "Sorry, Your Request Is Not Available Right Now!"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Unavailable", callback_data="None")]])
        elif data == "delete":
            result = "Delete"
            await query.message.delete()

    ogmsg = query.message.text
    newmsg = f"<b>{result}</b>\n\n<s>{ogmsg}</s>"
    usermention = ogmsg.removeprefix("New Request From ").split('\n\n')[0]
    await query.edit_message_text(text=newmsg, parse_mode=pyrogram.enums.ParseMode.HTML)
    await bot.send_message(chat_id=GRP_ID, text=f"Hello {usermention},\n {grpresult}", reply_markup=button)


          

print("Bot has been started...")
bot.run()
