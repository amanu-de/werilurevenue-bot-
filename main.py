
import telebot
from telebot import types
import time
import os

# 1. ቶክን እና አስተዳዳሪ መታወቂያ
TOKEN = '8060609986:AAH0HhnaesBSHIVkoac_KrU2rbEmjHjB0As'
ADMIN_ID = 5334673990 
bot = telebot.TeleBot(TOKEN)

user_state = {}
USER_LIST_FILE = "users.txt"

# --- ተጠቃሚዎችን ለመመዝገብና ለመቁጠር ---
def save_user(uid):
    if not os.path.exists(USER_LIST_FILE):
        with open(USER_LIST_FILE, "w") as f: f.write("")
    with open(USER_LIST_FILE, "r") as f:
        users = f.read().splitlines()
    if str(uid) not in users:
        with open(USER_LIST_FILE, "a") as f:
            f.write(f"{uid}\n")

def get_user_count():
    if not os.path.exists(USER_LIST_FILE): return 0
    with open(USER_LIST_FILE, "r") as f:
        return len(f.read().splitlines())

# --- የቁልፍ ሰሌዳዎች (ዋና ማውጫ) ---
def main_menu_am():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💰 በገቢ አሰባሰብ", "🏢 የደንበኞች አገልግሎት", 
               "🗓 የግብር ወቅቶች", "📍 አድራሻ እና ስለእኛ", 
               "📢 የቅሬታ ጥቆማና አስተያየት", "📊 የቦቱ ጥቅሞች")
    return markup

# --- ሰላምታ ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    welcome_text = (
        "<b>እንኳን ወደ ወረኢሉ ወረዳ ገቢዎች መረጃ ቦት በሰላም መጡ!</b> 🇪🇹\n\n"
        "ይህ ቦት ፈጣን መረጃ እንዲያገኙና ቅሬታዎችን በቀላሉ ለማድረስ ታስቦ የተዘጋጀ ነው።\n"
        "<b>እባክዎ ከታች ካሉት አማራጮች የሚፈልጉትን ይምረጡ።</b> 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_menu_am())

# --- 🔄 የአስተዳዳሪ መልስ ለደንበኛው ---
@bot.message_handler(func=lambda message: message.reply_to_message is not None and message.chat.id == ADMIN_ID)
def reply_to_user(message):
    try:
        original_msg = message.reply_to_message.text or message.reply_to_message.caption
        if "ID:" in original_msg:
            user_id = int(original_msg.split("ID:")[1].strip())
            bot.send_message(user_id, f"✅ <b>ከወረኢሉ ወረዳ ገቢዎች የተሰጠ ምላሽ፦</b>\n\n{message.text}", parse_mode="HTML")
            bot.send_message(ADMIN_ID, "✅ መልስዎ ለደንበኛው ደርሷል።")
    except Exception:
        bot.send_message(ADMIN_ID, "❌ ስህተት፦ መልሱን መላክ አልተቻለም።")

# --- ዋና የመልዕክት ማስተናገጃ ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'audio'])
def handle_all_messages(message):
    cid = message.chat.id
    txt = message.text
    save_user(cid)

    # --- 1. የቅሬታ ጥቆማና አስተያየት መቀበያ ---
    if user_state.get(cid) == 'waiting_feedback':
        if txt == "🔙 ወደ ኋላ":
            user_state[cid] = None
            bot.send_message(cid, "ተመልሰዋል", reply_markup=main_menu_am())
            return
        
        user_info = f"\n\nFrom: {message.from_user.first_name}\nID:{cid}"
        if message.content_type == 'text':
            bot.send_message(ADMIN_ID, f"📢 <b>አዲስ ጥቆማ፦</b>\n{txt}{user_info}", parse_mode="HTML")
        elif message.content_type == 'photo':
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📢 አዲስ የፎቶ ጥቆማ{user_info}")
        elif message.content_type in ['voice', 'audio']:
            file_id = message.voice.file_id if message.voice else message.audio.file_id
            bot.send_voice(ADMIN_ID, file_id, caption=f"📢 አዲስ የድምፅ ጥቆማ{user_info}")
            
        bot.send_message(cid, "✅ <b>እናመሰግናለን!</b> የሰጡን ሀሳብና ጥቆማ ደርሶናል፤ አግባብነት ካለው ምላሽ የምንሰጥበት ይሆናል።", parse_mode="HTML", reply_markup=main_menu_am())
        user_state[cid] = None
        return

    # --- 2. ዋና ዋና ምርጫዎች ---
    if txt == "🔙 ወደ ኋላ":
        bot.send_message(cid, "🏠 ወደ ዋናው ማውጫ ተመልሰዋል", reply_markup=main_menu_am())

    elif txt == "💰 በገቢ አሰባሰብ":
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("🏢 የቫት መረጃ", "📜 የቴምብር አገልግሎት", "🏠 ስመ ንብረት", "🛑 ንግድ ፈቃድ መዝጋት", "🔙 ወደ ኋላ")
        bot.send_message(cid, "📋 <b>የገቢ አሰባሰብ አገልግሎቶችን ይምረጡ፦</b>", parse_mode="HTML", reply_markup=markup)

    elif txt == "🏢 የቫት መረጃ":
        info = (
            "💰 <b>የቫት (VAT) መረጃ</b>\n\n"
            "ውድ ደንበኛችን! በወረዳችን የቫት ተመዝጋቢ ለመሆን ወይም መረጃ ለማግኘት የሚከተሉት ነጥቦች ተፈጻሚ ይሆናሉ፦\n\n"
            "🔹 ዓመታዊ የሽያጭ መጠናቸው <b>2,000,000 (ሁለት ሚሊዮን) ብር</b> እና በላይ የሆኑ ነጋዴዎች በቫት የመመዝገብ ግዴታ አለባቸው።\n"
            "🔹 በቫት የተመዘገቡ ደንበኞች በየወሩ ከመስከረምን ከጥቅምት 1-30 የጥቅምትን ከህዳር 1-30 እስከየ ወሩ መጨረሻ ቀን ድረስ የሂሳብ ሪፖርት ማቅረብ እና ካለም ክፍያ መፈጸም ይጠበቅባቸዋል።\n"
            "🔹 ሽያጭ ሲያከናውኑ ህጋዊ የቫት ደረሰኝ መቁረጥ ግዴታ ነው።\n"
            "🔹 አመታዊ ሂሳባቸዉንም <b>ከጥቅምት 1-30</b> ድረስ ማቅረብ ይጠበቅባቸዋል።"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "📜 የቴምብር አገልግሎት":
        info = (
            "<b>📜 የቴምብር አገልግሎት</b>\n\n"
            "ውድ ደንበኛችን! የቴምብር አገልግሎት በወረዳችን ፍትህ ጽሕፈት ቤት ላሉ አገልግሎቶች ለማግኘት የሚጠቅም ነው።\n\n"
            "🔸 <b>ለውክልና አገልግሎት፦</b> ወደ ፍትህ በመሄድ የውክልና አገልግሎት ማግኘት የሚፈልጉ ከሆነ ከእኛ ጋር የ 35 ብር ቴምብር መግዛትና በፋይናንስ ተቋም የ 100 ብር አገልግሎት ክፍያን መክፈል ይጠበቅቦታል፤\n"
            "🔸 <b>ለሌሎች አገልግሎቶች፦</b> ለማገጃ፣ ለማስከበሪያ፣ ኑዛዜ፣ ቃለ መሐላ፣ የስምምነት ውል፣ የቤት ሽያጭ፣ ወይም የስጦታ ውል አገልግሎቶች ከፈለጉ ከእኛ ጋር የ 5 ብር ቴምብር ይገዛሉ፤\n"
            "🔸 እንደየ አገልግሎቱ ዓይነት ወደ ፋይናንስ ተቋም በመሄድ የአገልግሎት ክፍያ በመክፈል አገልግሎቱን ማግኘት ይችላሉ።"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "🏠 ስመ ንብረት":
        info = (
            "<b>🏠 ስመ ንብረት አገልግሎት ለማግኘት</b>\n\n"
            "📍 በቅድሚያ በአቅራቢያዎ ወደሚገኝ ወደ <b>ማዘጋጃ ቤት</b> በመሄድ ግምት ማስገመት ይጠበቅቦታል።\n"
            "📍 ግምቱን ካስገመቱ በኅላ ከማዘጋጃ ቤቱ የተሰጠዎትን ደብዳቤ ወደ አቅራቢያዎ ወይም በደብዳቤዉ ወደተገለፀዉ የፍትህ ተቋም ይዘዉ ይሄዳሉ።\n\n"
            "📍 የማዘጋጃ ቤት የተፃፈለዎትን ደብዳቤ ወደ ፍትህ ተቋሙ ከዳረሱ በኅላ ከፍትህ የሚፃፈዉን ደብዳቤ በመያዝ ወደ ተቋማችን ገቢዎች ሲመጡም ደብዳቤዉን ብቻ ሳይሆን <b>የቤቱን ካርታና ፕላን</b> አንድ ኮፒ በማድረግ ይዘዉ መምጣት ይጠበቅቦታል።\n\n"
            "🤝 <b>ስለመረጡን እናመሰግናለን</b>"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "🛑 ንግድ ፈቃድ መዝጋት":
        info = (
            "<b>🛑 የንግድ ፈቃድ መዝጋት</b>\n\n"
            "🔹 የንግድ ፈቃድ ለመዝጋት ቀጥታ መጥተዉ የገቢ አሰባሰብ የሰራ ሂደት ጋር በመግባት <b>የአወሳሰን ባለሙያዎችን</b> ማግኘት ይጠበቅቦታል።\n"
            "🔹 ቀድመዉ ግን ከቤትዎ ሲመጡ ፈቃዱን መዝጋት የሚፈልጉበትን አሳማኝ ምክነያት በማመልከቻ መግለፅ።\n\n"
            "🔹 ፈቃዱን ሊመልሱ ወይም ሊዘጉ ሲመጡ ከድመዉ ከቢሯችን የወሰዱትን <b>የቲን ነበር (TIN) ኦርጅናሉንና የዘመኑን የታደሰ ፈቃድ</b> ይዘዉ መምጣት ይጠበቅቦታል። ይህን የምናደርገዉም አቁሚያለሁ ብለው በመስራቶ እርሶ ወንጀለኛ እንዳያደርግ ነዉ።\n\n"
            "🔹 ከመዝጋቶ በፊት የሩብ አመት ግብርዎን በሲስተም ወይም በባንክ ከከከፈሉ የሲስተሙን ደረሰኝ መያዝ፤ በእጅ ቢሮ መጥተዉ ከከከፈሉም ደረሰኞን መያዝ ይጠበቅቦታል።\n\n"
            "🔹 ያለበዎት የግብር እዳ ካለ እሱን መጨረስ ይጠበቅቦታል፤ ከዚያም የሚፈልጉትን አገልግሎት በታማኝነት እናገለግሎታለን።\n\n"
            "🙏 <b>እኛን ስለመረጡ እናመሰግናለን</b>"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "🏢 የደንበኞች አገልግሎት":
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("🆔 አዲስ ቲን (TIN)", "📄 የታክስ ክሊራንስ አገልግሎት", "⚖️ የግብር ይግባኝ", "✏️ የመረጃ ለውጥ", "🔙 ወደ ኋላ")
        bot.send_message(cid, "👤 <b>የደንበኞች አገልግሎት ምርጫዎች፦</b>", parse_mode="HTML", reply_markup=markup)

    elif txt == "📄 የታክስ ክሊራንስ አገልግሎት":
        info = (
            "<b>📄 የታክስ ክሊራንስ አገልግሎት</b>\n\n"
            "ውድ ደንበኛችን የክሊራንስ አገልግሎት ለማግኘት ወይም የፈቃድ እድሳት ለማድረግ በአመቱ መጨረሻ ከእኛ ተቋም የእድሳት ክሊራንስ መዉሰድ ይጠበቅቦታል።\n\n"
            "✅ ለዚህም ቀጥታ እንደመጡ የደንበኛ አገልግሎት ቢሮ በመግባት የምዝገባ ስረዛ ባለሙያዉን የእድሳት ክሊራንስ ለመዉሰድ እንደመጡ በመንገር አገልግሎቱን ማግኘት ይችላሉ።\n\n"
            "⚠️ <b>ሲመጡም የሚከተሉትን ማሟላት ይጠበቅቦታል፦</b>\n"
            "• በየሩብ አመት የከፈሉበትን የሩብ አመት መረጃ በሲስተም ከሆነ የባንክም ደረሰኙን ማምጣት።\n"
            "• በደረሰኝም ከሆነ የከፈሉት እርሶ ጋ ያለዉን ነጭ ደረሰኝ በመያዝ ፋይሎን በማዉጣት አገልግሎቱን ማግኘት ይችላሉ።"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "⚖️ የግብር ይግባኝ":
        info = (
            "<b>⚖️ የግብር ይግባኝ አገልግሎት</b>\n\n"
            "የግብር በዛብኝ ቅሬታና የቀን ገቢ ጥናት በዛብኝ ቅሬታን አገልግሎት ለማቅረብ የሚፈልጉ ከሆነ ችግሮን ወይም አሳማኝ ምክነያቶን በመያዝ ቀጥታ ወደ ቢሮዋችን በመምጣት ወደ <b>ደንበኛ አገልግሎት ቢሮ</b> በመቅረብ ያለዉን ችግር የቅሬታ ፎርሞን በመቀበል ቅሬታዎን በሚገባ ማቅረብና ለቅሬታዎም መልስ መሰጠትና አለመሰጠቱን መጠየቅ የሚችሉ መሆኑን እንገልፃለን።\n\n"
            "🤝 <b>ስለመረጡን እናመሰግናለን</b>"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "🆔 አዲስ ቲን (TIN)":
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("የነጋዴ ቲን ለማግኘት", "የመንግስት ሰራተኛ ለማግኘት", "የተማሪ ቲን ለማግኘት", "የማህበር ቲን ለማዉጣት", "🔙 ወደ ኋላ")
        bot.send_message(cid, "🪪 <b>የቲን (TIN) ዓይነት ይምረጡ፦</b>", parse_mode="HTML", reply_markup=markup)

    elif txt == "የነጋዴ ቲን ለማግኘት":
        info = (
            "<b>💼 የነጋዴ ቲን ነበር ለማዉጣት፦</b>\n\n"
            "✅ የብሔራዊ ዲጅታል መታወቂያ ካርድ ይዞ መምጣት\n"
            "✅ የብሔራዊ ዲጅታል መታወቂያ ያዝመዘገቡበትን ስልክ\n"
            "✅ ከሚኖሩበት አካባቢ የቀበሌ መታወቂያ\n"
            "✅ ከሚኖሩበት አካባቢ የቀበሌ ማረጋገጫ ወረቀት\n"
            "✅ ሁለት ጉርድ ፎቶ\n"
            "✅ ሁለት ክላሴር ይዘዉ በመምጣት አገልግሎት ማግኘት ይችላሉ"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "የመንግስት ሰራተኛ ለማግኘት" or txt == "የተማሪ ቲን ለማግኘት":
        role = "የመንግስት ሰራተኛ" if "ሰራተኛ" in txt else "የተማሪ"
        info = (
            f"<b>🎓 {role} ቲን ነበር ለማዉጣት፦</b>\n\n"
            "✅ የብሔራዊ ዲጅታል መታወቂያ ካርድ ይዞ መምጣት\n"
            "✅ የብሔራዊ ዲጅታል መታወቂያ ያዝመዘገቡበትን ስልክ ቁጥር እና ስልክ\n"
            "✅ የቀበሌ መታወቂያ ካርድ\n"
            "✅ አንድ ኮፒ የተደረገ የቀበሌ መታወቂያ ይዘዉ መምጣት"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "የማህበር ቲን ለማዉጣት":
        info = (
            "<b>👥 የማህበር ቲን ነበር ለማዉጣት፦</b>\n\n"
            "✅ ከደሴ የፀደቀዉን የማህበር ስም የያዘ መረጃ መያዝ\n"
            "✅ የማህበሩን ሽርክና ወረቀት መያዝ\n"
            "✅ የማህበሩ ስራ አስኪያጅ ሊኖር ይገባል ፈቃዱን ሲያወጣ\n"
            "✅ የማህበሩ ስራ አስኪያጅ ሁለት ጉርድ ፎቶ"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "🗓 የግብር ወቅቶች":
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("የደረጃ 'ሀ' የግብር መክፈያ ወቅቶች", "የደረጃ 'ለ' የግብር መክፈያ ወቅቶች", "🔙 ወደ ኋላ")
        bot.send_message(cid, "🗓 <b>የግብር ከፋይ ደረጃዎን ይምረጡ፦</b>", parse_mode="HTML", reply_markup=markup)

    elif txt == "የደረጃ 'ሀ' የግብር መክፈያ ወቅቶች":
        info = (
            "<b>📑 የደረጃ 'ሀ' ግብር መክፈያ ወቅቶች</b>\n\n"
            "የደረጃ 'ሀ' ግብር ከፋይ ማለት አመታዊ ግብይታቸዉ ከሁለት ሚሊየን ብር በላይ የሆነ፣ የሂሳብ መዝገብ የሚይዙ የመያዝም ግዴታ ያለባቸዉ፣ ግብይታቸዉ በሙሉ በደረሰኝ የሚጠቀሙ በየወሩ የቫት ሪፓርት የሚያቀርቡ ናቸዉ።\n"
            "አመታዊ የሂሳብ የሚያሳዉቁት <b>ከጥቅምት አንድ እስከ ጥቅምት ሰላሳ</b> ነዉ።\n\n"
            "✅ <b>የ1ኛ ሩብ አመት፦</b> መክፈያ ወቅት <b>ከየካቲት 1-30</b> (ከሀምሌ 1 እስከ መስከረም 30 ያለዉ የስራ ሰዓት)\n"
            "✅ <b>የ2ኛ ሩብ አመት፦</b> መክፈያ ወቅት <b>ከግንቦት 1-30</b> (ከጥቅምት 1 እስከ ታህሳስ 30 ያለዉ የስራ ሰዓት)\n"
            "✅ <b>የ3ኛ ሩብ አመት፦</b> መክፈያ ወቅት <b>ከነሀሴ 1-30</b> (ከጥር 1 እስከ መጋቢት 30 ያለዉ የስራ ሰዓት)\n"
            "✅ <b>የ4ኛ ሩብ አመት፦</b> መክፈያ ወቅት <b>ከጥቅምት 1-30</b> (ከሚያዚያ 1 እስከ ሰኔ 30 ያለዉ የስራ ሰዓት)\n\n"
            "🏢 <b>የወረኢሉ ወረዳ ገቢዎች</b>\n🤝 ስለመረጡን እናመሰግናለን"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "የደረጃ 'ለ' የግብር መክፈያ ወቅቶች":
        info = (
            "<b>📑 የደረጃ 'ለ' ግብር መክፈያ ወቅት</b>\n\n"
            "የደረጃ 'ለ' ግብር ከፋይች ማለት አመታዊ ግብይታቸዉ ከሁለት ሚሊዮን ብር የሚያንስ ነዉ።\n\n"
            "✅ <b>የ1ኛ ሩብ አመት፦</b> መክፈያ ግዜ <b>ከህዳር 1-30</b> (ከሀምሌ 1 እስከ መስከረም 30 ያለዉ የስራ ሰዓት)\n"
            "✅ <b>የ2ኛ ሩብ አመት፦</b> መክፈያ ግዜ <b>ከየካቲት 1-30</b> (ከጥቅምት 1 እስከ ታህሳስ 30 ያለዉ የስራ ሰዓት)\n"
            "✅ <b>የ3ኛ ሩብ አመት፦</b> መክፈያ ግዜ <b>ከግንቦት 1-30</b> (ከጥር 1 እስከ መጋቢት 30 ያለዉ የስራ ሰዓት)\n"
            "✅ <b>የ4ኛ ሩብ አመት፦</b> መክፈያ ግዜ <b>ከሀምሌ 1-30</b> (ከሚያዚያ 1 እስከ ሰኔ 30 ያለዉ የስራ ሰዓት)\n\n"
            "🏢 <b>የወረኢሉ ወረዳ ገቢዎች</b>\n🤝 ስለመረጡን እናመሰግናለን"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "📊 የቦቱ ጥቅሞች":
        count = get_user_count()
        info = (
            f"<b>📊 የቦቱ አጠቃቀምና ጥቅሞች</b>\n\n"
            f"👥 እስካሁን ቦቱን <b>{count} ሰዎች</b> ተጠቅመውታል።\n\n"
            f"🌟 <b>ዋና ዋና ጥቅሞች፦</b>\n"
            f"✅ <b>ጊዜን መቆጠብ፦</b> መረጃ ለማግኘት ቢሮ መመላለስ ሳይጠበቅቦት ባሉበት ሆነው ያገኛሉ።\n"
            f"✅ <b>ግልጽነት፦</b> ስለ ግብር መክፈያና ቲን (TIN) አወጣጥ በቂ ግንዛቤ ይሰጣል።\n"
            f"✅ <b>ቀጥተኛ ግንኙነት፦</b> ቅሬታዎችን በቀጥታ ለሀላፊዎች ያደርሳል።\n"
            f"✅ <b>ወጪ መቀነስ፦</b> የወረቀትና የትራንስፖርት ወጪን ይቀንሳል።\n\n"
            f"🚀 <b>በቴክኖሎጂ የታገዘ የወረኢሉ ወረዳ ገቢዎች አገልግሎት!</b>"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "📍 አድራሻ እና ስለእኛ":
        info = (
            "<b>📍 አድራሻችን፦</b>\n"
            "ከወረኢሉ እግርኳስ ሜዳ ገባ ብሎ ሲቪል ሰርቪስ ግቢ ዉስጥ ያገኙናል።\n"
            "📞 <b>ስልክ፦</b> 0331160514\n\n"
            "<b>👨‍💻 የቦቱ አዘጋጅ፦</b> አማኑኤል ተፈራ በቀለ\n"
            "📱 <b>ለበለጠ መረጃ፦</b> 0975847071\n\n"
            "🚀 <b>የወረኢሉ ወረዳ ገቢዎች አንድ እርምጃ ወደፊት!</b>"
        )
        bot.send_message(cid, info, parse_mode="HTML")

    elif txt == "📢 የቅሬታ ጥቆማና አስተያየት":
        user_state[cid] = 'waiting_feedback'
        info = (
            "<b>📢 ውድ ደንበኛችን!</b>\n\n"
            "ይህ የሚሰጡን የቅሬታ እና የጥቆማ የአስተያየት አገልግሎት በቀጥታ ለሀላፊ እና ለሰዉ ሀብት አስተዳደሩ ለሚመለከተዉ አካል ብቻ የሚደርስ መሆኑን ከወዲሁ አዉቀዉ በነፃነት ሀሳብ መስጠት ይችላሉ።\n\n"
            "ጥቆማዉ ህገወጥ ነጋዴዎችን ጭምር ያካተተ ማድረግም ይችላሉ ይህም ጥሩ የንግድ ስርአትን ለመዘርጋት ይጠቅመናልና የሚሰጡት ሀሳብና ጥቆማም አገልግሎታችን የበለጠ ለማሻሻል ይረዳናል።\n\n"
            "✍️ <b>እባክዎ ቅሬታዎን ወይም ጥቆማዎን እዚህ ይጻፉ (ወይም በፎቶ/በድምፅ ይላኩ)፦</b>"
        )
        bot.send_message(cid, info, parse_mode="HTML")

# --- ቦቱን ማስነሻ ---
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception:
            time.sleep(5)
