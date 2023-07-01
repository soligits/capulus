from db import DataBase

def init_db():
    """
    Clear the existing data and create new tables.
    """
    db = DataBase()
    db.init_db()
    print('Initialized the database.')
    db.close()

if __name__ == '__main__':
    init_db()