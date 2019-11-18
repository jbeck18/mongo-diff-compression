import pymongo
from pymongo import MongoClient
from bson import ObjectId
import copy
from datetime import datetime as dt
import threading

client = MongoClient()

db = client['main']

data = db['data']
history = db['history']
history_uncompressed = db['history_uncompressed']

from parser import Parser
from merger import Merger

def insert_one(document: dict):
    data.insert_one(document)

def update_one(query: dict, update: dict, upsert:bool=False):
    old_doc: dict = data.find_one_and_update(query, update, upsert=upsert)

    if not old_doc:
        return None

    def wrapper():
        current_doc: dict = data.find_one({ '_id': old_doc['_id'] })

        if old_doc == current_doc:
            return

        c = Parser()
        history_doc = c.parse(old_doc, current_doc)
        history_doc['ref'] = current_doc['_id']
        history.insert_one(history_doc)

        # For testing
        temp = copy.deepcopy(current_doc)
        temp['ref'] = temp['_id']
        del temp['_id']
        history_uncompressed.insert_one(temp)

    t1 = threading.Thread(target=wrapper)
    t1.start()

    return old_doc


"""
Returns the current document and the previous `num_changes` modifications to the document
"""
def get_history(id:ObjectId, num_changes:int=None):
    hist = history.find({ 'ref': id }).sort('_id', direction=pymongo.DESCENDING)
    curr = data.find_one({ '_id': id })

    yield curr

    prev = curr
    count = 0
    merger = Merger()
    for d in hist:
        if num_changes and count == num_changes:
            break

        d['ref_creation_time'] = d['_id'].generation_time
        del d['_id']
        del d['ref']

        l: dict = copy.deepcopy(prev)
        merger.merge_changes(l, d)

        yield l
        prev = l
        count+=1
