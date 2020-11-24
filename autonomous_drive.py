import socketio
import eventlet
import numpy as np
from flask import Flask
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import cv2


model_name = 'Models/model_5.h5'
speed_limit = 10 #MPH

sio = socketio.Server()

app = Flask(__name__)

# Preprocessing images
def img_preprocess(img):
  img = img[60:136, :, :]
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3, 3), 0)
  img = cv2.resize(img, (200, 66))
  img = img / 255
  return img

@sio.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed'])

    img = Image.open(BytesIO(base64.b64decode(data['image'])))
    img = np.asarray(img)
    img = img_preprocess(img)
    img = np.array([img])
    
    steering_angle = float(model.predict(img))
    throttle = 1.0 - speed/speed_limit
    print('angle: {} throttle: {} speed:{}'.format(steering_angle, throttle, speed))

    send_control(steering_angle, throttle)

@sio.on('connect')
def connect(sid, enviroment):
    print('Connected')

def send_control(steering_angle, throttle):
    sio.emit('steer', data = {
        'steering_angle': steering_angle.__str__(),
        'throttle': throttle.__str__()
    })

if __name__ == "__main__":
    
    model = load_model(model_name)

    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)