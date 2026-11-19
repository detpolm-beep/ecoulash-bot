# 🌿 EcoUlash Telegram Bot

EcoUlash ijtimoiy-ekologik loyihasi uchun zamonaviy Telegram bot.

## 📋 Funksiyalar

### Foydalanuvchilar uchun:
- ♻️ **Ehson qilish** — Buyum ehson qilish
- 🤲 **Yordam so'rash** — Kerakli buyumni so'rash
- 📦 **Mavjud buyumlar** — Ehson qilingan buyumlarni ko'rish
- 🙋 **Ko'ngilli bo'lish** — Jamoaga qo'shilish
- 📊 **Statistika** — Loyiha statistikasini ko'rish

### Adminlar uchun:
- 📢 **Broadcast** — Barcha foydalanuvchilarga xabar yuborish
- 👥 **Foydalanuvchilar** — Ro'yxatni ko'rish
- 🎁 **Ehsonlar** — Ehsonlarni boshqarish
- 📋 **So'rovlar** — Yordam so'rovlarini ko'rish
- 📊 **Batafsil statistika**

## 🚀 O'rnatish

### 1. Talablarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. .env faylini sozlash
```bash
cp .env.example .env
```
`.env` faylini oching va:
- `BOT_TOKEN` — BotFather dan olgan yangi token
- `ADMIN_IDS` — Sizning Telegram ID ingiz

### 3. Botni ishga tushirish
```bash
python main.py
```

## 📁 Loyiha tuzilmasi

```
ecoulash-bot/
├── main.py              # Asosiy fayl
├── requirements.txt     # Kutubxonalar
├── .env                 # Sozlamalar (git ga tushmaydi)
├── handlers/            # Handlerlar
│   ├── start.py         # /start, haqida, aloqa
│   ├── donation.py      # Ehson qilish
│   ├── request.py       # Yordam so'rash
│   ├── volunteer.py     # Ko'ngilli
│   ├── items.py         # Mavjud buyumlar
│   ├── stats.py         # Statistika
│   └── admin.py         # Admin panel
├── database/
│   └── db.py            # SQLite ma'lumotlar bazasi
├── keyboards/
│   └── main_kb.py       # Tugmalar
└── utils/
    └── config.py        # Konfiguratsiya
```

## ⚠️ Muhim

Tokeningizni hech qachon ommaviy joylarda ko'rsatmang.
Agar token sizib chiqqan bo'lsa, BotFather orqali darhol yangilang:
`/mybots → Tokeningizni tanlang → API Token → Revoke current token`
