# Scalable-Database
This microservice provides a simple way to save information to a database without having to build your own database schema from scratch.
## Communcication Contract
### How to Programmatically REQUEST Data
To request a database operation reuest to be sent, you need to send a JSON message to the microservice using ZeroMQ (ZMQ). Here are the steps:

1. Install the required library
`python3 -m pip install pyzmq`

2. Use the following Python code to send a database request:
```python
import zmq

def database_request(username, password, actionType, fileName, data):
    context = zmq.Context()

    #  Socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    entry = {"name": username,
            "pass": password,
            "action": actionType,
            "note_name": fileName,
            "data_contents": data,
            }

    socket.send_json(entry)

    response = socket.recv_json()
    print(f"Server response: {response}")

# Example Calls
database_request("John", "Tester", "create", "Meeting", data = {"Minutes": "30", "Topic": "Feature", "Due": "9/13/24"})
database_request("John", "Tester", "insert", "Meeting", data = {"Minutes": "45", "Topic": "Feature", "Due": "10/05/24"})
database_request("John", "Tester", "update", "Meeting", data = {"Minutes": "30", "Topic": "Feature", "Due": "9/13/24"})
database_request("John", "Tester", "select", "Meeting", data = {"Minutes": "30", "Topic": "Feature", "Due": "9/13/24"})
database_request("John", "Tester", "delete", "Meeting", data = {"Minutes": "30", "Topic": "Feature", "Due": "9/13/24"})


```
This function sends a database request to the microservice. The result of the operation will be sent back upon completion of the database operation. 

**NOTE:** You will need to make a call with the action parameter `create` as seen in the first example call in your *first call* in order for any of the other action types to work.

### How to Programmatically RECEIVE Data
The microservice sends a confirmation message when a database operation is executed, reflection the type of operation in it's response, but in the case of the `select` action, it will respond with a list of all your tables.

1. Use the following Python code to set up the receiver:
```python
#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

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

# Call this function to start receiving confirmation of database operations
request_processor()
```

This function sets up a database and listens for messages requesting database operations be performed, and upon receiving a request, identifies which database operation to perform and sends back confirmation of the result of the request as well as printing out the request in console.

## UML Sequence Diagram
