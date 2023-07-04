import requests
import utils
import socketio
from diffiehellman import DiffieHellman
from threading import Lock
import time
import json

is_reconnect = False

myusername = None
mypassword = None
myprivatekey = None

session = requests.session()
sio = socketio.Client(http_session=session, ssl_verify=False)

session_keys = {}
session_key_numbers = {}
public_keys = {}
group_session_keys = {}
group_session_key_numbers = {}
messages = {}
group_messages = {}
group_public_keys = {}
group_users = {}
group_owners = {}

key_exchange_lock = Lock()
group_key_exchange_lock = Lock()

left_group = False

def init_check_user_data(username):
    if username not in public_keys:
        getpublickey(username)
    if username not in session_key_numbers:
        session_key_numbers[username] = 0
    if username not in session_keys:
        session_keys[username] = {}
    if username not in messages:
        messages[username] = {}

def init_check_group_data(group_name):
    if group_name not in group_session_key_numbers:
        group_session_key_numbers[group_name] = 0
    if group_name not in group_session_keys:
        group_session_keys[group_name] = {}
    if group_name not in group_messages:
        group_messages[group_name] = {}
    if group_name not in group_public_keys:
        group_public_keys[group_name] = {}
    if group_name not in group_users:
        group_users[group_name] = []
    if group_name not in group_owners:
        group_owners[group_name] = None

# set up base url
BASE_URL = 'http://localhost:5000'


def register(username, password):
    url = BASE_URL + '/auth/register'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    print(response.text)



def login(username, password):
    global myusername, mypassword, is_reconnect
    url = BASE_URL + '/auth/login'
    data = {'username': username, 'password': password}
    response = session.post(url, json=data)
    print(response.text)
    myusername = username
    mypassword = password
    is_reconnect = True
    sio.disconnect()
    sio.connect(BASE_URL)
    is_reconnect = False


def logout():
    global is_reconnect
    
    is_reconnect = True
    sio.disconnect()
    url = BASE_URL + '/auth/logout'
    response = session.post(url, json={})
    print(response.text)
    sio.connect(BASE_URL)
    is_reconnect = False


def publishkey(username, password):
    key = utils.get_rsa_key(username, password)
    url = BASE_URL + '/user/publish_key'

    data = {
        'public_key': key.publickey().export_key().decode('utf-8')
    }
    # , headers={'Content-Type': 'application/x-www-form-urlencoded'}
    response = session.post(url, data)
    # print(response.text)


def getpublickey(username):
    url = BASE_URL + '/user/get_public_key'
    data = {'username': username}
    response = session.post(url, json=data)
    public_keys[username] = response.text

def getonlineusers():
    url = BASE_URL + '/user/get_online_users'
    response = session.get(url)
    print(response.text)

def key_exchange_0(username):
    key_exchange_lock.acquire()
    # generate session key
    print('\nkey_exchange_0')

    init_check_user_data(username)

    session_key_numbers[username] += 1
    messages[username][session_key_numbers[username]] = []

    dh1 = DiffieHellman(group=14, key_bits=540)
    dh1_public = dh1.get_public_key()
    key_number = session_key_numbers[username]
    session_keys[username][key_number] = {
        'dh': dh1,
        'shared_key': None
    }
    messages[username][key_number] = []

    message_obj = {
        'message': dh1_public,
        'type': 'key_exchange_1',
        'key_number': key_number
    }
    sio.emit('send_message', {'message': message_obj, 'room': username})

def key_exchange_1(username, key_number, dh1_public):
    print('\nkey_exchange_1')
    
    init_check_user_data(username)

    dh2 = DiffieHellman(group=14, key_bits=540)
    dh2_public = dh2.get_public_key()
    dh2_shared = dh2.generate_shared_key(dh1_public)

    session_key_numbers[username] = key_number

    session_keys[username][key_number] = {
        'dh': dh2,
        'shared_key': dh2_shared[:32]
    }
    messages[username][key_number] = []
    message_obj = {
        'message': dh2_public,
        'type': 'key_exchange_2',
        'key_number': key_number
    }
    sio.emit('send_message', {'message': message_obj, 'room': username})

def key_exchange_2(username, key_number, dh2_public):
    
    print('\nkey_exchange_2')
    dh3 = session_keys[username][key_number]['dh']
    dh3_shared = dh3.generate_shared_key(dh2_public)
    messages[username][key_number] = []
    session_keys[username][key_number] = {
        'dh': dh3,
        'shared_key': dh3_shared[:32]
    }
    key_exchange_lock.release()

def key_exchange_group_0(group_name):
    print('\nkey_exchange_group 0')
    init_check_group_data(group_name)
    group_key_exchange_lock.acquire()
    session_key = utils.get_symmetric_key()
    group_session_key_numbers[group_name] += 1
    key_number = group_session_key_numbers[group_name]
    group_session_keys[group_name][key_number] = session_key
    group_encrypted_session_keys = {}
    for username in group_users[group_name]:
        group_encrypted_session_keys[username] = utils.encrypt_session_key(session_key, public_keys[username])
    message = {
        'message': group_encrypted_session_keys,
        'key_number': key_number
    }
    message_obj = {
        'message': message,
        'type': 'key_exchange_group_1',
        'group_name': group_name
    }
    sio.emit('send_group_message', {'message': message_obj, 'group_name': group_name})
    group_key_exchange_lock.release()

def key_exchange_group_1(group_name, group_encrypted_session_keys, key_number):
    print('\nkey_exchange_group 1')
    init_check_group_data(group_name)
    group_session_key_numbers[group_name] = key_number
    enc_key_session = group_encrypted_session_keys[myusername]
    myprivatekey = utils.get_rsa_key(myusername, mypassword).export_key()
    session_key = utils.decrypt_session_key(enc_key_session, myprivatekey)
    group_session_keys[group_name][key_number] = session_key
    # group_key_exchange_lock.release()



def send_message(username):

    init_check_user_data(username)

    while True:
        
        last_key_number = session_key_numbers[username]
        if last_key_number == 0 or len(messages[username][last_key_number]) >= 10:
            key_exchange_0(username)
            key_exchange_lock.acquire()
            key_exchange_lock.release()
        message = input('send to ' + username + ': ')
        if message == 'exit':
            return
        
        last_key_number = session_key_numbers[username]
        session_key = session_keys[username][last_key_number]['shared_key']
        public_key = public_keys[username]
        messages[username][last_key_number].append({"sender": myusername, "message": message})
        nonce, tag, ciphertext = utils.encrypt_message_symmetric(message, session_key)
        message = {
            'nonce': nonce,
            'tag': tag,
            'ciphertext': ciphertext
        }
        rsa_key_bin = utils.get_rsa_key(myusername, mypassword)
        private_key = rsa_key_bin.export_key()
        signed_message = utils.sign_message(ciphertext, private_key)
        message_obj = {
            'message': message,
            'signature': signed_message,
            'type': 'normal',
            'key_number': last_key_number
        }
        sio.emit('send_message', {'message': message_obj, 'room': username})

def send_group_message(group_name):
    init_check_group_data(group_name)
    while True:
        last_key_number = group_session_key_numbers[group_name]
        owner = group_owners[group_name]
        if myusername == owner and (last_key_number == 0 or len(group_messages[group_name][last_key_number]) >= 10):
            key_exchange_group_0(group_name)
            group_key_exchange_lock.acquire()
            group_key_exchange_lock.release()
        message = input('send to ' + group_name + ': ')
        if message == 'exit':
            sio.emit('leave_group_chat', {'group_name': group_name})
            return
        last_key_number = group_session_key_numbers[group_name]
        if last_key_number not in group_session_keys[group_name]:
            group_session_keys = utils.get_random_bytes()
        session_key = group_session_keys[group_name][last_key_number]
        if group_name not in group_messages:
            group_messages[group_name] = {}
        if last_key_number not in group_messages[group_name]:
            group_messages[group_name][last_key_number] = []
        group_messages[group_name][last_key_number].append({"sender": myusername, "message": message})
        nonce, tag, ciphertext = utils.encrypt_message_symmetric(message, session_key)
        message = {
            'nonce': nonce,
            'tag': tag,
            'ciphertext': ciphertext
        }
        rsa_key_bin = utils.get_rsa_key(myusername, mypassword)
        private_key = rsa_key_bin.export_key()
        signed_message = utils.sign_message(ciphertext, private_key)
        message_obj = {
            'message': message,
            'signature': signed_message,
            'type': 'normal',
            'key_number': last_key_number
        }
        sio.emit('send_group_message', {'message': message_obj, 'group_name': group_name})

def chat(username):
    sio.emit('join', {'room': username})
    send_message(username)
    sio.emit('leave', {'room': username})

def create_group(group_name):
    url = BASE_URL + '/group/create_group'
    data = {'group_name': group_name}
    response = session.post(url, json=data)
    print(response.text)

def invite_user(group_name, username):
    url = BASE_URL + '/group/invite_user'
    data = {'group_name': group_name, 'username': username}
    response = session.post(url, json=data)
    print(response.text)

def get_groups():
    url = BASE_URL + '/group/get_groups'
    response = session.get(url)
    print(response.text)

def get_group_users(group_name):
    url = BASE_URL + '/group/group_users/' + group_name
    response = session.get(url)
    print('group users: ' + response.text)
    return response.text

def delete_group(group_name):
    url = BASE_URL + '/group/delete_group'
    data = {'group_name': group_name}
    response = session.post(url, json=data)
    print(response.text)

def remove_user(group_name, username):
    url = BASE_URL + '/group/remove_user'
    data = {'group_name': group_name, 'username': username}
    response = session.post(url, json=data)
    print(response.text)

def promote_user(group_name, username):
    url = BASE_URL + '/group/promote_user'
    data = {'group_name': group_name, 'username': username}
    response = session.post(url, json=data)
    print(response.text)

def demote_user(group_name, username):
    url = BASE_URL + '/group/demote_user'
    data = {'group_name': group_name, 'username': username}
    response = session.post(url, json=data)
    print(response.text)

def leave_group(group_name):
    url = BASE_URL + '/group/leave_group'
    data = {'group_name': group_name}
    response = session.post(url, json=data)
    print(response.text)

def group_chat(group_name):
    owner = get_group_owner(group_name)
    group_owners[group_name] = owner
    get_users_public_keys(group_name)
    sio.emit('join_group_chat', {'group_name': group_name})
    time.sleep(5)

def get_group_owner(group_name):
    url = BASE_URL + '/group/get_group_owner'
    data = {'group_name': group_name}
    response = session.post(url, json=data)
    print('group owner: ' + response.text)
    return response.text

def get_users_public_keys(group_name):
    users = json.loads(get_group_users(group_name))
    group_users[group_name] = users
    for username in users:
        getpublickey(username)
    
    group_public_keys[group_name] = {}
    for username in users:
        group_public_keys[group_name][username] = public_keys[username]
    


def processCommand(command, args):
    if command == 'register':
        register(args[0], args[1])
    elif command == 'login':
        login(args[0], args[1])
    elif command == 'logout':
        logout()
    elif command == 'publish_key':
        publishkey(args[0], args[1])
    elif command == 'get_public_key':
        getpublickey(args[0])
    elif command == 'get_online_users':
        getonlineusers()
    elif command == 'chat':
        chat(args[0])
    elif command == 'create_group':
        create_group(args[0])
    elif command == 'invite_user':
        invite_user(args[0], args[1])
    elif command == 'get_groups':
        get_groups()
    elif command == 'get_group_users':
        get_group_users(args[0])
    elif command == 'delete_group':
        delete_group(args[0])
    elif command == 'remove_user':
        remove_user(args[0], args[1])
    elif command == 'leave_group':
        leave_group(args[0])
    elif command == 'promote_user':
        promote_user(args[0], args[1])
    elif command == 'demote_user':
        demote_user(args[0], args[1])
    elif command == 'group_chat':
        group_chat(args[0])
    elif command == 'get_group_owner':
        get_group_owner(args[0])
    elif command == 'exit':
        sio.disconnect()
        exit()
    else:
        print('invalid command')


@sio.on('connect')
def on_connect():
    if not is_reconnect:
        print('\nconnected to server')

@sio.on('disconnect')
def on_disconnect():
    if not is_reconnect:
        print('\ndisconnected from server')

@sio.on('join')
def on_join(data):
    pass

@sio.on('logged_in')
def on_logged_in(data):
    print('\n' + data)
    
@sio.on('logged_out')
def on_logged_out(data):
    print('\n' + data)

@sio.on('join_group_chat')
def on_join_group_chat(data):
    if data['username'] == myusername:
        send_group_message(data['group_name'])
    else:
        print('\n' + data['message'])

@sio.on('leave_group_chat')
def on_leave_group_chat(data):
    print('\n' + data)


@sio.on('receive_message')
def on_receive_message(message):
    username = message['sender']
    if username not in public_keys:
        getpublickey(username)
    if username == myusername:
        return
    message = message['message']
    if message['type'] == 'key_exchange_1':
        key_number = int(message['key_number'])
        dh1_public = message['message']
        key_exchange_1(username, key_number, dh1_public)
    elif message['type'] == 'key_exchange_2':
        key_number = int(message['key_number'])
        dh2_public = message['message']
        key_exchange_2(username, key_number, dh2_public)
    elif message['type'] == 'normal':
        key_number = int(message['key_number'])
        session_key = session_keys[username][key_number]['shared_key']
        signature = message['signature']
        
        if not utils.verify_signature(message['message']['ciphertext'], signature, public_keys[username]):
            print('signature not verified')
            return

        message = message['message']
        nonce = message['nonce']
        tag = message['tag']
        ciphertext = message['ciphertext']
        decrypted = utils.decrypt_message_symmetric(nonce, tag, ciphertext, session_key)
        messages[username][key_number].append({"sender": username, "message": decrypted})
        print(username + ': ' + decrypted)

@sio.on('receive_group_message')
def on_receive_group_message(data):
    group_name = data['group_name']
    sender = data['sender']
    message = data['message']
    type = message['type']
    if sender == myusername:
        return
    elif type == 'key_exchange_group_1':
        message = message['message']
        key_number = int(message['key_number'])
        enc_session_keys = message['message']
        key_exchange_group_1(group_name, enc_session_keys, key_number)
    elif type == 'normal':
        init_check_group_data(group_name)
        print(message)
        key_number = int(message['key_number'])
        signature = message['signature']
        message = message['message']
        if not utils.verify_signature(message['ciphertext'], signature, group_public_keys[group_name][sender]):
            print('signature not verified')
            return
        nonce = message['nonce']
        tag = message['tag']
        ciphertext = message['ciphertext']
        if len(group_session_keys[group_name]) == 0:
            print('no session key')
            return
        session_key = group_session_keys[group_name][key_number]
        decrypted = utils.decrypt_message_symmetric(nonce, tag, ciphertext, session_key)
        if key_number not in group_messages[group_name]:
            group_messages[group_name][key_number] = []
        group_messages[group_name][key_number].append({"sender": sender, "message": decrypted})
        print('[' + group_name + '] ' + sender + ': ' + decrypted)



if __name__ == '__main__':

    sio.connect(BASE_URL)

    while True:
        command = input('>>> ')
        command = command.split(' ')
        processCommand(command[0], command[1:])
    # sio.disconnect()
