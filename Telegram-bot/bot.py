import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, CSV_FILE

# --- Load dữ liệu CSV ---
def load_data():
    try:
        return pd.read_csv(CSV_FILE, sep='\t')
    except FileNotFoundError:
        return pd.DataFrame(columns=["PLU CODE", "PLU NAME", "Price"])

# --- Tìm sản phẩm theo PLU ---
def search_by_plu(plu_code):
    data = load_data()
    result = data[data["PLU CODE"].astype(str) == str(plu_code)]
    if result.empty:
        return "❌ Không tìm thấy sản phẩm."
    row = result.iloc[0]
    return f"📦 {row['PLU NAME']}\n💰 Giá: {row['Price']} VND"

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Chào bạn!\n"
        "- Upload file CSV để cập nhật dữ liệu.\n"
        "- Nhập mã PLU để tra cứu giá.\n"
        "- Gõ /check để xem số sản phẩm hiện có."
    )

# --- /check ---
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    count = len(data)
    if count == 0:
        await update.message.reply_text("⚠️ Hiện chưa có sản phẩm nào.")
    else:
        await update.message.reply_text(f"📦 Hiện có {count} sản phẩm trong file CSV.")

# --- Xử lý khi upload file ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    await file.download_to_drive(CSV_FILE)
    try:
        data = pd.read_csv(CSV_FILE)
        await update.message.reply_text(f"✅ File CSV đã được cập nhật! Có {len(data)} sản phẩm.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi đọc file: {e}")
        

 # --- /add Ten san pham |Gia ---
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = " ".join(context.args)
        name, price = text.split("|")
        global data
        new_row = {"ProductName": name.strip(), "Price": price.strip()}
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        data.to_csv("141PLUcan.csv", index=False)
        await update.message.reply_text(f"✅ Đã thêm {name.strip()} - {price.strip()}")
    except:
        await update.message.reply_text("❌ Sai cú pháp. Dùng: /add Tên sản phẩm | Giá")

# Thêm vào main()
application.add_handler(CommandHandler("add", add_product))
# --- Xử lý nhập mã PLU ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    reply = search_by_plu(code)
    await update.message.reply_text(reply)

# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
