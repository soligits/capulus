import time

online_users = {}

def heartbeat():
    while True:
        time.sleep(10)
        for user in online_users:
            if time.time() - online_users[user] > 300:
                del online_users[user]