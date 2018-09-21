import requests
import json
import facerecognition
import cv2
import numpy as np
import time




def send_features(features):
    print "Send features to GW."
    svrurl  = 'http://10.193.20.1:4040/feature'

    headers = {"Content-type":"application/json","Accept": "application/json"}
    r = requests.post(svrurl, headers=headers, data=json.dumps(features))
    if (r.status_code == 200):
        print "Sent successfully"
        return True
    else:
        print "Sent failed"
        return False

facerecg = facerecognition.FaceRecognition("./models", 0.71)
cap = cv2.VideoCapture(1)

while True:
    _, img = cap.read()
    image_char = img.astype(np.uint8).tostring()
    features = facerecg.get_feature(img.shape[0], img.shape[1], image_char)
    rets = {'id': 0, 'features' : features, 'time' : time.time()}
    print(json.dumps(rets))
    send_features(rets)
