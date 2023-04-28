import functools

from environs import Env
from redis import Redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Filters, MessageHandler, Updater)

from elastic_api import ElasticConnection


def get_menu_reply_markup(elastic_connection: ElasticConnection):
    products = elastic_connection.get_products()
    keyboard = []
    for product in products['data']:
        keyboard.append(
            [
                InlineKeyboardButton(
                    product['attributes']['name'],
                    callback_data=product['id']
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def start(
    update: Update,
    context: CallbackContext,
    elastic_connection: ElasticConnection
) -> str:
    reply_markup = get_menu_reply_markup(elastic_connection)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return 'HANDLE_MENU'


def handle_menu(
    update: Update,
    context: CallbackContext,
    elastic_connection: ElasticConnection
) -> str:
    query = update.callback_query

    # CallbackQueries need to be answered,
    # even if no notification to the user is needed
    # Some clients may have trouble otherwise.
    # See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    chat_id = query.from_user.id
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id
    )
    product = elastic_connection.get_product(query.data)["data"]
    main_image_id = product['relationships']['main_image']['data']['id']
    image_link = elastic_connection.get_file_link(main_image_id)
    caption = (
        f'{product["attributes"]["name"]}\n\n'
        f'{product["meta"]["display_price"]["without_tax"]["formatted"]} '
        'per kg\n\n'
        f'{product["attributes"]["description"]}'
    )
    keyboard = [[InlineKeyboardButton('Back', callback_data='Back')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_photo(
        chat_id=chat_id,
        photo=image_link,
        caption=caption,
        reply_markup=reply_markup
    )

    return 'HANDLE_DESCRIPTION'


def handle_description(
    update: Update,
    context: CallbackContext,
    elastic_connection: ElasticConnection
):
    query = update.callback_query
    query.answer()

    chat_id = query.from_user.id
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id
    )
    if query.data == 'Back':
        reply_markup = get_menu_reply_markup(elastic_connection)
        context.bot.send_message(
            chat_id=chat_id,
            text='Please choose:',
            reply_markup=reply_markup
        )
        return 'HANDLE_MENU'


def handle_users_reply(
        update: Update,
        context: CallbackContext,
        redis_connection: Redis,
        elastic_connection: ElasticConnection) -> None:
    chat_id_prefix = 'fish_shop_'
    chat_id = f'{chat_id_prefix}{update.message.chat_id}' if update.message\
        else f'{chat_id_prefix}{update.callback_query.from_user.id}'

    if update.message and update.message.text == '/start':
        user_state = 'START'
    else:
        user_state = redis_connection.get(chat_id)

    if not user_state:
        user_state = 'START'

    start_handler = functools.partial(
        start,
        elastic_connection=elastic_connection,
    )

    menu_handler = functools.partial(
        handle_menu,
        elastic_connection=elastic_connection,
    )

    description_handler = functools.partial(
        handle_description,
        elastic_connection=elastic_connection,
    )

    states_functions = {
        'START': start_handler,
        'HANDLE_MENU': menu_handler,
        'HANDLE_DESCRIPTION': description_handler,
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

    with env.prefixed('ELASTIC_'):
        elastic_connection = ElasticConnection(
            client_id=env('PATH_CLIENT_ID'),
            client_secret=env('PATH_CLIENT_SECRET'),
        )

    users_reply_handler = functools.partial(
        handle_users_reply,
        redis_connection=redis_connection,
        elastic_connection=elastic_connection,
    )

    updater = Updater(env('FISH_BOT_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, users_reply_handler))
    dispatcher.add_handler(CommandHandler('start', users_reply_handler))
    dispatcher.add_handler(CallbackQueryHandler(users_reply_handler))
    updater.start_polling()


if __name__ == '__main__':
    main()
