import zmq
import sqlite3

def request_processor():

    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        # Wait for next request from client
        message = socket.recv_json()
        print(f"Received request: {message}")

        action = message.get('action')
        note_name = message.get('note_name')
        data_contents = message.get('data_contents', {})

        result = {"error": "Invalid action"}

        if action == 'create':
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{note_name}" ({', '.join([f'{k} TEXT' for k in data_contents.keys()])})''')
            conn.commit()
            result = f"Table '{note_name}' created."

        elif action == 'insert':
            columns = ', '.join(data_contents.keys())
            placeholders = ':' + ', :'.join(data_contents.keys())
            cursor.execute(f'''INSERT INTO "{note_name}" ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING''', data_contents)
            conn.commit()
            result = f"Data inserted into '{note_name}'."

        elif action == 'update':
            update_statements = ', '.join([f'{k}=:{k}' for k in data_contents.keys()])
            cursor.execute(f'''UPDATE "{note_name}" SET {update_statements} WHERE rowid IN (SELECT rowid FROM "{note_name}" ORDER BY rowid DESC LIMIT 1)''', data_contents)
            conn.commit()
            result = f"Updated '{note_name}'."

        elif action == 'delete':
            cursor.execute(f'DELETE FROM "{note_name}"')
            conn.commit()
            result = f"Deleted '{note_name}'."

        elif action == 'select':
            # Fetch all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            result = [table[0] for table in tables]

        else:
            result = {"error": "Invalid action"}

        # Send reply back to client
        socket.send_json({"result": result})

request_processor()