import requests
import utils
import socketio
import sys
import asyncio

myusername = None
mypassword = None

session = requests.session()
sio = socketio.Client(http_session=session)

# set up base url
BASE_URL = 'http://localhost:5000'
public_keys = {}


def register(username, password):
    url = BASE_URL + '/auth/register'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    print(response.text)



def login(username, password):
    url = BASE_URL + '/auth/login'
    data = {'username': username, 'password': password}
    response = session.post(url, json=data)

    # sio.emit('login')
    print(response.text)


def logout(username):
    url = BASE_URL + '/auth/logout'
    data = {'username': username}
    response = session.post(url, json=data)
    # sio.emit('logout')
    print(response.text)



def publishkey(username, password):
    key = utils.get_rsa_key(username, password)
    url = BASE_URL + '/user/publish_key'

    data = {
        'public_key': key.publickey().export_key().decode('utf-8')
    }
    # , headers={'Content-Type': 'application/x-www-form-urlencoded'}
    response = session.post(url, data)
    print(response.text)


def getpublickey(username):
    url = BASE_URL + '/user/get_public_key'
    data = {'username': username}
    response = session.post(url, json=data)
    public_keys[username] = response.text
    print(response.text)

def getonlineusers():
    url = BASE_URL + '/user/get_online_users'
    response = session.get(url)
    print(response.text)

def chat(username):
    getpublickey(username)
    public_key = public_keys[username]
    sio.emit('chat', {'username': username, 'public_key': public_key})

def processCommand(command, args):
    print(session.cookies.get_dict())
    if command == 'register':
        register(args[0], args[1])
    elif command == 'login':
        login(args[0], args[1])
    elif command == 'logout':
        logout(args[0])
    elif command == 'publish_key':
        publishkey(args[0], args[1])
    elif command == 'get_public_key':
        getpublickey(args[0])
    elif command == 'get_online_users':
        getonlineusers()
    elif command == 'chat':
        chat(args[0])
    elif command == 'exit':
        sio.disconnect()
        exit()
    else:
        print('invalid command')


@sio.on('connect')
def on_connect():
    print('connected to server')

@sio.on('disconnect')
def on_disconnect():
    print('disconnected from server')




if __name__ == '__main__':

    sio.connect(BASE_URL)

    while True:
        command = input('>>> ')
        command = command.split(' ')
        processCommand(command[0], command[1:])
    sio.disconnect()
