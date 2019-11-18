from operations import *
from bson import ObjectId
import datetime
import random
import time

#insert_one({'a': 1})
#update_one({ '_id': ObjectId('5dd015e0571a1298101a5cf3') }, { '$set': {'b': 75} })

keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']
def get_random_key():
    return keys[random.randint(0, len(keys)-1)]

def get_random_update():
    num_of_updates = random.randint(1, 7)
    res = {}
    for _ in range(num_of_updates):
        key = get_random_key()
        while key in res.keys():
            key = get_random_key()

        res[key] = random.randint(0, 10000)

    return res


start = time.time()
for _ in range(1):
    #update_one({ '_id': ObjectId('5dd1e69aecfb53460573ccf9') }, { '$set': get_random_update() })
    pass
end = time.time()
#print(end-start)


update_one({ '_id': ObjectId('5dd2bd21ecfb53460573ccfe') }, { '$set': {'key': 100 } })


start = time.time()
for d in get_history(ObjectId('5dd2bd21ecfb53460573ccfe'), num_changes=10):
    if 'ref_creation_time' in d:
        time_ = d['ref_creation_time']
        del d['ref_creation_time']
    else:
        time_ = datetime.datetime.utcnow()

    print(f'At {time_}: {d}')


end = time.time()
print(end-start)