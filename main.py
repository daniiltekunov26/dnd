from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from database import Session, Character

# Состояния для диалога создания персонажа
ENTER_NAME, CHOOSE_RACE, CHOOSE_SUBRACE, CHOOSE_CLASS, ENTER_STATS = range(5)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Используйте команду /create_character для создания персонажа."
    )

async def create_character_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя персонажа:")
    return ENTER_NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    races = ["Человек", "Эльф", "Дварф", "Гном", "Полурослик", "Драконорожденный"]
    keyboard = ReplyKeyboardMarkup.from_column(races, one_time_keyboard=True)
    await update.message.reply_text("Выберите расу:", reply_markup=keyboard)
    return CHOOSE_RACE


async def receive_race(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_race = update.message.text
    context.user_data['race'] = selected_race
    if selected_race == 'Человек':
        subraces = ['Рус', 'Ящер']
        keyboard = ReplyKeyboardMarkup.from_column(subraces, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Выберите подрасу:", reply_markup=keyboard)
        return CHOOSE_SUBRACE
    elif selected_race == 'Дварф':
        subraces = ['Микроглэк', 'Миниглэк']
        keyboard = ReplyKeyboardMarkup.from_column(subraces, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Выберите подрасу:", reply_markup=keyboard)
        return CHOOSE_SUBRACE
    else:
        classes = ["Воин", "Волшебник", "Плут", "Жрец", "Паладин"]
        keyboard = ReplyKeyboardMarkup.from_column(classes, one_time_keyboard=True)
        await update.message.reply_text("Выберите класс:", reply_markup=keyboard)
        return CHOOSE_CLASS

async def receive_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['class_name'] = update.message.text
    await update.message.reply_text(
        "Введите характеристики через пробел в порядке исходя из следующего набора: 15,14,13,12,10,8.\n "
        "\nХарактеристики: Сила, Ловкость, Телосложение, Интеллект, Мудрость, Харизма.\n"
        "\nКаждое из чисел может соответствовать только одной характеристике. Порядок распределения соответствует списку характеристик сверху.\n"
        "\nПример ввода: 13 12 15 8 10 14"
        "\nВ данном случае Сила = 13, Ловкость = 12 и т.д."

    )
    return ENTER_STATS

async def receive_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stats = list(map(int, update.message.text.strip().split()))
        if len(stats) != 6:
            raise ValueError("Должно быть ровно 6 чисел")
    except Exception:
        await update.message.reply_text("Неверный формат. Введите 6 чисел через пробел.")
        return ENTER_STATS

    session = Session()
    new_character = Character(
        user_id=update.effective_user.id,
        name=context.user_data['name'],
        race=context.user_data['race'],
        class_name=context.user_data['class_name'],
        strength=stats[0],
        dexterity=stats[1],
        constitution=stats[2],
        intelligence=stats[3],
        wisdom=stats[4],
        charisma=stats[5],
        level=1,
        skills=None,
        inventory=None,
    )
    session.add(new_character)
    session.commit()
    await update.message.reply_text("Персонаж успешно создан! Используйте /show_character для просмотра.")
    return ConversationHandler.END

async def level_up_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    character = session.query(Character).filter_by(user_id=update.effective_user.id).first()
    if not character:
        await update.message.reply_text("Персонаж не найден. Создайте его с помощью /create_character.")
        return
    character.level += 1
    # Здесь можно добавить логику повышения характеристик и навыков
    session.commit()
    await update.message.reply_text(f"Персонаж {character.name} повышен до уровня {character.level}!")

async def show_character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    character = session.query(Character).filter_by(user_id=update.effective_user.id).first()
    if not character:
        await update.message.reply_text("Персонаж не найден. Создайте его с помощью /create_character.")
        return

    def mod(stat):
        return (stat - 10) // 2

    sheet = (
        f"Имя: {character.name}\n"
        f"Уровень: {character.level}\n"
        f"Раса: {character.race}\n"
        f"Подраса {character.subrace}\n"
        f"Класс: {character.class_name}\n"
        f"Статы:\n"
        f"Сила: {character.strength} ({mod(character.strength):+d})\n"
        f"Ловкость: {character.dexterity} ({mod(character.dexterity):+d})\n"
        f"Телосложение: {character.constitution} ({mod(character.constitution):+d})\n"
        f"Интеллект: {character.intelligence} ({mod(character.intelligence):+d})\n"
        f"Мудрость: {character.wisdom} ({mod(character.wisdom):+d})\n"
        f"Харизма: {character.charisma} ({mod(character.charisma):+d})"
    )
    await update.message.reply_text(sheet)

def main():
    application = ApplicationBuilder().token("8162549210:AAEVGps-DLIt9PYRSRaZBOMhlg6I_G5xP80").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create_character", create_character_start)],
        states={
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            CHOOSE_RACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_race)],
            CHOOSE_CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_class)],
            ENTER_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_stats)],
        },
        fallbacks=[],
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("level_up", level_up_command))
    application.add_handler(CommandHandler("show_character", show_character_command))

    application.run_polling()

if __name__ == "__main__":
    main()


