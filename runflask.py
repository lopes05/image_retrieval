import sys
from flask import Flask
from image import *
from flask import request
import requests

import logging

logging.basicConfig(filename='backend.log', level=logging.DEBUG)
logger = logging.getLogger('backend')


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World from Flask!"
import cv2

from flask import Response
import json

@app.route('/image', methods=['GET'])
def image_url():
    try:
        f = open('/tmp/temp.jpg','wb')

        image_url = request.args['imgurl']  # get the image URL
        f.write(requests.get('http://localhost:8000/' + image_url).content)
        f.close()

        hists = run_process('/tmp/temp.jpg')
        return Response(json.dumps(hists))

    except Exception as e:
        logger.error(str(e))
        return 'error'

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
