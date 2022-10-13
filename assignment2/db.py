import os
import sqlite3

# From: https://goo.gl/YzypOI


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secure a connection with the database and 
        store it in the instance variable `conn`
        """
        self.conn = sqlite3.connect(
            "venmo.db", check_same_thread=False
        )
        self.delete_user_table()
        self.create_user_table()

    def create_user_table(self):
        """
        Create a user table using SQL
        """
        cursor = self.conn.execute("""
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                balance REAL,
                password TEXT
            );
        """)

    def delete_user_table(self):
        """
        Delete a user table using SQL
        """
        self.conn.execute("DROP TABLE IF EXISTS user;")

    def get_all_users(self):
        """
        Get all users' id, name, and username using SQL
        """
        cursor = self.conn.execute("""
            SELECT id, name, username FROM user; 
        """)
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def create_user(self, name, username, balance):
        """
        Create a user with name, username, and balance using SQL. 
        Assume balance is 0 if no input. 
        """
        cursor = self.conn.execute("""
            INSERT INTO user (name, username, balance) VALUES (?, ?, ?);
        """, (name, username, balance)
        )
        self.conn.commit()
        return cursor.lastrowid

    def set_password(self,id, input_password): 
        """
        set password to the database for user of a specific id
        """
        cursor = self.conn.execute("""
            UPDATE user SET password = ? WHERE id = ?;
        """, (input_password, id))
        self.conn.commit() 


    def get_user_by_id(self, id):
        """
        Get a user from the database by their id using SQL
        """
        cursor = self.conn.execute("""
            SELECT * FROM user WHERE id= ?;
        """, (id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}

        return None

    def delete_user_by_id(self, id):
        """
        Delete a user from the database by their id using SQL
        """
        cursor = self.conn.execute("""
        DELETE FROM user WHERE id = ?;
        """, (id,))
        self.conn.commit()

    def get_balance(self, id):
        """
        Helper function for send_money to get the current balance of user
        using SQL
        """
        cursor = self.conn.execute("""
        SELECT balance FROM user WHERE id = ?;
        """, (id,))
        for row in cursor:
            return row[0]
        return 0

    def send_money(self, sender, receiver, amount):
        """
        Change balance of sender and receiver based on amount using SQL
        """
        self.conn.execute("""
        UPDATE user SET balance = ? where id = ?; 
        """, ((self.get_balance(sender) - amount), sender))
        self.conn.execute("""
        UPDATE user SET balance = ? where id = ?;
        """, ((self.get_balance(receiver) + amount), receiver))

    def verify_password(self, id, input_password): 
        """
        Verify the password of the user with the given id
        """
        cursor = self.conn.execute("""
        SELECT password FROM user WHERE id = ?;
        """,(id,))

        for row in cursor:
            return row[0]==input_password
        
        return False

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
