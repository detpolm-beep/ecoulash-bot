from aiogram import Router, F
from aiogram.types import Message

from database.db import get_donations, log_event
from keyboards.main_kb import main_menu

router = Router()


@router.message(F.text == "📦 Mavjud buyumlar")
async def items_handler(message: Message):
    await log_event("view_items", message.from_user.id)

    donations = await get_donations(status="pending")

    if not donations:
        await message.answer(
            "📦 <b>Mavjud buyumlar</b>\n\n"
            "Hozircha mavjud buyumlar yo'q.\n"
            "Birinchi bo'lib ehson qiluvchi bo'ling! ♻️",
            reply_markup=main_menu()
        )
        return

    text = "📦 <b>Mavjud buyumlar ro'yxati:</b>\n\n"
    for i, item in enumerate(donations[:20], 1):
        # donations: (id, donor_id, item_name, quantity, description, status, created_at)
        item_name = item[2]
        quantity = item[3]
        description = item[4] or ""
        created_at = item[6][:10] if item[6] else ""

        text += (
            f"{i}. 📦 <b>{item_name}</b>\n"
            f"   🔢 Miqdor: {quantity} dona\n"
        )
        if description:
            text += f"   📝 {description}\n"
        text += f"   📅 {created_at}\n\n"

    if len(donations) > 20:
        text += f"\n<i>...va yana {len(donations) - 20} ta buyum mavjud</i>"

    await message.answer(text, reply_markup=main_menu())
