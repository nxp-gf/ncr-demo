#!/usr/bin/env python
from flask import Flask, send_from_directory
from flask_restful import reqparse, abort, Api, Resource, request
import json, math, threading, time, random, csv

parser = reqparse.RequestParser()

app = Flask(__name__)
api = Api(app)
parser.add_argument('id', type=str, location='args')
parser.add_argument('end', type=str, location='args')


TIME_THRES = 1
CNTS_THRES = 3
STATUS_ENTER = 1
STATUS_EXIT = 0
FACE_RECOGNITION_THRES = 0.71
IDENTIFY_START  = 1000000000
IDENTIFY_END    = 9999999999
NULL_TIME       = ""

IDENTIFY_DB_FILE = "./models/identify.csv"
RECORD_DB_FILE = "./models/record.csv"

enter_camera_list = [1]
exit_camera_list = [2]
shelf_camera_list = [3,4]

#to store identify and feature, read/write feature database
identify_dict = {}
#To store the feature received for next step;
tmp_ft_list = []

#calulate the similar feature
def cal_similar(v1, v2):
    #print v1, v2
    if (len(v1) != len(v2)):
        return False
    ret = 0.0
    mod1 = 0.0
    mod2 = 0.0
    for i in range(len(v1)):
        ret += v1[i] * v2[i]
        mod1 += v1[i] * v1[i];
        mod2 += v2[i] * v2[i];

    return (ret / math.sqrt(mod1) / math.sqrt(mod2) + 1) / 2.0;

#pay attention that the feature is not the same but just similar,
#so it cannot use the feature directly;

#load identify lib;
def load_identfiy():
    with open(IDENTIFY_DB_FILE, 'a+') as fp:
        lines = csv.reader(fp)
        for line in lines:
            identify_dict[eval(line[0])] = int(line[1])

#save identify lib;
def save_identify():
    with open(IDENTIFY_DB_FILE, 'a') as fp:
        mywriter = csv.writer(fp)
        for item in identify_dict.items():
            mywriter.writerow(item)

#Get identify from identify_dict by feature
def get_identify(feature):
    largest = 0
    for key in identify_dict.keys():
        similar = cal_similar(key, feature)
        #print similar
        if (similar > largest):
            largest = similar
            identify = identify_dict[key]

    if (largest > FACE_RECOGNITION_THRES):
        return identify;
    else:
        return 0

#create identify and add it to identify lib;
def create_identify(feature):
    identify = random.randint(IDENTIFY_START, IDENTIFY_END)
    identify_dict[feature] = identify

    #add it to idetify lib
    with open(IDENTIFY_DB_FILE, 'a') as fp:
        mywriter = csv.writer(fp)
        mywriter.writerow((feature, identify))

    return identify;

def record_msg(camera_id, identify, time1, time2):
    with open(RECORD_DB_FILE, 'a') as fp:
        mywriter = csv.writer(fp)
        mywriter.writerow((camera_id, str(identify), time1, time2))

def db_update_thread():
    while(True):
        time.sleep(1)

        #loop the tmp_ft_list
        for db in tmp_ft_list:
            cur = time.time()
            #fault alert
            if ((cur - db['time']) > TIME_THRES and db['count'] < CNTS_THRES):
                print("Delete fault alert")
                tmp_ft_list.remove(db)
                continue

            camera_id = db['camera_id']
            identify = get_identify(db['feature'])
            if (0 == identify):
                identify = create_identify(db['feature'])

            tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(db['time']))
            #exit 2s in camera
            if((cur - db['time'] > TIME_THRES) and (db['count'] > CNTS_THRES)):
                if camera_id in enter_camera_list:
                    print(identify, camera_id, "enter.")
                    record_msg(camera_id, identify, tm, NULL_TIME)
                    tmp_ft_list.remove(db)
                #exit camera;
                elif camera_id in exit_camera_list:
                    print(identify, camera_id, "exit.")
                    record_msg(camera_id, identify, NULL_TIME, tm)
                    tmp_ft_list.remove(db)
                #shelf camera;
                elif camera_id in shelf_camera_list:
                    print(identify, "shelf",camera_id, "exit.")
                    record_msg(camera_id, identify, NULL_TIME, tm)
                    tmp_ft_list.remove(db)
            #stay in camera, if it is shelf camera, enter
            elif((cur - db['time'] < TIME_THRES) and (db['count'] > CNTS_THRES)):
                if (camera_id in shelf_camera_list) and  db['status'] != STATUS_ENTER:
                    print(identify, "shelf", camera_id, "enter.")
                    record_msg(camera_id, identify, tm, NULL_TIME)
                    db['status'] = STATUS_ENTER

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
            largest = 0
            for db in tmp_ft_list:
                similar = cal_similar(newfeature, db['feature'])
                if (similar > largest):
                    largest = similar
                    db_copy = db
            if (largest > FACE_RECOGNITION_THRES and db_copy['camera_id'] == payload[u'id']):
                print("Found the same people")
                db_copy['count'] += 1
                db_copy['time'] = time.time()
                #db_copy['time'] = payload[u'time']
            else:
                #Add new feature
                print("Found new people")
                #if feature is not in feature_dict, give it an identify and add it
                newdb = {'count':1, 'feature':tuple(newfeature), 'time':time.time(), 'camera_id':payload[u'id'], 'status':STATUS_EXIT}
                #newdb = {'count':1, 'feature':tuple(newfeature), 'time':payload[u'time'], 'camera_id':payload[u'id'], 'status':STATUS_EXIT}
                tmp_ft_list.append(newdb)

        return {'state':'SUCCESS'}, 200

##
## Actually setup the Api resource routing here
##
api.add_resource(GetFeature, '/feature')

if __name__ == '__main__':
    #Init identify_dict according to the identify lib;
    load_identfiy();

    app.run(host='0.0.0.0', port=4040, threaded=True)
