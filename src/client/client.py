import click
import requests
import utils
import json
import pickle
import chardet



session = requests.session()

# set up base url
BASE_URL = 'http://localhost:5000'

# handle subcommands
@click.group()
def cli():
    pass

# subcommand: register
@cli.command()
@click.argument('username')
@click.argument('password')
def register(username, password):
    url = BASE_URL + '/auth/register'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    print(response.text)

# subcommand: login
@cli.command()
@click.argument('username')
@click.argument('password')
def login(username, password):
    url = BASE_URL + '/auth/login'
    data = {'username': username, 'password': password}
    response = session.post(url, json=data)
    print(response.text)
    print(response.cookies.get_dict())

    with open('cookies.pkl', 'wb') as f:
        pickle.dump(session.cookies, f)
        print('session saved')

# subbcommand: logout
@cli.command()
@click.argument('username')
def logout(username):
    url = BASE_URL + '/auth/logout'
    data = {'username': username}
    response = session.post(url, json=data)

    print(response.text)

# subcommand: publish_key
@cli.command()
@click.argument('password')
def publishkey(password):
    key = utils.get_rsa_key(password)
    url = BASE_URL + '/user/publish_key'

    data = {
        'public_key': key.publickey().export_key().decode('utf-8')
    }
    # , headers={'Content-Type': 'application/x-www-form-urlencoded'}
    response = session.post(url, data)

# subcommand: get_public_key
@cli.command()
@click.argument('username')
def getpublickey(username):
    url = BASE_URL + '/user/get_public_key'
    data = {'username': username}
    response = session.post(url, json=data)
    print(response.text)

# subcommand: get_online_users
@cli.command()
def getonlineusers():
    url = BASE_URL + '/user/get_online_users'
    response = session.get(url)
    print(response.text)

# add subcommands
cli.add_command(register)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(publishkey)




if __name__ == '__main__':
    # load sessions
    try:
        with open('cookies.pkl', 'rb') as f:
            session.cookies.update(pickle.load(f))
            print('session loaded')
    except FileNotFoundError:
        print('session empty')
    print('session cookies:', session.cookies.get_dict())
    cli()
