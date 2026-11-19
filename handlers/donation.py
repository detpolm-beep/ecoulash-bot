from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_donation, log_event
from keyboards.main_kb import main_menu, cancel_button

router = Router()


class DonationForm(StatesGroup):
    item_name = State()
    quantity = State()
    description = State()
    confirm = State()


@router.message(F.text == "♻️ Ehson qilish")
async def donation_start(message: Message, state: FSMContext):
    await log_event("donation_start", message.from_user.id)
    await state.set_state(DonationForm.item_name)
    await message.answer(
        "♻️ <b>Ehson qilish</b>\n\n"
        "Qanday buyum ehson qilmoqchisiz?\n"
        "<i>Masalan: kiyim, oyoq kiyim, kitob, o'yinchoq...</i>",
        reply_markup=cancel_button()
    )


@router.message(DonationForm.item_name)
async def donation_item(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    await state.update_data(item_name=message.text)
    await state.set_state(DonationForm.quantity)
    await message.answer(
        "📦 Nechta buyum ehson qilmoqchisiz?\n"
        "<i>Faqat raqam kiriting (masalan: 3)</i>",
        reply_markup=cancel_button()
    )


@router.message(DonationForm.quantity)
async def donation_quantity(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting! Masalan: 1, 2, 5")
        return

    await state.update_data(quantity=int(message.text))
    await state.set_state(DonationForm.description)
    await message.answer(
        "📝 Buyum haqida qo'shimcha ma'lumot kiriting:\n"
        "<i>(holati, rangi, o'lchami va h.k.) yoki 'yo'q' deb yozing</i>",
        reply_markup=cancel_button()
    )


@router.message(DonationForm.description)
async def donation_description(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    data = await state.get_data()
    description = message.text if message.text.lower() != "yo'q" else ""

    await state.update_data(description=description)

    # Tasdiqlash
    yoq = "Yo'q"
    summary = (
        f"✅ <b>Ehson ma'lumotlari:</b>\n\n"
        f"📦 Buyum: <b>{data['item_name']}</b>\n"
        f"🔢 Miqdor: <b>{data['quantity']} dona</b>\n"
        f"📝 Izoh: <b>{description or yoq}</b>\n\n"
        f"Tasdiqlaysizmi?"
    )

    from keyboards.main_kb import confirm_kb
    await state.set_state(DonationForm.confirm)
    await message.answer(summary, reply_markup=confirm_kb("donation"))


@router.message(DonationForm.confirm)
async def donation_text_confirm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())


from aiogram.types import CallbackQuery


@router.callback_query(F.data == "confirm_donation")
async def donation_confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    await add_donation(
        donor_id=callback.from_user.id,
        item_name=data.get("item_name", ""),
        quantity=data.get("quantity", 1),
        description=data.get("description", "")
    )
    await log_event("donation_completed", callback.from_user.id, data.get("item_name"))

    await callback.message.edit_text(
        "🎉 <b>Rahmat!</b>\n\n"
        "Ehsoningiz qabul qilindi. Adminlar siz bilan tez orada bog'lanadi.\n\n"
        "🌿 Sizning yaxshiligingiz tabiatga ham, insonga ham foyda keltiradi!"
    )
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "cancel_donation")
async def donation_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Ehson bekor qilindi.")
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()
