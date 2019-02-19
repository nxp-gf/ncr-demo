#!/usr/bin/env python
from flask import Flask, send_from_directory
from flask_restful import reqparse, abort, Api, Resource, request
import json, math, threading, time, random, csv

parser = reqparse.RequestParser()

app = Flask(__name__)
api = Api(app)
parser.add_argument('id', type=str, location='args')
parser.add_argument('end', type=str, location='args')


TIMEOUT = 3
TIME_THRES = 2
CNTS_THRES = 3
FACE_RECOGNITION_THRES = 0.71
IDENTIFY_START  = 1000000000
IDENTIFY_END    = 9999999999

IDENTIFY_DB_FILE = "./models/identify.csv"
RECORD_DB_FILE = "./models/record.csv"

enter_camera_list = [0]
exit_camera_list = [2]
shelf_camera_list = [3,4,5]

#to store identify and feature, read/write feature database
identify_dict = {}
#To store the feature in the shop
main_ft_list = []
#To store the feature received for next step;
tmp_ft_list = []
#To store the feature list in each shelf;
shelf_ft_dict = {}

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

#find feature in feature_list
def find_feature(feature, feature_list):
    largest = 0
    for value in feature_list:
        similar = cal_similar(value, feature)
        print similar
        if (similar > largest):
            largest = similar

    if (largest > FACE_RECOGNITION_THRES):
        return True;
    else:
        return 0

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
        print similar
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

def record_msg(identify, camera_id, time1, time2):
    with open(RECORD_DB_FILE, 'a') as fp:
        mywriter = csv.writer(fp)
        tm1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time1))
        tm2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time2))
        mywriter.writerow((camera_id, str(identify), tm1, tm2))
        #fp.write(', '.join([str(identify), str(camera_id), time1, time2]))
        #fp.write('\n')

def handle_feature(feature, camera_id, time):
    ret = False
    #enter camera;
    if camera_id in enter_camera_list:
        ret = find_feature(feature, main_ft_list);
        #If feature does not in list, enter! add it in the list and record entry
        if(0 == ret):
            main_ft_list.append(feature)
            #if feature is not in feature_dict, give it an identify and add it
            identify = get_identify(feature)
            if (0 == identify):
                identify = create_identify(feature)

            #record the entry to data base
            record_msg(identify, camera_id, time, 0);
            print(identify, "enter.")
            ret = True
    #exit camera;
    elif camera_id in exit_camera_list:
        #If find the feature in list, exit! del it from list and record entry;
        ret = find_feature(feature, main_ft_list);
        if ret :
            main_ft_list.remove(feature)
            record_msg(get_identify(feature), camera_id, 0, time);
            ret = True
            print(identify, "exit.")
    #counter camera;
    elif camera_id in shelf_camera_list:
        #If not in list, enter! add it in list, record entry;
        #if in list and the time exceed 3s, exit! record entry;
        identify = get_identify(feature)
        #Get feature list first, if there is no camera_id, print error and return
        feature_list = shelf_ft_dict.get(camera_id, [])
        ret = find_feature(feature, feature_list);
        if(0 == ret):
            feature_list.append(feature)
            #record the entry to data base
            record_msg(identify, camera_id, time, 0);
            ret = True

        elif(time.time() - time > TIMEOUT):
            #Did not appear in 3s, exit!
            feature_list.remove(feature)
            record_msg(identify, camera_id, 0, time);
            ret = True

def db_update_thread():
    while(True):
        time.sleep(1)

        #The camera for entrance
        for db in tmp_ft_list:
            #only the time bigger than 2s, we handle it;
            if ((time.time() - db['time']) > TIME_THRES and db['count'] < CNTS_THRES):
                print("Delete fault alert")
                tmp_ft_list.remove(db)
            else:
                #If enter or exit, remove this feature from tmp_ft_list
                if(handle_feature(db['feature'], db['camera_id'], db['time'])):
                    tmp_ft_list.remove(db)


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
            if (largest > FACE_RECOGNITION_THRES):
                print("Found the same people")
                db_copy['count'] += 1
                db_copy['time'] = payload[u'time']
            else:
                #Add new feature
                print("Found new people")
                newdb = {'count':1, 'feature':tuple(newfeature), 'time':payload[u'time'], 'camera_id':payload[u'id']}
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
