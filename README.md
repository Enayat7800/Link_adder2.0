Telegram Link Adder Bot
Yeh ek advanced Telegram bot hai jo aapke dwara set kiye gaye channel messages mein keywords ke aadhar par automatically links jod deta hai. Ismein user management, subscription system, aur ek powerful admin panel bhi hai.
✨ Features (Visheshtayein)
Automatic Link Insertion: Channel mein bheje gaye messages mein keywords ko detect karke unse jude links ko automatically jod deta hai.
Subscription & Trial System: Users ke liye default 7-din ka trial. Admin custom trial (seconds, minutes, hours, days) ya paid subscription (mahine, saal) set kar sakta hai.
Command-Based Plan Selection: Trial khatam hone par, users ko naye plan select karne ke liye commands dikhai jaati hain.
Powerful Admin Panel: Admin users ko broadcast message bhej sakte hain, unka subscription activate kar sakte hain, trial set kar sakte hain, aur unhe block/unblock kar sakte hain.
Admin Notifications: Jab bhi koi naya user join karta hai, koi link add karta hai, ya koi plan select karta hai, to admin ko ek private channel mein notification milta hai.
Adult Content Filter: Anuchit (adult) shabdon ka istemal karne par user ko automatically block kar deta hai.
Multi-Channel Support: Har user apne multiple channels ko manage kar sakta hai.
⚙️ Setup and Installation (Set-up aur Sthaapna)
Bot ko apne server ya local machine par set up karne ke liye in steps ko follow karein.
Prerequisites (Aavashyaktaayein)
Python 3.8 ya usse naya version.
pip (Python package installer).
1. Repository Clone Karein
Generated bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Use code with caution.
Bash
2. Dependencies Install Karein
Bot ko chalane ke liye telethon library ki zaroorat hai.
Generated bash
pip install telethon
Use code with caution.
Bash
3. Telegram API Credentials Prapt Karein
API ID aur API HASH ke liye my.telegram.org par jaayein, login karein, aur "API development tools" section mein ek app banayein.
4. Telegram Bot Banayein
Telegram par @BotFather se baat karein.
/newbot command ka istemal karke ek naya bot banayein.
BotFather aapko ek BOT TOKEN dega. Ise surakshit rakhein.
5. Environment Variables Set Karein
Bot ko sahi se kaam karne ke liye in environment variables ki zaroorat hai. Aap inhe apne hosting environment (Heroku, Railway, etc.) mein set kar sakte hain ya ek .env file bana sakte hain.
API_ID: Aapka Telegram App API ID.
API_HASH: Aapka Telegram App API Hash.
BOT_TOKEN: @BotFather se mila aapka bot token.
ADMIN_ID: Aapki Telegram User ID (yeh bot ka admin hoga). Aap apni ID @userinfobot se prapt kar sakte hain.
NOTIFICATION_CHANNEL_ID: Ek private channel ki ID jahaan admin ko saari notifications milengi.
Ek private channel banayein.
Apne bot ko us channel ka admin banayein (messages post karne ki permission ke saath).
Channel se koi bhi message kisi dusre bot jaise @userinfobot par forward karein, wahan se aapko channel ki ID mil jaayegi (e.g., -100123456789).
🚀 Bot Ko Chalayein
Saari configuration set karne ke baad, is command se bot ko start karein:
Generated bash
python bot.py
Use code with caution.
Bash
(Yahaan bot.py aapki Python file ka naam hai)
📝 Commands
User Commands
/start - Bot ko start karein aur 7-din ka trial paayein.
/allcommands - Sabhi uplabdh commands ki list dekhein.
/help - Support ke liye admin se sampark karein.
/addchannel <channel_id> - Link jodne ke liye ek naya channel add karein. (e.g., /addchannel -100123...)
/addlink <text> <link> - Ek naya keyword aur usse juda link add karein. (e.g., /addlink Join Now https://t.me/...)
/showchannels - Aapke dwara add kiye gaye sabhi channels dekhein.
/showlinks - Aapke dwara add kiye gaye sabhi links dekhein.
/removechannel <channel_id> - List se ek channel hatayein.
/removelink <text> - Keyword ke aadhar par ek link hatayein.
/selectchannel <channel_id> - Messages mein link jodne ke liye ek channel ko active karein.
/deselectchannel - Active channel ko deselect karein.
Subscription Commands (Trial Khatam Hone Par)
/buy_1_month - 1 mahine ka plan chunein.
/buy_4_months - 4 mahine ka plan chunein.
/buy_1_year - 1 saal ka plan chunein.
Admin Commands (Sirf Admin Ke Liye)
/totalusers - Bot ke कुल users ki sankhya dekhein.
/broadcast <message> - Sabhi users ko ek message bhejein.
/activate <user_id> <duration> - User ka subscription activate karein. (e.g., /activate 12345 1m or /activate 12345 1y)
/settrial <user_id> <duration> - Kisi user ke liye custom trial period set karein. (e.g., /settrial 12345 30s, 5m, 2h, 5d)
/block <user_id> - Kisi user ko bot istemal karne se block karein.
/unblock <user_id> - Kisi user ko unblock karein.
💾 Data Storage
User ka saara data (channels, links, subscription status) bot_data.json naam ki file mein store hota hai. Yeh file bot ke chalne par automatically ban jaati hai. Kripya is file ko delete na karein.
44.0s
Start typing a prompt
