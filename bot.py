# -*- coding: utf-8 -*-
import os
import json
from telethon import TelegramClient, events
# NAYA BADLAV: KeyboardButton aur ReplyKeyboardMarkup ki ab zaroorat nahi hai.
from datetime import datetime, timedelta
import logging
import re

# === ENVIRONMENT VARIABLES ===
try:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_ID = int(os.getenv('ADMIN_ID'))
    NOTIFICATION_CHANNEL_ID = int(os.getenv('NOTIFICATION_CHANNEL_ID'))
except (TypeError, ValueError):
    print("CRITICAL ERROR: Environment variables (API_ID, ADMIN_ID, etc.) sahi number nahi hain. Please check your config.")
    exit(1)

# === DATA FILE, LOGGING & NEW: ADULT CONTENT KEYWORDS ===
DATA_FILE = 'bot_data.json'
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

ADULT_KEYWORDS = [
    'porn', 'sex', 'sexy', 'nude', 'naked', 'fuck', 'chut', 'lund', 
    'randi', 'gaand', 'bitch', 'xxx', 'boobs', 'pussy'
]


# ==============================================================================
# === DATA HANDLING FUNCTIONS (DATA KO LOAD AUR SAVE KARNA) ===
# ==============================================================================

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            user_data = data.get('user_data', {})
            total_users = data.get('total_users', len(user_data))
            return user_data, total_users
    except (FileNotFoundError, json.JSONDecodeError):
        return {}, 0

def save_data(user_data, total_users):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({'user_data': user_data, 'total_users': total_users}, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log.error(f"FATAL: Data save nahi ho pa raha! Error: {e}")

# Initializing Bot
user_data, total_users = load_data()
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ==============================================================================
# === HELPER FUNCTIONS (MADADGAAR FUNCTIONS) ===
# ==============================================================================

async def send_notification(message, parse_mode='md'):
    try:
        await client.send_message(NOTIFICATION_CHANNEL_ID, message, parse_mode=parse_mode)
    except Exception as e:
        log.error(f"Error sending notification: {e}")

async def log_and_notify_activity(event, action):
    user = await event.get_sender()
    user_id = user.id
    username = f"@{user.username}" if user.username else "N/A"
    notification_text = (
        f"**User Activity**\n\n"
        f"**User:** {user.first_name}\n"
        f"**User ID:** `{user_id}`\n"
        f"**Username:** {username}\n"
        f"**Action:** {action}"
    )
    await send_notification(notification_text)

# ### NAYA BADLAV: Plan selection ke liye naya function ###
# Yeh function ab buttons nahi, balki commands dikhayega.
async def send_plan_selection_prompt(event):
    msg = (
        "Aapka free trial ya subscription khatam ho gaya hai. 😔\n\n"
        "Bot ka istemal jaari rakhne ke liye, kripya neeche diye gaye commands mein se koi ek chunein aur send karein:\n\n"
        "**Plans:**\n"
        "🔹 **1 Mahina (₹79):**\n`/buy_1_month`\n\n"
        "🔹 **4 Mahine (₹300):**\n`/buy_4_months`\n\n"
        "🔹 **1 Saal (₹600):**\n`/buy_1_year`\n\n"
        "Plan command send karne ke baad, payment ke liye admin se sampark karein."
    )
    await event.respond(msg, parse_mode='md')


def check_user_status(user_id):
    """SUDHAR KIYA GAYA: Is function ki logic ko behtar banaya gaya hai taaki trial sahi se expire ho."""
    user_id_str = str(user_id)
    
    if user_id == ADMIN_ID:
        return True # Admin ke paas hamesha access rahega

    user_info = user_data.get(user_id_str, {})
    if not user_info: return True # Naye user ko allow karein
    
    if user_info.get('is_blocked', False): return False
    
    # 1. Paid user check
    if user_info.get('is_paid', False):
        end_date_str = user_info.get('subscription_end_date')
        if end_date_str and datetime.now() <= datetime.fromisoformat(end_date_str):
            return True
        else:
            user_data[user_id_str]['is_paid'] = False
            # Data save baad mein hoga
    
    # 2. Custom trial date check
    trial_end_date_str = user_info.get('trial_end_date')
    if trial_end_date_str and datetime.now() <= datetime.fromisoformat(trial_end_date_str):
        return True

    # 3. Default 7-day trial check (Agar custom trial set nahi hai)
    if not trial_end_date_str:
        start_date_str = user_info.get('start_date')
        if start_date_str:
            trial_end_date = datetime.fromisoformat(start_date_str) + timedelta(days=7)
            if datetime.now() <= trial_end_date:
                return True
        
    # Agar upar koi bhi condition True nahi hai, to user ka access khatam ho chuka hai.
    save_data(user_data, total_users) # Agar paid status change hua hai to save karein
    return False

# ==============================================================================
# === USER COMMANDS (SABHI COMMANDS AB JAWAB DENGE) ===
# ==============================================================================

@client.on(events.NewMessage(pattern=r'^/start$'))
async def start(event):
    global total_users
    user_id, user_id_str = event.sender_id, str(event.sender_id)
    log.info(f"User {user_id} used /start.")
    
    if user_id_str not in user_data:
        user_data[user_id_str] = {
            'start_date': datetime.now().isoformat(), 
            'is_paid': False, 
            'is_blocked': False,
            'subscription_end_date': None, 
            'trial_end_date': None,
            'channels': [], 
            'links': {}, 
            'active_channel': None
        }
        total_users += 1
        save_data(user_data, total_users)
        
        await log_and_notify_activity(event, "Started the bot for the first time.")
        
        await event.respond(
            'Namaste! 🙏 Bot mein aapka swagat hai!\n\n'
            '**Congratulations! Aapko is bot ka 7-din ka free trial mila hai.** 🎉\n\n'
            'Ye bot aapke messages mein automatically links add kar dega.\n'
            'Commands dekhne ke liye /allcommands type karein.\n\n'
            '--- **Zaroori Soochna** ---\n'
            '⚠️ **Kripya dhyan dein:** Is bot par adult (18+) content ka prayog karna ya share karna sakht mana hai. Agar aap aisi koi bhi samagri bhejte hain, to aapko **bina kisi chetavani ke turant block kar diya jayega.**',
            parse_mode='md'
        )
    else:
        if not check_user_status(user_id):
            await send_plan_selection_prompt(event) # Naya function call
            return
        await event.respond('Aapka bot mein fir se swagat hai! Commands dekhne ke liye /allcommands use karein.')
        await log_and_notify_activity(event, "Restarted the bot.")

@client.on(events.NewMessage(pattern=r'^/allcommands$'))
async def all_commands(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, "Used /allcommands")
    
    commands_list = (
        '/start - Bot ko start karein.\n'
        '/help - Support ke liye sampark karein.\n'
        '/addchannel - Channel add karein (e.g., /addchannel -100123...).\n'
        '/addlink - Text aur link add karein (e.g., /addlink text link).\n'
        '/showchannels - Apne added channels dekhein.\n'
        '/showlinks - Apne added links dekhein.\n'
        '/removechannel - Channel remove karein (e.g., /removechannel -100123...).\n'
        '/removelink - Link remove karein (e.g., /removelink text).\n'
        '/selectchannel - Link lagane ke liye channel select karein (e.g., /selectchannel -100123...).\n'
        '/deselectchannel - Channel deselect karein.'
    )
    admin_commands = (
        '\n\n--- **Admin Commands** ---\n'
        '/totalusers - Sabhi users dekhein.\n'
        '/broadcast <message> - Sabhi users ko message bhejein.\n'
        '/activate <user_id> <duration> - User ka subscription activate karein.\n'
        '/block <user_id> - User ko block karein.\n'
        '/unblock <user_id> - User ko unblock karein.\n'
        '/settrial <user_id> <duration> - User ka trial set karein (e.g., 30s, 5m, 2h, 5d).'
    )
    response_text = f'**Bot Commands:**\n\n{commands_list}'
    if event.sender_id == ADMIN_ID:
        response_text += admin_commands
    await event.respond(response_text, parse_mode='md')

@client.on(events.NewMessage(pattern=r'^/help$'))
async def help_command(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, "Used /help")
    await event.respond('Aapko koi bhi problem ho, to mujhe yahaan contact karein: @captain_stive')

# ### Baaki sabhi user commands mein bhi prompt function ko update kiya gaya ###

@client.on(events.NewMessage(pattern=r'^/addchannel(\s+.*)?$'))
async def add_channel(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, f"Used /addchannel command.")
    arg = event.pattern_match.group(1)
    if not arg or not arg.strip():
        await event.respond('**Galat Format!**\nSahi tarika: `/addchannel -100123456789`', parse_mode='md'); return
    try:
        channel_id = int(arg.strip())
        user_id_str = str(event.sender_id)
        user_channels = user_data.get(user_id_str, {}).get('channels', [])
        if channel_id not in user_channels:
            user_channels.append(channel_id)
            user_data[user_id_str]['channels'] = user_channels
            save_data(user_data, total_users)
            await event.respond(f'✅ Channel ID `{channel_id}` add ho gaya!', parse_mode='md')
        else:
            await event.respond(f'⚠️ Channel ID `{channel_id}` pahle se hi add hai!', parse_mode='md')
    except ValueError:
        await event.respond('**Galat ID!**\nChannel ID ek number hona chahiye, jaise: `-100123456789`', parse_mode='md')

@client.on(events.NewMessage(pattern=r'^/deselectchannel$'))
async def deselect_channel(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, "Used /deselectchannel")
    user_id_str = str(event.sender_id)
    if user_data.get(user_id_str, {}).get('active_channel') is not None:
        user_data[user_id_str]['active_channel'] = None
        save_data(user_data, total_users)
        await event.respond('✅ Active channel deselect ho gaya hai.')
    else:
        await event.respond('⚠️ Pehle se koi channel active nahi hai.')

@client.on(events.NewMessage(pattern=r'^/addlink(\s+.*)?$'))
async def add_link(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    args = event.pattern_match.group(1)
    if not args or not args.strip():
        await event.respond('**Galat Format!**\nSahi tarika: `/addlink Your Text https://example.com`', parse_mode='md'); return
    match = re.match(r'(.+?)\s+(https?://[^\s]+)', args.strip())
    if not match:
        await event.respond('**Galat Format!**\nLink `http` ya `https` se shuru hona chahiye.\nExample: `/addlink Join Now https://t.me/....`', parse_mode='md'); return
    text, link = match.groups()
    user_id_str = str(event.sender_id)
    user_data.setdefault(user_id_str, {}).setdefault('links', {})[text.strip()] = link.strip()
    save_data(user_data, total_users)
    try:
        user = await event.get_sender()
        notification_text = (f"**🔗 Link Added by User**\n\n**User:** {user.first_name} (ID: `{user.id}`)\n**Text:** `{text}`\n**Link:** `{link}`")
        await send_notification(notification_text)
    except Exception as e:
        log.error(f"Could not send link addition notification: {e}")
    await event.respond(f'✅ Link for "{text.strip()}" add ho gaya!', parse_mode='md')

@client.on(events.NewMessage(pattern=r'^/showchannels$'))
async def show_channels(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, "Used /showchannels")
    user_channels = user_data.get(str(event.sender_id), {}).get('channels', [])
    if user_channels:
        await event.respond('Aapke add kiye gaye channels:\n' + "\n".join([f"`{cid}`" for cid in user_channels]), parse_mode='md')
    else:
        await event.respond('Aapne abhi tak koi channel add nahi kiya hai.')

@client.on(events.NewMessage(pattern=r'^/showlinks$'))
async def show_links(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, "Used /showlinks")
    user_links = user_data.get(str(event.sender_id), {}).get('links', {})
    if user_links:
        await event.respond('Aapke add kiye gaye links:\n' + "\n".join([f'**{t}**: {l}' for t, l in user_links.items()]), parse_mode='md')
    else:
        await event.respond('Aapne abhi tak koi link add nahi kiya hai.')

@client.on(events.NewMessage(pattern=r'^/removechannel(\s+.*)?$'))
async def remove_channel(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, f"Used /removechannel command.")
    arg = event.pattern_match.group(1)
    if not arg or not arg.strip():
        await event.respond('**Galat Format!**\nSahi tarika: `/removechannel -100123456789`', parse_mode='md'); return
    try:
        channel_id = int(arg.strip())
        user_id_str = str(event.sender_id)
        user_channels = user_data.get(user_id_str, {}).get('channels', [])
        if channel_id in user_channels:
            user_channels.remove(channel_id)
            if user_data.get(user_id_str, {}).get('active_channel') == channel_id:
                user_data[user_id_str]['active_channel'] = None
            save_data(user_data, total_users)
            await event.respond(f'✅ Channel ID `{channel_id}` remove ho gaya!', parse_mode='md')
        else:
            await event.respond(f'⚠️ Channel ID `{channel_id}` aapki list mein nahi mila.', parse_mode='md')
    except ValueError:
        await event.respond('**Galat ID!**\nChannel ID ek number hona chahiye.', parse_mode='md')

@client.on(events.NewMessage(pattern=r'^/removelink(\s+.*)?$'))
async def remove_link(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, f"Used /removelink command.")
    text_to_remove = event.pattern_match.group(1)
    if not text_to_remove or not text_to_remove.strip():
        await event.respond('**Galat Format!**\nSahi tarika: `/removelink Your Text`', parse_mode='md'); return
    text_to_remove = text_to_remove.strip()
    user_id_str = str(event.sender_id)
    user_links = user_data.get(user_id_str, {}).get('links', {})
    if text_to_remove in user_links:
        del user_links[text_to_remove]
        save_data(user_data, total_users)
        await event.respond(f'✅ Link jiska text "{text_to_remove}" tha, remove ho gaya!', parse_mode='md')
    else:
        await event.respond(f'⚠️ "{text_to_remove}" text wala koi link nahi mila.', parse_mode='md')

@client.on(events.NewMessage(pattern=r'^/selectchannel(\s+.*)?$'))
async def select_channel(event):
    if not check_user_status(event.sender_id): await send_plan_selection_prompt(event); return
    await log_and_notify_activity(event, f"Used /selectchannel command.")
    arg = event.pattern_match.group(1)
    if not arg or not arg.strip():
        await event.respond('**Galat Format!**\nSahi tarika: `/selectchannel -100123456789`', parse_mode='md'); return
    try:
        channel_id = int(arg.strip())
        user_id_str = str(event.sender_id)
        user_channels = user_data.get(user_id_str, {}).get('channels', [])
        if channel_id in user_channels:
            user_data[user_id_str]['active_channel'] = channel_id
            save_data(user_data, total_users)
            await event.respond(f'✅ Channel `{channel_id}` ab active hai.', parse_mode='md')
        else:
            await event.respond(f'⚠️ Channel `{channel_id}` aapki list mein nahi hai. Pehle `/addchannel` use karein.', parse_mode='md')
    except ValueError:
        await event.respond('**Galat ID!**\nChannel ID ek number hona chahiye.', parse_mode='md')


# ==============================================================================
# === NAYA: PLAN SELECTION KE LIYE COMMAND HANDLERS ===
# ==============================================================================

# Yeh ek helper function hai taaki code repeat na ho.
async def handle_plan_selection(event, plan_details_text, duration_for_admin):
    """Admin ko notification bhejta hai aur user ko jawab deta hai."""
    user = await event.get_sender()
    username = f"@{user.username}" if user.username else 'N/A'
    
    await log_and_notify_activity(event, f"Selected plan: {plan_details_text}")

    # Admin ko notification
    admin_notification = (
        f"**💰 Subscription Plan Selected!**\n\n"
        f"**User:** {user.first_name} (ID: `{user.id}`)\n"
        f"**Username:** {username}\n"
        f"**Selected Plan:** {plan_details_text}\n\n"
        f"Activate with: `/activate {user.id} {duration_for_admin}`"
    )
    await send_notification(admin_notification)

    # User ko jawab
    user_response = (
        f"Aapne '{plan_details_text}' plan chuna hai. Kripya payment ke liye admin (@captain_stive) se sampark karein. "
        f"Payment ke waqt apni User ID zaroor batayein: `{event.sender_id}`"
    )
    await event.respond(user_response)

# In handlers mein `check_user_status` nahi hai taaki expired user bhi inko use kar sake.
@client.on(events.NewMessage(pattern=r'^/buy_1_month$'))
async def buy_1_month(event):
    await handle_plan_selection(event, "1 Mahina - ₹79", "1m")

@client.on(events.NewMessage(pattern=r'^/buy_4_months$'))
async def buy_4_months(event):
    await handle_plan_selection(event, "4 Mahine - ₹300", "4m")

@client.on(events.NewMessage(pattern=r'^/buy_1_year$'))
async def buy_1_year(event):
    await handle_plan_selection(event, "1 Saal - ₹600", "1y")


# ==============================================================================
# === NAYA: ADULT CONTENT FILTER AUR PRIVATE MESSAGE HANDLER ===
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: e.is_private and e.message.text and not e.message.text.startswith('/')))
async def handle_private_messages(event):
    """
    SUDHAR KIYA GAYA: Isme se plan selection ki purani logic hata di gayi hai.
    Yeh ab sirf adult content check karega.
    """
    # Sabse pehle user status check karein, agar trial khatam to prompt dikhayein.
    if not check_user_status(event.sender_id):
        await send_plan_selection_prompt(event)
        return

    # Agar user ka status theek hai, to adult content check karein.
    message_text_lower = event.text.lower()
    for keyword in ADULT_KEYWORDS:
        if keyword in message_text_lower:
            user = await event.get_sender()
            user_id_str = str(user.id)
            user_data[user_id_str]['is_blocked'] = True
            save_data(user_data, total_users)
            
            await send_notification(
                f"**🚨 ADULT CONTENT DETECTED & USER BLOCKED 🚨**\n\n"
                f"User ko **automatically block** kar diya gaya hai."
            )
            await event.respond(
                "**⚠️ WARNING & BLOCK ⚠️**\n\nAapko anuchit shabdon ke prayog ke kaaran block kar diya gaya hai."
            )
            return


# ==============================================================================
# === CORE FUNCTIONALITY (LINK ADD KARNA) ===
# ==============================================================================
@client.on(events.NewMessage(func=lambda e: e.is_channel and not e.text.startswith('/')))
async def add_links(event):
    for user_id_str, u_data in list(user_data.items()):
        if u_data.get('active_channel') == event.chat_id:
            # Yahan bhi check karein, agar user ka access nahi hai to link add na karein
            if not check_user_status(int(user_id_str)): continue
            
            message_text = event.message.text
            if not message_text: return
            
            message_text_lower = message_text.lower()
            user_links = u_data.get('links', {})
            
            link_to_add = []
            for text, link in user_links.items():
                if re.search(r'\b' + re.escape(text.lower()) + r'\b', message_text_lower):
                    link_to_add.append(link)
            
            if link_to_add:
                try:
                    final_text = f"{message_text}\n\n" + "\n".join(link_to_add)
                    await event.edit(final_text)
                    log.info(f"Edited message in {event.chat_id} for user {user_id_str}")
                except Exception as e:
                    log.error(f"Error editing in {event.chat_id}: {e}")
                return # Ek user ke liye edit karne ke baad loop se bahar aa jayein

# ==============================================================================
# === ADMIN COMMANDS (UPDATED & NEW) ===
# ==============================================================================

@client.on(events.NewMessage(pattern=r'^/totalusers$', from_users=ADMIN_ID))
async def total_users_command(event):
    await event.respond(f"Total users: {total_users}")

@client.on(events.NewMessage(pattern=r'^/broadcast(\s+.*)?$', from_users=ADMIN_ID))
async def broadcast_message(event):
    msg = event.pattern_match.group(1)
    if not msg or not msg.strip(): await event.respond("Usage: /broadcast <message>"); return
    sent, failed = 0, 0
    for uid in list(user_data.keys()):
        try:
            await client.send_message(int(uid), msg.strip(), parse_mode='md'); sent += 1
        except Exception as e:
            failed += 1; log.warning(f"Broadcast failed for {uid}: {e}")
    await event.respond(f"Broadcast complete.\nSent: {sent}\nFailed: {failed}")

@client.on(events.NewMessage(pattern=r'^/activate(\s+.*)?$', from_users=ADMIN_ID))
async def activate_user(event):
    args = event.pattern_match.group(1)
    if not args or not args.strip():
        await event.respond("Usage: /activate <user_id> <1m|4m|1y>"); return
    match = re.match(r'(\d+)\s+(\d+)([my])', args.strip().lower())
    if not match:
        await event.respond("Invalid format. Example: `/activate 12345 1m`"); return
    uid, val_str, unit = match.groups()
    if str(uid) not in user_data: await event.respond(f"User {uid} not found."); return
    val = int(val_str)
    end_date, txt = (datetime.now() + timedelta(days=val*30), f"{val} mahine") if unit == 'm' else (datetime.now() + timedelta(days=val*365), f"{val} saal")
    user_data[str(uid)].update({'is_paid': True, 'is_blocked': False, 'subscription_end_date': end_date.isoformat(), 'trial_end_date': None})
    save_data(user_data, total_users)
    await event.respond(f"✅ User {uid} activated for {txt}.")
    await send_notification(f"**Admin Action:** Activated user `{uid}` for {txt}.")
    try: await client.send_message(int(uid), f"✅ Mubarak ho! Aapka account **{txt}** ke liye activate ho gaya hai.")
    except Exception as e: await event.respond(f"Couldn't notify user. Error: {e}")

@client.on(events.NewMessage(pattern=r'^/settrial(\s+.*)?$', from_users=ADMIN_ID))
async def set_trial(event):
    args = event.pattern_match.group(1)
    if not args or not args.strip():
        await event.respond("Usage: `/settrial <user_id> <duration>`\nExample: `/settrial 12345 30s`\nUnits: `s`, `m`, `h`, `d`"); return
    match = re.match(r'(\d+)\s+(\d+)([smhd])', args.strip().lower())
    if not match:
        await event.respond("Invalid format. Example: `/settrial 12345 30s` (30 seconds)"); return
    uid_str, value_str, unit = match.groups()
    if uid_str not in user_data: await event.respond(f"User {uid_str} not found."); return
    value = int(value_str)
    now, duration_text = datetime.now(), ""
    if unit == 's': new_end_date, duration_text = now + timedelta(seconds=value), f"{value} second"
    elif unit == 'm': new_end_date, duration_text = now + timedelta(minutes=value), f"{value} minute"
    elif unit == 'h': new_end_date, duration_text = now + timedelta(hours=value), f"{value} ghante"
    elif unit == 'd': new_end_date, duration_text = now + timedelta(days=value), f"{value} din"
    user_data[uid_str].update({'trial_end_date': new_end_date.isoformat(), 'is_blocked': False, 'is_paid': False})
    save_data(user_data, total_users)
    await event.respond(f"✅ User `{uid_str}` ka trial **{duration_text}** ke liye set kar diya gaya hai.")
    await send_notification(f"**Admin Action:** Set trial for user `{uid_str}` for **{duration_text}**.")
    try:
        await client.send_message(int(uid_str), f"🔔 Aapka trial period badal diya gaya hai. Ab aap bot ko agle **{duration_text}** tak istemal kar sakte hain.")
    except Exception as e: await event.respond(f"User ko notify nahi kar paya. Error: {e}")

@client.on(events.NewMessage(pattern=r'^/block(\s+.*)?$', from_users=ADMIN_ID))
async def block_user(event):
    uid = event.pattern_match.group(1)
    if not uid or not uid.strip().isdigit(): await event.respond("Usage: /block <user_id>"); return
    if uid.strip() in user_data:
        user_data[uid.strip()]['is_blocked'] = True; save_data(user_data, total_users)
        await event.respond(f"🚫 User {uid.strip()} blocked.")
        await send_notification(f"**Admin Action:** Blocked user `{uid.strip()}`.")
    else: await event.respond(f"User {uid.strip()} not found.")

@client.on(events.NewMessage(pattern=r'^/unblock(\s+.*)?$', from_users=ADMIN_ID))
async def unblock_user(event):
    uid = event.pattern_match.group(1)
    if not uid or not uid.strip().isdigit(): await event.respond("Usage: /unblock <user_id>"); return
    if uid.strip() in user_data:
        user_data[uid.strip()]['is_blocked'] = False; save_data(user_data, total_users)
        await event.respond(f"✅ User {uid.strip()} unblocked.")
        await send_notification(f"**Admin Action:** Unblocked user `{uid.strip()}`.")
    else: await event.respond(f"User {uid.strip()} not found.")


# ==============================================================================
# === BOT KO START KARNA ===
# ==============================================================================
async def main():
    print("Bot is running... Subscription system updated.")
    log.info("Bot started successfully. Subscription system updated.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
