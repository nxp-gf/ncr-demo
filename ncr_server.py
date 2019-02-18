#!/usr/bin/env python
from flask import Flask, send_from_directory
from flask_restful import reqparse, abort, Api, Resource, request
import json, math, threading,time

parser = reqparse.RequestParser()

app = Flask(__name__)
api = Api(app)
parser.add_argument('id', type=str, location='args')
parser.add_argument('end', type=str, location='args')

CAMERA_ID_ENTRANCE = 0
CAMERA_ID_EXIT     = 1
CAMERA_ID_SHELF1   = 2
CAMERA_ID_SHELF2   = 3
CAMERA_NUMBER      = 4

customer_tmp_db = [[] for x in range(CAMERA_NUMBER)]
latest_time = [0 for x in range(CAMERA_NUMBER)]

FACE_RECOGNITION_THRES = 0.71
def feature_is_same_people(f1, f2):
    if (len(f1) != len(f1)):
        return False
    ret = 0.0
    mod1 = 0.0
    mod2 = 0.0
    for i in range(len(f1)):
       ret += f1[i] * f2[i];
       mod1 += f1[i] * f1[i];
       mod2 += f2[i] * f2[i];
    ret = (ret / math.sqrt(mod1) / math.sqrt(mod2) + 1) / 2.0
    print (ret)
    if (ret > FACE_RECOGNITION_THRES):
        return True
    else:
        return False

def db_update_thread():
    while(True):
        time.sleep(0.2)

        #The camera for entrance
        db = customer_tmp_db[CAMERA_ID_ENTRANCE]
        latest = latest_time[CAMERA_ID_ENTRANCE]
        for people in db:
             if (people['count'] < 3 and latest - people['latest_time'] >= 2):
                 print("Delete fault alert")
                 db.remove(people)
             if (people['count'] >= 3 and latest - people['latest_time'] >= 2):
                 print("People enter")
            

threading.Thread(target = db_update_thread, args =()).start()

class GetFeature(Resource):
    def get(self):
        return {'state':'SUCCESS'}, 200

    def delete(self):
        return {'state':'SUCCESS'}, 200

    def put(self):
        return {'state':'SUCCESS'}, 200

    def post(self):
        payload = request.json
        #print(payload)
        for newfeature in payload[u'features']:
            found = False
            for db in customer_tmp_db[CAMERA_ID_ENTRANCE]:
                if feature_is_same_people(newfeature, db['feature']):
                    print("Found same people")
                    db['count'] += 1
                    db['latest_time'] = payload[u'time']
                    found = True
            if (found == False):
                print("New people")
                db = {'count' : 1, 'entre_time' : payload[u'time'], 'latest_time' : payload[u'time'], 'feature' : newfeature }
                customer_tmp_db[CAMERA_ID_ENTRANCE].append(db)

        latest_time[payload[u'id']] = payload[u'time']
                
        return {'state':'SUCCESS'}, 200

##
## Actually setup the Api resource routing here
##
api.add_resource(GetFeature, '/feature')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4040, threaded=True)
