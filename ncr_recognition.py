import requests
import json
import facerecognition
import cv2
import numpy as np
import time,os
import argparse

os.putenv("CAP_PROP_FRAME_WIDTH", "320")
os.putenv("CAP_PROP_FRAME_HEIGHT", "240")

parser = argparse.ArgumentParser()
parser.add_argument('--dev', type=str, required=True,
                    help='[usb|"url" of IP camera]input video device')
parser.add_argument('--gwip', type=str, default="10.193.20.1",
                    help='The port for http server')
parser.add_argument('--gwport', type=str, default="4040",
                    help='The ip for training server')
parser.add_argument('--camid', type=int, required=True,
                    help='Camera id')
args = parser.parse_args()

if 'usb' in args.dev:
    print("Using onboard usb camera")
    cap = cv2.VideoCapture(int(args.dev[3]))
else:
    print("Using ip camera with url(s)", args.dev)
    cap = cv2.VideoCapture(args.dev)
print("Using gw ip:" + args.gwip + " port:" + args.gwport)

def send_features(features):
    svrurl  = 'http://' + args.gwip + ':' + args.gwport + '/feature'

    headers = {"Content-type":"application/json","Accept": "application/json"}
    r = requests.post(svrurl, headers=headers, data=json.dumps(features))
    if (r.status_code == 200):
        #print "Sent successfully"
        return True
    else:
        print "Sent failed"
        return False

facerecg = facerecognition.FaceRecognition("./models", 0.71)

while True:
    _, img = cap.read()
    image_char = img.astype(np.uint8).tostring()
    features = facerecg.get_feature(img.shape[0], img.shape[1], image_char)
    rets = {'id': args.camid, 'features' : features, 'time' : time.time()}
    #print(json.dumps(rets))
    send_features(rets)
