import click
import requests
import json

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
    response = requests.post(url, json=data)
    print(response.text)

# subbcommand: logout
@cli.command()
@click.argument('username')
def logout(username):
    url = BASE_URL + '/auth/logout'
    data = {'username': username}
    response = requests.post(url, json=data)
    print(response.text)

# add subcommands


if __name__ == '__main__':
    cli()
