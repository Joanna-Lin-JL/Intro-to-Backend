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
        self.delete_transactions_table()
        self.create_user_table()
        self.create_transactions_table()

    def create_user_table(self):
        """
        Create a user table using SQL
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                balance REAL
            );
        """)

    def delete_user_table(self):
        """
        Delete a user table using SQL
        """
        self.conn.execute("DROP TABLE IF EXISTS user;")

    def create_transactions_table(self):
        """
        Create the transactions table using SQL
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                timestamp TEXT NOT NULL, 
                sender_id INTEGER SECONDARY KEY NOT NULL,
                receiver_id INTEGER SECONDARY KEY NOT NULL,
                amount REAL NOT NULL,
                message TEXT,
                accepted BOOL
            );
        """)

    def delete_transactions_table(self):
        """
        Delete a transactions table using SQL
        """
        self.conn.execute("DROP TABLE IF EXISTS transactions;")

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

    def get_user_transactions(self, user_id):
        """
        Get all transactions that involve user with id = user_id using SQL
        """
        cursor = self.conn.execute("""
        SELECT * FROM transactions WHERE sender_id = ?; 
        """, (user_id,))
        txns = []
        for row in cursor:
            if (row[6] is None):
                accepted = None
            else:
                accepted = bool(row[6])
            txns.append({
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5],
                "accepted": accepted
            })
        cursor = self.conn.execute("""
        SELECT * FROM transactions WHERE receiver_id = ?; 
        """, (user_id,))
        for row in cursor:
            if (row[6] is None):
                accepted = None
            else:
                accepted = bool(row[6])
            txns.append({
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5],
                "accepted": accepted
            })
        return txns

    def get_user_by_id(self, id):
        """
        Get a user from the database by their id using SQL
        """
        cursor = self.conn.execute("""
            SELECT * FROM user WHERE id= ?;
        """, (id,))
        for row in cursor:
            return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "balance": row[3],
                "transactions": self.get_user_transactions(id)
            }

        return None

    def delete_user_by_id(self, id):
        """
        Delete a user from the database by their id using SQL
        """
        cursor = self.conn.execute("""
        DELETE FROM user WHERE id = ?;
        """, (id,))
        self.conn.execute("""
        DELETE FROM transactions WHERE sender_id = ?;
        """, (id,))
        self.conn.execute("""
        DELETE FROM transactions WHERE receiver_id = ?;
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
        return -1

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
        self.conn.commit()

    def create_transactions(self, sender, receiver, timestamp, amount, message, accepted):
        """
        Create a transaction by sending or requesting money using SQL
        """
        cursor = self.conn.execute("""
        INSERT INTO transactions (timestamp, sender_id, receiver_id, amount, 
        message, accepted) VALUES (?, ?, ?, ?, ?, ?);
        """, (timestamp, sender, receiver, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid

    def get_transaction(self, id):
        """
        Get the transaction info given the id using SQL
        """
        cursor = self.conn.execute("""
        SELECT * FROM transactions WHERE id = ?; 
        """, (id,))
        for row in cursor:
            if (row[6] is None):
                accepted = None
            else:
                accepted = bool(row[6])
            return {
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5],
                "accepted": accepted
            }

        return None

    def update_transaction(self, id, timestamp, accepted):
        """
        Update the timestamp and accept status for the transaction using SQL
        """
        self.conn.execute("""
        UPDATE transactions SET timestamp = ? WHERE id = ?;
        """, (timestamp, id))
        self.conn.execute("""
        UPDATE transactions SET accepted = ? WHERE id = ?;
        """, (accepted, id))
        self.conn.commit()


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
