from flask import Flask, render_template, jsonify, request
from dataclasses import dataclass, asdict
import uuid
from urllib.parse import urlparse

app = Flask(__name__)
endpoint = "http://127.0.0.1:5000"

@dataclass
class TodoItem(object):
    id : str
    text : str
    done : bool = False

class TodoList(object):
    def __init__(self, items : list[TodoItem] = None):
        self.items = {}
        if items != None:
            self.add_items(items)

    def add_items(self, items : list):
        for item in items:
            self.items[item.id] = item

    def change_item_state(self, id: str, new_state: bool):
        # print (id)
        # print (self.items_to_list())
        if id in self.items:
            self.items[id].done = new_state
            # print( " ".join(["Item", str(id), "(", str(self.items[id].text) ,")", "is now", str(new_state) ] ))

    def remove_items(self, ids: list[str]):
        for id in ids:
            if id in self.items:
                del self.items[id]
    
    def items_to_list(self):
        out = []
        for id in self.items.keys():
            out.append(asdict( self.items[id] ))
        return out
    
    def get_cleared_items(self):
        out = []
        for item in self.items:
            if item.done:
                out.append(item)
        return out

def make_todo_items(text : list[str]) -> list[TodoItem]:
    items = []
    for item in text:
        items.append(TodoItem(str(uuid.uuid4()), item))
    return items

todo_text = [
    "Go to store", 
    "Buy some eggs",
    "Have a good time"
]

todo_object = TodoList()

@app.before_first_request
def setup():
    items = make_todo_items(todo_text)
    todo_object.add_items(items)

@app.route("/todo/")
def render_todo():
    url = urlparse(request.base_url)
    host = url[0] + "://" + url[1]
    print (host)
    return render_template("index.html", todo_items=todo_object.items_to_list(), endpoint=host)

@app.route("/todo/update/<string:statechanged>", methods=["POST"])
def update_todo(statechanged):
    json = request.json
    todo_object.change_item_state(statechanged, json["state"])
    return ""

@app.route("/todo/delete/<string:todelete>", methods=["POST"])
def delete_todo(todelete):
    todo_object.remove_items([todelete])
    return ""

@app.route("/todo/deletemany/", methods=["POST"])
def delete_several():
    json = request.json
    todo_object.remove_items(json["to_delete"])
    return ""

@app.route("/todo/get-cleared/", methods=["GET"] )
def get_cleared():
    ids = [x.id for x in todo_object.get_cleared_items()]
    return { "cleared": ids }

@app.route("/todo/add/", methods=["POST"])
def add_todo():
    json = request.json
    new_item = (TodoItem(str(uuid.uuid4()), json["text"]))
    todo_object.add_items([ new_item ])
    return asdict(new_item)