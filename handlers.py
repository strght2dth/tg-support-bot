import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from settings import WELCOME_MESSAGE, TELEGRAM_SUPPORT_CHAT_ID, REPLY_TO_THIS_MESSAGE, WRONG_REPLY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

    user_info = update.message.from_user.to_dict()

    await context.bot.send_message(
        chat_id=TELEGRAM_SUPPORT_CHAT_ID,
        text=f"""
📞 Connected {user_info}.
        """,
    )


async def forward_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles forwarding messages from private chats to the support chat."""
    forwarded = await update.message.forward(chat_id=TELEGRAM_SUPPORT_CHAT_ID)
    if not hasattr(forwarded, 'forward_from') or forwarded.forward_from is None:
        await context.bot.send_message(
            chat_id=TELEGRAM_SUPPORT_CHAT_ID,
            reply_to_message_id=forwarded.message_id,
            text=f'{update.message.from_user.id}\n{REPLY_TO_THIS_MESSAGE}'
        )


async def forward_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles forwarding replies from the support chat back to the user."""
    user_id = None
    reply_message = update.message.reply_to_message

    if reply_message and hasattr(reply_message, 'forward_from') and reply_message.forward_from:
        user_id = reply_message.forward_from.id
    elif reply_message and REPLY_TO_THIS_MESSAGE in reply_message.text:
        try:
            user_id = int(reply_message.text.split('\n')[0])
        except ValueError:
            user_id = None

    if user_id:
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
    else:
        await context.bot.send_message(
            chat_id=TELEGRAM_SUPPORT_CHAT_ID,
            text=WRONG_REPLY
        )


def setup_dispatcher(application: Application) -> Application:
    """Sets up the handlers for the application."""
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE, forward_to_chat))
    application.add_handler(MessageHandler(filters.Chat(TELEGRAM_SUPPORT_CHAT_ID) & filters.REPLY, forward_to_user))
    return application
