import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies
import random

connection = sqlite3.connect('users.db')

stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
cursor = connection.cursor()
result = cursor.execute(stmt)
r = result.fetchall()
if not r:
    exp = 'CREATE TABLE users (username,password)'
    connection.execute(exp)

nb = "SELECT name FROM sqlite_master WHERE type='table' AND name='numbers'"
cursor = connection.cursor()
result = cursor.execute(nb)
r = result.fetchall()
if not r:
    exp = 'CREATE TABLE numbers (n1, n2, c_a, ra_1, ra_2, ra_3, answers)'
    connection.execute(exp)
cursor = connection.cursor()


def reset_numbers():
    num1 = connection.execute('SELECT n1 FROM numbers').fetchall()[0][0]
    num2 = connection.execute('SELECT n2 FROM numbers').fetchall()[0][0]
    c_an = connection.execute('SELECT c_a FROM numbers').fetchall()[0][0]
    r_an1 = connection.execute('SELECT ra_1 FROM numbers').fetchall()[0][0]

    r_an2 = connection.execute('SELECT ra_2 FROM numbers').fetchall()[0][0]

    r_an3 = connection.execute('SELECT ra_3 FROM numbers').fetchall()[0][0]

    an_string = connection.execute('SELECT answers FROM numbers').fetchall()[0][0]

    an_list = an_string.split(':')

    return [num1, num2, c_an, r_an1, r_an2, r_an3, an_list]


def create_numbers():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    c_an = num1 * num2
    r_an1 = random.randint(1, 100)
    while r_an1 == c_an:
        r_an1 = random.randint(1, 100)
    r_an2 = random.randint(1, 100)
    while r_an2 == c_an or r_an2 == r_an1:
        r_an2 = random.randint(1, 100)
    r_an3 = random.randint(1, 100)
    while r_an3 == c_an or r_an3 == r_an1 or r_an3 == r_an2:
        r_an3 = random.randint(1, 100)
    an_list = [c_an, r_an1, r_an2, r_an3]
    random.shuffle(an_list)

    an_string = ''
    for i in an_list:
        an_string += str(i)
        an_string += ':'

    connection.execute('INSERT INTO numbers VALUES (?, ?, ?, ?, ?, ?, ?)', [num1, num2, c_an, r_an1, r_an2, r_an3, an_string])


def update_numbers():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    c_an = num1 * num2
    r_an1 = random.randint(1, 100)
    while r_an1 == c_an:
        r_an1 = random.randint(1, 100)
    r_an2 = random.randint(1, 100)
    while r_an2 == c_an or r_an2 == r_an1:
        r_an2 = random.randint(1, 100)
    r_an3 = random.randint(1, 100)
    while r_an3 == c_an or r_an3 == r_an1 or r_an3 == r_an2:
        r_an3 = random.randint(1, 100)
    an_list = [c_an, r_an1, r_an2, r_an3]
    random.shuffle(an_list)

    an_string = ''
    for i in an_list:
        an_string += str(i)
        an_string += ':'

    connection.execute('UPDATE numbers SET n1 = ?', [num1])
    connection.execute('UPDATE numbers SET n2 = ?', [num2])
    connection.execute('UPDATE numbers SET c_a = ?', [c_an])
    connection.execute('UPDATE numbers SET ra_1 = ?', [r_an1])
    connection.execute('UPDATE numbers SET ra_2 = ?', [r_an2])
    connection.execute('UPDATE numbers SET ra_3 = ?', [r_an3])
    connection.execute('UPDATE numbers SET answers = ?', [an_string])


is_num = connection.execute('SELECT n1 FROM numbers').fetchall()

if not is_num:
    create_numbers()
    print('true')


def application(environ, start_response):
    number1, number2, c_answer, r_answer1, r_answer2, r_answer3, answers = reset_numbers()

    headers = [('Content-Type', 'text/html; charset=utf-8')]

    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    un = params['username'][0] if 'username' in params else None
    pw = params['password'][0] if 'password' in params else None

    if path == '/register' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken <br> <a href = "/"> HOME </a>'.format(un).encode()]
        elif len(un.split()) > 1 or len(pw.split()) > 1:
            start_response('200 OK', headers)
            return ['Sorry, usernames and passwords should have no spaces in them <br> <a href = "/"> HOME </a>'.format(un).encode()]
        else:
            connection.execute('INSERT INTO users VALUES (?, ?)', [un, pw])
            connection.commit()
            start_response('200 OK', headers)
            page = ''' <!DOCTYPE html>
            <html>
            <head><title>Log in</title></head>
            <body>
            <p> Username {} has has been successfully registered</p>
            <a href = "/"> HOME </a>

            </body></html>
            '''.format(un)
            return [page.encode()]

    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['User {} successfully logged in. <a href="/account">Account</a>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password <br> <a href = "/"> HOME </a>'.encode()]

    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['Logged out. <a href="/">Login</a>'.encode()]

    elif path == '/account':
        if 'HTTP_COOKIE' not in environ:
            start_response('200 OK', headers)
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            start_response('200 OK', headers)
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')

        if 'reset' in params:
            headers.append(('Set-Cookie', '{}_cookies={}:{}'.format(un, 0, 0)))
            print('true')

        if '{}_cookies'.format(un) in cookies:
            correct = int(cookies['{}_cookies'.format(un)].value.split(':')[0])
            incorrect = int(cookies['{}_cookies'.format(un)].value.split(':')[1])

        else:
            correct = 0
            incorrect = 0

        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            page = '''
            <!DOCTYPE html>
            <html>
            <head><title>Multiplication GAME!</title></head>
            <body style = "background-color: lightblue">
            <p> What is {} * {}? </p>
            <p> A: <a href = "/score?answer={}" style = "color: blue;"> {} </a></p>
            <p> B: <a href = "/score?answer={}" style = "color: blue;"> {} </a> </p>
            <p> C: <a href = "/score?answer={}" style = "color: blue;"> {} </a></p>
            <p> D: <a href = "/score?answer={}" style = "color: blue;"> {} </a> </p>
            
            <p> Current Score: Correct = {} Incorrect = {}</p>
                
            <p>Logged in: {}</p>
            <a href="/logout" style = "color: blue;">Logout</a> <br> 
            <a href = "/" style = "color: blue;"> HOME </a> <br>
            <a href = "/account?reset=0" style = "color: blue;"> Reset Scores (Reload Page After)</a> <br>
            </body>
            </html>
            
            '''.format(number1, number2, answers[0], answers[0], answers[1], answers[1], answers[2], answers[2], answers[3], answers[3], correct, incorrect, un)
            start_response('200 OK', headers)
            return [page.encode()]
        else:
            return ['Not logged in. <a href="/">Login</a> <br> <a href = "/"> HOME </a>'.encode()]

    elif path == '/score':
        if 'HTTP_COOKIE' not in environ:
            start_response('200 OK', headers)
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])

        if 'session' not in cookies:
            start_response('200 OK', headers)
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()

        if user:
            headers.append(('Set-Cookie', 'reset_game=1'))
            if 'answer' in params:
                if params['answer'][0] == str(c_answer):
                    cookies = http.cookies.SimpleCookie()
                    cookies.load(environ['HTTP_COOKIE'])

                    if '{}_cookies'.format(un) in cookies:
                        correct = int(cookies['{}_cookies'.format(un)].value.split(':')[0]) + 1
                        incorrect = int(cookies['{}_cookies'.format(un)].value.split(':')[1])
                        username = un
                        headers.append(('Set-Cookie', '{}_cookies={}:{}'.format(username, correct, incorrect)))

                    else:
                        correct = 1
                        incorrect = 0
                        username = un
                        headers.append(('Set-Cookie', '{}_cookies={}:{}'.format(username, correct, incorrect)))

                    page = '''
                    <!DOCTYPE html>
                    <html>
                    <head><title>Multiplication GAME!</title></head>
                    <body style = "background-color: blue">
                    <h1 style = "background-color: lightgreen"> Correct! {} * {} = {} </h1>
                    <h2> Current Score: Correct = {}, Incorrect = {}</h2>

                    <a href="/account" style = "color: red;">Account</a> <br> 
                    <a href = "/" style = "color: red;"> HOME </a>
                    </body>
                    </html>                        
                    '''.format(number1, number2, c_answer, correct, incorrect)

                    update_numbers()
                    start_response('200 OK', headers)
                    return [page.encode()]

                else:

                    cookies = http.cookies.SimpleCookie()
                    cookies.load(environ['HTTP_COOKIE'])

                    if '{}_cookies'.format(un) in cookies:
                        correct = int(cookies['{}_cookies'.format(un)].value.split(':')[0])
                        incorrect = int(cookies['{}_cookies'.format(un)].value.split(':')[1]) + 1
                        username = un
                        headers.append(('Set-Cookie', '{}_cookies={}:{}'.format(username, correct, incorrect)))

                    else:
                        correct = 0
                        incorrect = 1
                        username = un
                        headers.append(('Set-Cookie', '{}_cookies={}:{}'.format(username, correct, incorrect)))

                    page = '''
                    <!DOCTYPE html>
                    <html>
                    <head><title>Multiplication GAME!</title></head>
                    <body style = "background-color: orange">
                    <h1 style = "background-color: red"> Incorrect :( The answer was {} * {} = {} </h1>
                    <h2> Current Score: Correct = {}, Incorrect = {}</h2>

                    <a href="/account" style = "color: blue;">Account</a> <br> 
                    <a href = "/" style = "color: blue;"> HOME </a>
                    </body>
                    </html>                        
                    '''.format(number1, number2, c_answer, correct, incorrect)

                    update_numbers()
                    start_response('200 OK', headers)
                    return [page.encode()]

        else:
            return ['Not logged in. <a href="/">Login</a> <br> <a href = "/"> HOME </a>'.encode()]

    elif path == '/':
        page = '''<!DOCTYPE html>
            <html>
            <head><title>Multiplication GAME!</title></head>
            <body style = "background-color: red">
            <h1>Welcome to the multiplication game! </h1>
            <h2>Make an account or sign in if you have one</h2>
            <h2>Register Account</h2>
            <form action = "/register">
                Username <input type="text" name="username"><br>
                Password <input type="password" name="password"><br>
                <input type="submit">
            </form>

            <h2>Login</h2>
            <form action = "/login">
                Username <input type="text" name="username"><br>
                Password <input type="password" name="password"><br>
                <input type="submit">
            </form>
            <br>
            <a href = "/all_accounts" style = "color: blue;"> All accounts </a>
            </body></html>'''
        start_response('200 OK', headers)

        return [page.encode()]

    elif path == '/all_accounts':
        start_response('200 OK', headers)

        product_cursor = connection.execute('SELECT username FROM users')
        product_list = product_cursor.fetchall()
        return_value = ''''''
        for product in product_list:
            return_value += '<a href = "/account?username={}"> {} </a>'.format(product[0], product)
            if 'HTTP_COOKIE' in environ:
                cookies = http.cookies.SimpleCookie()
                cookies.load(environ['HTTP_COOKIE'])
                if 'session' in cookies:
                    if cookies['session'].value.split(':')[0] == product[0]:
                        return_value += ' Logged In'

            return_value += '<br> <br>'
        return_value += '<a href = "/"> HOME </a>'

        return [return_value.encode()]

    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found <br> <a href = "/"> HOME </a>'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()