#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

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

