from flask import Flask, url_for, request, render_template, redirect
import os
import json, datetime
from news_form import AddNewsForm
from loginform import LoginForm
from chat_form import ChatForm
import time

import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
count = 0


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 user_name VARCHAR(50),
                                 password_hash VARCHAR(128),
                                 friend_list VARCHAR(320)
                                 )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, friend_list) 
                          VALUES (?,?,?)''', (user_name, password_hash, bytes([])))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        if user_id == 'all':
            cursor.execute("SELECT * FROM users")
            row = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", [str(user_id)])
            row = cursor.fetchone()
        return row

    def get_by_name(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", [name])
        row = cursor.fetchone()
        return row

    def correct_user(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def check_username(self, user_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", [user_name])
        row = cursor.fetchone()
        if row :
            return (True, row[0])
        else:
            return False

    def registrate(self, user_name, password):
        row = self.check_username(user_name)
        if row:
            return (False, 0)
        else:
            cursor = self.connection.cursor()
            self.insert(user_name, password)
            cursor.execute("SELECT * FROM users WHERE user_name = ?", [user_name])
            row = cursor.fetchone()
            return (True, row[0])

    def add_friend(self, user_id, friend_id):
        self.adding_friend(user_id, friend_id)
        self.adding_friend(friend_id, user_id)

    def adding_friend(self, user_id, friend_id):
        massive = list(self.get(user_id)[3])
        massive.append(friend_id)
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET friend_list = ? WHERE id = ?", (bytes(massive), user_id))
        self.connection.commit()

    def delete_friend(self, user_id, friend_name):
        friend_id = self.get_by_name(friend_name)[0]
        self.deleting_friend(friend_id, user_id)
        self.deleting_friend(user_id, friend_id)

    def deleting_friend(self, user_id, friend_id):
        massive = list(self.get(user_id)[3])
        del massive[massive.index(friend_id)]
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET friend_list = ? WHERE id = ?", (bytes(massive), user_id))
        self.connection.commit()


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 title VARCHAR(100),
                                 content VARCHAR(1000),
                                 user_id INTEGER
                                 )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                            (title, content, user_id) 
                              VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", [str(news_id)])
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ?", [str(user_id)])
        else:
            cursor.execute("SELECT * FROM news")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', [str(news_id)])
        cursor.close()
        self.connection.commit()


class MessageModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 content VARCHAR(1000),
                                 user_id INTEGER,
                                 friend_id INTEGER,
                                 time REAL)''')
        cursor.close()
        self.connection.commit()

    def insert(self, content, user_id, friend_id):
        cursor = self.connection.cursor()
        t1 = time.time()
        print(t1)
        cursor.execute('''INSERT INTO messages 
                            (content, user_id, friend_id, time) 
                              VALUES (?,?,?,?)''', (content, str(user_id), str(friend_id), t1))
        cursor.close()
        self.connection.commit()

    def get(self, user_id, friend_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM messages WHERE user_id = ? AND friend_id = ?",
                       [str(user_id), str(friend_id)])
        sended = cursor.fetchall()
        cursor.execute("SELECT * FROM messages WHERE user_id = ? AND friend_id = ?",
                       [str(friend_id), str(user_id)])
        gotten = cursor.fetchall()
        return [sended, gotten]

    def delete(self, id):
        cursor = self.connection.cursor()
        if id == 'all':
            cursor.execute('''DELETE FROM messages''')
            cursor.execute('''DELETE FROM messages WHERE id = ?''', [str(id)])
        cursor.close()
        self.connection.commit()


db = DB()
session = {}
user_model = UsersModel(db.get_connection())
user_model.init_table()
if not user_model.check_username('danil'):
    user_model.insert('danil', 'jojo')
news_model = NewsModel(db.get_connection())
news_model.init_table()
sort_method = 'date'
message_model = MessageModel(db.get_connection())
message_model.init_table()
print(user_model.get(1))
#user_model.add_friend(1, 4)
#message_model.delete('all')
print(message_model.get(1, 3))
print((user_model.get(1)))
print(news_model.get_all(1))


@app.route('/user/<username>')
def index(username):
    global sort_method
    if request.method == 'GET':
        if 'username' not in session:
            return redirect('/login')
        if username == 'favicon.ico':
            return
        host = user_model.get_by_name(username)
        print(username, 'name')
        if host:

            user_id = host[0]
        else:
            print(host)
        isfriend = user_id in list(user_model.get(session['user_id'])[3])
        print(isfriend)
        news = news_model.get_all(user_id)
        if sort_method == 'alph':
            news.sort(key=lambda x: x[1])
        else:
            news.sort(key=lambda x: x[0])
        print(session)
        return render_template('index_news.html', username=username,
                               news=news, session=session, isfriend=isfriend)


@app.route('/admin')
def admin():
    global sort_method
    if request.method == 'GET':
        users = user_model.get('all')
        print(users)
        if 'username' not in session:
            return redirect('/login')
        if session['username'] != 'admin':
            return redirect('/user/admin')
        content = {}
        for i in users:
            content[i[1]] = len(news_model.get_all(i[0]))

        return render_template('admin_page.html', content=content, session=session)


@app.route('/sort_by_date')
def sort_by_date():
    global sort_method
    sort_method = 'date'
    return redirect('/user/{}'.format(session['username']))


@app.route('/sort_by_alph')
def sort_by_alph():
    global sort_method
    sort_method = 'alph'
    print(session['username'], 'alph')
    return redirect('/user/{}'.format(session['username']))


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        news_model.insert(title, content, session['user_id'])
        print(session['username'], 'add_news')
        return redirect('/user/{}'.format(session['username']))
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'], session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('username', 0)
    session.pop('user_id', 0)
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        exists = user_model.correct_user(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        print(user_name, 'login')
        return redirect('/user/{}'.format(user_name))

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/chat/<friend_name>', methods=['GET', 'POST'])
def chat(friend_name):
    if 'username' not in session:
        return redirect('/login')
    friend_id = user_model.get_by_name(friend_name)[0]
    if request.method == 'POST':
        message_model.insert(request.form['text'], session['user_id'], friend_id)
        chat = get_chat(friend_id)
        return render_template('chat.html', title='Диалог', session=session, chat=chat,
                               friend_name=friend_name)
    elif request.method == 'GET':
        chat = get_chat(friend_id)
        return render_template('chat.html', title='Диалог', session=session, chat=chat,
                               friend_name=friend_name)


def get_chat(friend_id):
    date = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', "Июль",
            "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    chat = message_model.get(session['user_id'], friend_id)
    chat = chat[0] + chat[1]
    chat.sort(key=lambda x: x[4])
    for i in range(len(chat)):
        chat[i] = list(chat[i])
        t1 = time.gmtime(chat[i][4])
        cur_time = time.gmtime(time.time())
        razn = t1[2] - cur_time[2]
        if t1[0] == cur_time[0] and t1[1] == cur_time[1]:
            if razn == 0:
                day = 'сегодня'
            elif razn == 1:
                day = 'вчера'
            elif razn == 2:
                day = 'позавчера'
            else:
                day = '{} {}'.format(t1[2], date[t1[1] - 1])
        else:
            day = '{} {}'.format(t1[2], date[t1[1] - 1])
        chat[i][4] = day
    chat = chat[::-1]
    return chat


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/delete_news/<int:number>/', methods=['GET', 'POST'])
def delete_news(number):
    news_model.delete(number)
    return redirect('/user/{}'.format(session['username']))


@app.route('/delete_friend/<name>/', methods=['GET', 'POST'])
def delete_friend(name):
    if 'username' not in session:
        return redirect('/login')

    user_model.delete_friend(session['user_id'], name)
    return redirect('/user/{}'.format(name))


@app.route('/add_friend/<name>/', methods=['GET', 'POST'])
def add_friend(name):
    if 'username' not in session:
        return redirect('/login')
    friend_id = user_model.get_by_name(name)[0]
    user_model.add_friend(session['user_id'], friend_id)
    print(session['username'], 'add_Friend')
    return redirect('/user/{}'.format(name))


@app.route('/')
def log_index():
    return redirect('/login')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    session.pop('username', 0)
    session.pop('user_id', 0)
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        exists = user_model.registrate(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            print(session['username'], 'registration')
            return redirect('/user/{}'.format(user_name))
        form.alert = 'Такой логин уже занят'
    return render_template('login.html', title='Регистрация', form=form)


@app.route('/friends')
def friend_list():
    if 'username' not in session:
        return redirect('/login')
    new_friends = []
    friends = list(user_model.get(session['user_id'])[3])
    for i in friends:
        try:
            new_friends.append(user_model.get(i)[1])
        except Exception:
            pass
    print(friends, new_friends)
    return render_template('friend_list.html', username=session['username'],
            friends=new_friends, session=session)


if __name__ == '__main__':
    app.run(port=8888, host='127.0.0.1')
