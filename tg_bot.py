import functools

from environs import Env
from redis import Redis
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def start(update, context):
    update.message.reply_text(text='Hello!')
    return "ECHO"


def echo(update, context):
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return "ECHO"


def handle_users_reply(update, context, redis_connection):
    user_reply = update.message.text
    chat_id = update.message.chat_id
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = redis_connection.get(chat_id)

    if not user_state:
        user_state = 'START'

    states_functions = {
        'START': start,
        'ECHO': echo
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    redis_connection.set(chat_id, next_state)


def main():
    env = Env()
    env.read_env()

    with env.prefixed('REDIS_'):
        redis_connection = Redis(
            host=env('HOST'),
            port=env('PORT'),
            password=env('PASSWORD'),
            decode_responses=True
        )

    users_reply_handler = functools.partial(
        handle_users_reply,
        redis_connection=redis_connection,
    )

    updater = Updater(env('FISH_BOT_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, users_reply_handler))
    dispatcher.add_handler(CommandHandler('start', users_reply_handler))
    updater.start_polling()


if __name__ == '__main__':
    main()
