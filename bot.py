# coding: utf-8

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ChatAction, InlineQueryResultArticle, InputTextMessageContent
import logging
import os
import time
from uuid import uuid4
import json

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

MODE = os.environ.get('MODE', 'polling')
URL = os.environ.get('URL')
TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', '5000'))

LOADED_DATA = json.loads(open('kinobiletbot.json').read())
DATA = []
for movie in LOADED_DATA:
    title = list(movie.keys())[0]
    for movie2 in movie[title]:
        DATA.append({
            'title': '{} {}'.format(title, movie2['option']),
            'image': movie2['image_link'],
            'sessions': movie2['sessions']
        })
CUR_INDEX = 0
IND_SIZE = len(DATA)

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Привет, чтобы узнать расписание сеансов отправь команду /go', parse_mode='HTML')

def show_movie(bot, update):
  chat_id = update.message.chat_id
  message_id = update.message.message_id + 1

  INDEX = 0

  inline_buttons = [[InlineKeyboardButton('⬅️', callback_data='prev'),
                     InlineKeyboardButton('➡️', callback_data='next')]]

  for session in DATA[INDEX]['sessions']:
      inline_buttons.append([InlineKeyboardButton('{} ({} руб.)'.format(session['time'], session['price']), callback_data='time_{}_{}'.format(INDEX, session['time']))])

  bot.sendChatAction(chat_id, ChatAction.TYPING)
  owner_id = update.message.from_user.id
  #bot.send_photo(chat_id=chat_id, photo=DATA[INDEX]['image'])
  bot.sendMessage(chat_id=chat_id, text='<b>{}</b> \n{}'.format(DATA[INDEX]['title'], DATA[INDEX]['image']), parse_mode='HTML',
                  reply_markup=InlineKeyboardMarkup(inline_buttons))

  
def button_click(bot, update):
  global CUR_INDEX  
  query = update.callback_query

  user_id = query.from_user.id
  chat_id = None
  message_id = None
  inline_message_id = None
  try:
    chat_id = query.message.chat_id
    message_id = query.message.message_id
  except:
    inline_message_id = query.inline_message_id

  button_key = query.data.split('_')

  if button_key[0] == 'prev' or button_key[0] == 'next' or button_key[0] == 'return':
    if button_key[0] == 'prev':
        CUR_INDEX = (CUR_INDEX - 1) % IND_SIZE
    if button_key[0] == 'next':
        CUR_INDEX = (CUR_INDEX + 1) % IND_SIZE

    inline_buttons = [[InlineKeyboardButton('⬅️', callback_data='prev'),
                       InlineKeyboardButton('➡️', callback_data='next')]]

    for session in DATA[CUR_INDEX]['sessions']:
        inline_buttons.append([InlineKeyboardButton('{} ({} руб.)'.format(session['time'], session['price']), callback_data='time_{}_{}'.format(CUR_INDEX, session['time']))])

    #bot.answerCallbackQuery(update.callback_query.id, 'хело')
    bot.editMessageText(text='<b>{}</b> \n{}'.format(DATA[CUR_INDEX]['title'], DATA[CUR_INDEX]['image']), 
                        chat_id=chat_id, message_id=message_id, inline_message_id=inline_message_id,
                        parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_buttons))
  
  elif button_key[0] == 'time' or button_key[0] == 'refresh':
    time_text = button_key[2]

    inline_buttons = [[InlineKeyboardButton('Обновить', callback_data='refresh_{}_{}'.format(CUR_INDEX, time_text))],
                      [InlineKeyboardButton('Назад', callback_data='return')]]

    if button_key[0] == 'refresh':
        bot.answerCallbackQuery(update.callback_query.id, 'схема зала обновлена') 
    bot.editMessageText(text='<b>{}</b>\nНачало в {} \nВ {} зале \n{}'.format(DATA[CUR_INDEX]['title'], time_text, 'красном', 
                        'https://s3.eu-central-1.amazonaws.com/gidigo-photos/out3.png?'+str(time.time())),
                        chat_id=chat_id, message_id=message_id, inline_message_id=inline_message_id,
                        parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_buttons))

def inline_query(bot, update):
  results = []

  inline_buttons = [[InlineKeyboardButton('пример', callback_data='sample')]]

  for movie in DATA:
    movie_desc = ''
    for session in movie['sessions']:
        movie_desc += '{} '.format(session['time'])

    inline_buttons = [[InlineKeyboardButton('⬅️', callback_data='prev'),     
                       InlineKeyboardButton('➡️', callback_data='next')]]             
                                                                                                                    
    for session in movie['sessions']: 
      inline_buttons.append([InlineKeyboardButton('{} ({} руб.)'.format(session['time'], session['price']), callback_data='time_{}_{}'.format(1, session['time']))])

    results.append(InlineQueryResultArticle(id=uuid4(), title='{}'.format(movie['title']), 
                     input_message_content=InputTextMessageContent('<b>{}</b> \n{}'.format(movie['title'], movie['image']), parse_mode='HTML'),
                     description=movie_desc,
                     thumb_url=movie['image'],
                     reply_markup=InlineKeyboardMarkup(inline_buttons)))
    
  bot.answerInlineQuery(inline_query_id=update.inline_query.id, results=results)

def error_callback(bot, update, error):
  try:
    raise error
  except Exception as e:
    print(e)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('go', show_movie))
dispatcher.add_handler(CallbackQueryHandler(button_click))
dispatcher.add_handler(InlineQueryHandler(inline_query))
dispatcher.add_error_handler(error_callback)


if MODE == 'webhook':
    updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
    updater.bot.setWebhook(URL + '/' + TOKEN)
    updater.idle()
else:
    updater.start_polling()




















