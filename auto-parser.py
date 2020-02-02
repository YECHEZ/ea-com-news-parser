import sys
import os
import platform
from datetime import datetime
import time
import re
import pymysql as mariadb
import asyncio
import discord
from discord.ext import commands
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup

IS_DEV = True

if IS_DEV:
    token = ''
    TRACK_GUILD = None
    CHANNEL_DEV = None
    CHANNEL_ADV = CHANNEL_DEV
    CHANNEL_APEX = CHANNEL_DEV
    CHANNEL_ANTHEM = CHANNEL_DEV
    CHANNEL_FIFA = CHANNEL_DEV
    CHANNEL_BF = CHANNEL_DEV
    CHANNEL_NFS = CHANNEL_DEV
    CHANNEL_PVZ = CHANNEL_DEV
    CHANNEL_SIMS = CHANNEL_DEV
    ROLE_APEX = None
    ROLE_ANTHEM = ROLE_APEX
    ROLE_FIFA = ROLE_APEX
    ROLE_BF = ROLE_APEX
    ROLE_NFS = ROLE_APEX
    ROLE_PVZ = ROLE_APEX
    ROLE_SIMS = ROLE_APEX
else:
    token = ''
    TRACK_GUILD = None
    CHANNEL_DEV = None
    CHANNEL_ADV = CHANNEL_DEV
    CHANNEL_APEX = CHANNEL_DEV
    CHANNEL_ANTHEM = CHANNEL_DEV
    CHANNEL_FIFA = CHANNEL_DEV
    CHANNEL_BF = CHANNEL_DEV
    CHANNEL_NFS = CHANNEL_DEV
    CHANNEL_PVZ = CHANNEL_DEV
    CHANNEL_SIMS = CHANNEL_DEV
    ROLE_APEX = None
    ROLE_ANTHEM = ROLE_ANTHEM
    ROLE_FIFA = ROLE_ANTHEM
    ROLE_BF = ROLE_ANTHEM
    ROLE_NFS = ROLE_ANTHEM
    ROLE_PVZ = ROLE_ANTHEM
    ROLE_SIMS = ROLE_ANTHEM

urls = [
    'https://www.ea.com/ru-ru/games/apex-legends/news',
    'https://www.ea.com/ru-ru/games/anthem/news',
    'https://www.ea.com/ru-ru/games/battlefield/battlefield-5/news',
    'https://www.ea.com/ru-ru/games/need-for-speed/need-for-speed-heat/news',
    'https://www.ea.com/ru-ru/games/plants-vs-zombies/plants-vs-zombies-battle-for-neighborville/news',
    'https://www.ea.com/ru-ru/games/fifa/fifa-20/news',
    'https://www.ea.com/ru-ru/games/the-sims/the-sims-4/news',
    'https://www.ea.com/ru-ru/games/fifa/fifa-19/news',
]

def db_connect():
    if IS_DEV:
        mariadb_connection = mariadb.connect(
            host='localhost',
            user='root',
            password='',
            db='',
            charset='utf8mb4',
            cursorclass=mariadb.cursors.DictCursor,
        )
    else:
        mariadb_connection = mariadb.connect(
            host='localhost',
            user='root',
            password='',
            db='',
            charset='utf8mb4',
            cursorclass=mariadb.cursors.DictCursor,
        )
    return mariadb_connection

def get_html(response):
    if response.status_code == 200:
        return response.content
    return None

def parse(html):
    soup = BeautifulSoup(html, features="lxml")
    content = soup.find('ea-grid')
    news_feed = []
    if content:
        container = content.find_all('ea-container')
        if container:
            for item in container:
                news_object = News(item, is_html=True)
                news_feed.append(news_object)
    return news_feed

async def send_message(self, result):
    post = News(result, is_html=False)
    channel = None
    role = None
    guild = self.get_guild(TRACK_GUILD)
    if guild is not None:
        if 'apex' in str(post.game).lower():
            role = guild.get_role(ROLE_APEX)
            channel = guild.get_channel(CHANNEL_APEX)
        if 'anthem' in str(post.game).lower():
            role = guild.get_role(ROLE_ANTHEM)
            channel = guild.get_channel(CHANNEL_ANTHEM)
        if 'fifa' in str(post.game).lower():
            role = guild.get_role(ROLE_FIFA)
            channel = guild.get_channel(CHANNEL_FIFA)
        if 'battlefield' in str(post.game).lower():
            role = guild.get_role(ROLE_BF)
            channel = guild.get_channel(CHANNEL_BF)
        if 'nfs' in str(post.game).lower() or 'need for speed' in str(post.game).lower():
            role = guild.get_role(ROLE_NFS)
            channel = guild.get_channel(CHANNEL_NFS)
        if 'pvz' in str(post.game).lower() or 'plants' in str(post.game).lower():
            role = guild.get_role(ROLE_PVZ)
            channel = guild.get_channel(CHANNEL_PVZ)
        if 'sims' in str(post.game).lower():
            role = guild.get_role(ROLE_SIMS)
            channel = guild.get_channel(CHANNEL_SIMS)

        if role is not None and channel is not None:
            content = f"{role.mention}\n\n**{post.title}**\n{post.description}\n\nПодробнее: {post.url}"
            try:
                await channel.send(content)
            except Exception as e:
                print("Ошибка в постинге сообщения - send_message")
                print(str(e))
                channel = guild.get_channel(CHANNEL_DEV)
                await channel.send(f"Ошибка отправки поста: {post.title}\nError: {str(e)}")
        else:
            print(f"Ошибка отправки поста: {post.title}\nError: Unknown role {str(role)} or channel {str(channel)}")
    else:
        print(f"Ошибка отправки поста: {post.title}\nError: Unknown guild {str(guild)}")

def update_handler(loop, context):
    print('Exception handler called')
    print(loop)
    print(context)
    print('------------------------')
    sys.exit()

class News:

    def __init__(self, raw_data, is_html):
        self._data = raw_data
        self.title = None
        self.date = None

        if is_html == True:
            self.from_html()
        else:
            self.from_db()

    def from_html(self):
        self.date = self._data.find('ea-tile').get('eyebrow-secondary-text')
        self.title = str(self._data.h3.string).strip()
        self.description = str(self._data.find('ea-tile-copy').string).strip()
        self.game = str(self._data.find('ea-tile').get('eyebrow-text')).strip()
        self.url = 'https://www.ea.com' + self._data.a.get('href')
        self.media = self._data.find('ea-tile').get('media')
        # костыль под шаблон фифы
        if self.date is None:
            self.date = self.game
            self.game = "FIFA 19" if 'fifa-19' in self.url else "FIFA 20"

    def from_db(self):
        self.date = self._data['post_date']
        self.title = self._data['post_title'] if self._data['post_edit_title'] is None else self._data['post_edit_title']
        self.description = self._data['post_short_description'] if self._data['post_description'] is None else self._data['post_description']
        self.game = self._data['post_game']
        self.url = self._data['post_url']
        self.media = self._data['post_media_url']

    def __repr__(self):
        return ('<{0} {1} {2}>').format(self.__class__.__name__, self.date, self.title)

    def __str__(self):
        content = f"[{self.date}] #{self.game} | {self.title} - {self.description} ({self.url})"
        return content


class NewsFeed(commands.Bot):

    def __init__(self, is_dev):
        super().__init__(command_prefix="!")
        self.remove_command('help')
        self.is_dev = is_dev
        self.sleep_time = 0
        self.loop.set_exception_handler(update_handler)
           
    async def on_ready(self):
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('--------')
        print(f'Current Discord.py Version: {str(discord.__version__)}')
        print(f'Current Python Version: {str(platform.python_version())}')
        self.loop.create_task(self.news_listener())

    async def news_listener(self):
        await self.wait_until_ready()
        print("news_listener - load")
        while not self.is_closed():
            await asyncio.sleep(1)

            current_time = time.time()
            if current_time > self.sleep_time:
                self.sleep_time = 0

            if self.sleep_time == 0:
                current_datetime = datetime.now()
                print(f"[{current_datetime}] Проверка на новые посты")
                with FuturesSession(executor=ProcessPoolExecutor()) as session:
                    futures = [session.get(url) for url in urls]
                    for future in futures:
                        result = future.result()
                        raw_html = get_html(result)
                        if raw_html is not None:
                            news_objects = parse(raw_html)
                            if len(news_objects) != 0:
                                conn = db_connect()
                                for post in news_objects:
                                    with conn.cursor() as cursor:
                                        sql = "SELECT * FROM news_feed WHERE post_title LIKE %s LIMIT 1"
                                        params = (str(post.title),)
                                        cursor.execute(sql, params)
                                        result = cursor.fetchone()
                                        #insert if None
                                        if result is None:
                                            sql = "INSERT INTO news_feed (post_title, post_short_description, post_game, post_url, post_media_url, post_date) VALUES (%s, %s, %s, %s, %s, %s)"
                                            params = (post.title, post.description, post.game, post.url, post.media, post.date,)
                                            cursor.execute(sql, params)
                                            post_id = cursor.lastrowid
                                            conn.commit()
                                            channel = self.get_channel(CHANNEL_DEV)
                                            if channel is not None:
                                                dev_message = f"@here\n#НОВОЕ\n\nИгра: {post.game} | Дата: {post.date}\nЗаголовок: {post.title}\nОписание: {post.description}\nИсточник: {post.url}"\
                                                    f"\n`ID поста для редактирования: {post_id}\n!accept {post_id} - подтвердить на отправку\n!edit_title {post_id} Новый_заголовок - изменить заголовок статьи"\
                                                    f"\n!edit_description {post_id} Новое_описание - изменить описание статьи"\
                                                    f"\n!edit_game {post_id} Новое_название_игры - изменить название игры (*используется для определения чата при публикации)"\
                                                    f"\n!edit_url {post_id} Новый_источник - изменить источник статьи\n!refresh {post_id} - вид сообщения из БД"\
                                                    f"\n!cancel {post_id} - отменить статью на публикацию (не опубликует если была в очереди / используя после !accept {post_id} можно переопубликовать ещё раз)`"
                                                try:
                                                    await channel.send(dev_message)
                                                except Exception as e:
                                                    await channel.send(f"Ошибка отправки поста: {post.title}\nID поста для редактирования: {post_id}\nError: {str(e)}")
                                        else:
                                            is_posted = bool(result['is_posted'])
                                            is_active = bool(result['is_active'])
                                            if is_posted == False:
                                                if is_active == True:
                                                    # постим и делаем is_posted = True
                                                    try:
                                                        await send_message(self, result)
                                                        post_id = int(result['post_id'])
                                                        sql = "UPDATE news_feed SET is_posted = %s WHERE post_id = %s LIMIT 1"
                                                        params = (1, post_id,)
                                                        cursor.execute(sql, params)
                                                        conn.commit()
                                                    except Exception as e:
                                                        print("Ошибка отправки поста в news_listener")
                                                        print(str(e))
                                conn.close()
                self.sleep_time = current_time + (5*60)
            await asyncio.sleep(3)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if isinstance(message.channel, discord.abc.PrivateChannel):
            channel = message.channel
            await channel.send(f"Привет, {message.author.mention} !"
                               "\nМне запретили обрабатывать запросы через личные сообщения :zipper_mouth: "
                               "\nНо ТЫ всегда можешь увидеть меня на Discord сервере EA Russia :sunglasses: "
                               "\nEA Russia - https://discord.gg/earussia"
                               "\n\nРазработчик бота - YECHEZ#0024")
        if message.guild.id != TRACK_GUILD:
            return

        if message.channel.id == CHANNEL_DEV:
            if '!!restart_bot' in message.content:
                await message.channel.send("Ухожу в перезагрузку")
                print(f"Перезагрузка вызвана - {str(message.author)}")
                sys.exit()
                return

            if message.content.startswith("!accept"):
                params = message.content.split(' ', 1)
                if len(params) == 2:
                    post_id = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    if post_id is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                sql = "UPDATE news_feed SET is_active = %s WHERE post_id = %s LIMIT 1"
                                sql_params = (1, post_id,)
                                cursor.execute(sql, sql_params)
                                conn.commit()
                                await message.channel.send(f"Пост с ID = {post_id} - в очереди на отправку (~ каждые 5 минут)\n!cancel {post_id} - убрать из очереди")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !accept ID")

            if message.content.startswith("!cancel"):
                params = message.content.split(' ', 1)
                if len(params) == 2:
                    post_id = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    if post_id is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                sql = "UPDATE news_feed SET is_active = %s, is_posted = %s WHERE post_id = %s LIMIT 1"
                                sql_params = (0, 0, post_id,)
                                cursor.execute(sql, sql_params)
                                conn.commit()
                                await message.channel.send(f"Пост с ID = {post_id} - снят с очереди\n!accept {post_id} - добавить в очередь на отправку (~ каждые 5 минут)")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !cancel ID")

            if message.content.startswith("!edit_title"):
                params = message.content.split(' ', 2)
                if len(params) == 3:
                    post_id = None
                    new_game = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    try:
                        new_game = params[2]
                    except:
                        await message.channel.send(f"Ошибка во втором параметре = {params[2]}")
                    if post_id is not None and new_game is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                sql = "UPDATE news_feed SET post_edit_title = %s WHERE post_id = %s LIMIT 1"
                                sql_params = (new_game, post_id,)
                                cursor.execute(sql, sql_params)
                                conn.commit()
                                await message.channel.send(f"Пост с ID = {post_id} - Обновлён.\n!refresh {post_id} - обновлённое сообщение\n!accept {post_id} - добавить в очередь на отправку (~ каждые 5 минут)")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !edit_title ID Новый_заголовок")

            if message.content.startswith("!edit_description"):
                params = message.content.split(' ', 2)
                if len(params) == 3:
                    post_id = None
                    new_game = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    try:
                        new_game = params[2]
                    except:
                        await message.channel.send(f"Ошибка во втором параметре = {params[2]}")
                    if post_id is not None and new_game is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                sql = "UPDATE news_feed SET post_description = %s WHERE post_id = %s LIMIT 1"
                                sql_params = (new_game, post_id,)
                                cursor.execute(sql, sql_params)
                                conn.commit()
                                await message.channel.send(f"Пост с ID = {post_id} - Обновлён.\n!refresh {post_id} - обновлённое сообщение\n!accept {post_id} - добавить в очередь на отправку (~ каждые 5 минут)")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !edit_description ID Новое_описание")

            if message.content.startswith("!edit_url"):
                params = message.content.split(' ', 2)
                if len(params) == 3:
                    post_id = None
                    new_game = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    try:
                        new_game = params[2]
                    except:
                        await message.channel.send(f"Ошибка во втором параметре = {params[2]}")
                    if post_id is not None and new_game is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                sql = "UPDATE news_feed SET post_url = %s WHERE post_id = %s LIMIT 1"
                                sql_params = (new_game, post_id,)
                                cursor.execute(sql, sql_params)
                                conn.commit()
                                await message.channel.send(f"Пост с ID = {post_id} - Обновлён.\n!refresh {post_id} - обновлённое сообщение\n!accept {post_id} - добавить в очередь на отправку (~ каждые 5 минут)")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !edit_url ID Новый_источник")

            if message.content.startswith("!edit_game"):
                params = message.content.split(' ', 2)
                if len(params) == 3:
                    post_id = None
                    new_game = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    try:
                        new_game = params[2]
                    except:
                        await message.channel.send(f"Ошибка во втором параметре = {params[2]}")
                    if post_id is not None and new_game is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                sql = "UPDATE news_feed SET post_game = %s WHERE post_id = %s LIMIT 1"
                                sql_params = (new_game, post_id,)
                                cursor.execute(sql, sql_params)
                                conn.commit()
                                await message.channel.send(f"Пост с ID = {post_id} - Обновлён.\n!refresh {post_id} - обновлённое сообщение\n!accept {post_id} - добавить в очередь на отправку (~ каждые 5 минут)")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !edit_game ID Новое_название_игры")

            if message.content.startswith("!refresh"):
                params = message.content.split(' ', 1)
                if len(params) == 2:
                    post_id = None
                    try:
                        post_id = int(params[1])
                    except:
                        await message.channel.send(f"Не могу найти пост с ID = {params[1]}")
                    if post_id is not None:
                        conn = db_connect()
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM news_feed WHERE post_id = %s LIMIT 1"
                            sql_params = (post_id,)
                            cursor.execute(sql, sql_params)
                            result = cursor.fetchone()
                            if result is not None:
                                post = News(result, is_html=False)
                                dev_message = f"Игра: {post.game} | Дата: {post.date}\nЗаголовок: {post.title}\nОписание: {post.description}\nИсточник: {post.url}\nID поста для редактирования: {post_id}\n"
                                try:
                                    await message.channel.send(dev_message)
                                except Exception as e:
                                    await message.channel.send(f"Ошибка отправки поста: {post.title}\nID поста для редактирования: {post_id}\nError: {str(e)}")
                            else:
                                await message.channel.send(f"Не могу найти пост с ID = {post_id}")
                        conn.close()
                else:
                    await message.channel.send(f"Используй: !refresh ID")

if __name__ == '__main__':
    try:
        conn = db_connect()
    except Exception as e:
        print('Starting bot - Database error')
        print(str(e))
        sys.exit()
    finally:
        conn.close()

    try:
        bot = NewsFeed(IS_DEV)
        bot.run(token)
    except Exception as e:
        print('bot.run - error')
        print(str(e))
    finally:
        sys.exit()