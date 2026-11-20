from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="♻️ Ehson qilish"),
        KeyboardButton(text="🤲 Yordam so'rash")
    )
    builder.row(
        KeyboardButton(text="📦 Mavjud buyumlar"),
        KeyboardButton(text="🙋 Ko'ngilli bo'lish")
    )
    builder.row(
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="ℹ️ Loyiha haqida")
    )
    builder.row(
        KeyboardButton(text="📞 Aloqa")
    )
    return builder.as_markup(resize_keyboard=True)


def admin_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📢 Xabar yuborish"),
        KeyboardButton(text="📊 Statistika")
    )
    builder.row(
        KeyboardButton(text="👥 Foydalanuvchilar"),
        KeyboardButton(text="📋 So'rovlar")
    )
    builder.row(
        KeyboardButton(text="🎁 Ehsonlar"),
        KeyboardButton(text="🙋 Ko'ngillilar")
    )
    builder.row(
        KeyboardButton(text="➕ Admin qo'shish"),
        KeyboardButton(text="➖ Admin o'chirish")
    )
    builder.row(
        KeyboardButton(text="🏠 Asosiy menyu")
    )
    return builder.as_markup(resize_keyboard=True)


def phone_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="📱 Telefon raqamni ulashish",
        request_contact=True
    ))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def cancel_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def back_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)


def broadcast_target_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="👥 Hamma foydalanuvchilarga",
            callback_data="broadcast_all"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🙋 Ko'ngillilarga",
            callback_data="broadcast_volunteers"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data="broadcast_cancel"
        )
    )
    return builder.as_markup()


def confirm_kb(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Tasdiqlash",
            callback_data=f"confirm_{action}"
        ),
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data=f"cancel_{action}"
        )
    )
    return builder.as_markup()
