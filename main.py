# -*- coding: utf-8 -*-
from pyrogram import Client
from pyrogram.errors import FloodWait
import redis
import _thread as thread
import time
import re
import os
redis = redis.Redis(host = 'localhost', port = 6379, db = 0)
sudo_ids = [802959264,859862734] #sudo user id
app = Client(
api_id = 1053684,
api_hash = '3c32c51e34a193db04b06ba0f004f115',
session_name = 'test',
workdir = './session'
)
##+++++++++++++++START+++++++++++++++++##
def is_sudo(user_id):
    for sudo_id in sudo_ids:
        if sudo_id == user_id:
            return True

def send_sudo(text):
    for sudo_id in sudo_ids:
        try:
            app.send_message(chat_id = sudo_id, text = text, parse_mode = 'html')
        except Exception as Error:
            print(Error)

def check_username(user_name):
    url = 'https://t.me/{}'.format(user_name)
    result = os.popen('torsocks curl "https://t.me/{}"'.format(user_name)).read()
    if re.search('tgme_icon_user', result):
        return True

def get_username(user_name):
    while redis.get('user_name'):
        if check_username(user_name):
            try:
                app.update_username(username = user_name)
                send_sudo('☤ Message : \n User : @{}  <b>seted to user check</b> '.format(user_name))
                redis.delete('user_name')
                redis.delete('checked:latest')
                break
            except FloodWait as error:
                send_sudo('☤ Message : Access Denied \n Error : <b> Too Many Requests: retry after {} seconds </b> '.format(error.x))
                time.sleep(error.x)
            except Exception as Error:
                print(Error)
        else:
            redis.set('checked:latest',time.strftime('%H:%M:%S'))

@app.on_message()
def main(client, msg):
    if msg.text and is_sudo(msg.from_user.id):
        if msg.text == '/ping':
            msg.reply('☤ PONG ☤')
        elif re.match('/setusername\W@(\w+)', msg.text):
            user_name = re.match('/setusername\W@(\w+)', msg.text).groups()[0]
            try:
                result = app.get_chat(user_name)
                redis.set('user_name', user_name)
                thread.start_new_thread(get_username,(user_name,))
                msg.reply('☤ Message : User :@{} | {}  seted to  user check'.format(user_name , result.first_name or result.title), parse_mode = 'html')
            except Exception as error:
                msg.reply(error)
        elif msg.text == '/info':
            if redis.get('user_name'):
                checked_latest = redis.get('checked:latest').decode()
                user_name = redis.get('user_name').decode()
                msg.reply('☤ username @{} checked {} \n\n Powered by <a href="github.com/khodeamir">Amir Bagheri</a> and <a href="github.com/MiladHeidary">Milad Heidary</a>'.format(user_name, checked_latest), parse_mode = 'html', disable_web_page_preview  = True)
            else:
                msg.reply('☤ <b>Please set target</b> !', parse_mode = 'html')
        elif msg.text == '/delete':
            redis.delete('user_name')
            redis.delete('checked:latest')
            msg.reply('☤ <b>Bot database reseted</b> !', parse_mode = 'html')

if __name__ == '__main__':
    app.run()
