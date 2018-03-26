#!/usr/bin/env python

import sys
import io
import os
import base64
from threading import Thread
from time import sleep, time
from http.server import HTTPServer, BaseHTTPRequestHandler

import picamera

WIDTH = 1920
HEIGHT = 1080

HTTP_PORT = 8082

#720p
#WIDTH = 1280
#HEIGHT = 720


RaspberryCamera = None

img64 = None

class StreamingHttpHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', 'current_frame.base64')
            self.end_headers()
            return
        elif self.path == '/current_frame.base64':
            content_type = 'text/plain'
            content = img64
        elif self.path == '/current.html':
            content_type = 'text/html; charset=utf-8'
            img = img64
            content = '<html><img height="720" width="1280" src="data:image/png;base64, {}" /></html>'\
                .format(img).replace("b'", "",).replace("'", "")
            content = content.encode('utf-8')
        else:
            self.send_error(404, 'Not found bro')
            return

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def GetScreenshot(self):
        my_stream = io.BytesIO()
        RaspberryCamera.capture(my_stream, 'jpeg')
        img = base64.b64encode(my_stream.getvalue())
        my_stream.close()
        return img

class StreamingHttpServer(HTTPServer):
    def __init__(self):
        super(StreamingHttpServer, self).__init__(
            ('', HTTP_PORT), StreamingHttpHandler)


def UpdateScreenshot():
    global img64
    try:
        my_stream = io.BytesIO()
        RaspberryCamera.capture(my_stream, 'jpeg')
        img = base64.b64encode(my_stream.getvalue())
        my_stream.close()
        img64 = img
    except picamera.PiCameraRuntimeError:
        global RaspberryCamera
        RaspberryCamera.close()
        print('PiCamera runtime error, attempting to reinitialize..')
        InitialiseCamera()


def InitialiseCamera():
    global RaspberryCamera
    while True:
        print('Initialising HDMI -> CSI2 Bridge')
        try:
            RaspberryCamera = picamera.PiCamera()
            break
        except picamera.PiCameraMMALError:
            print('Failure to initialise, trying again in 5s..')
            sleep(5)
            continue

    RaspberryCamera.resolution = (WIDTH, HEIGHT)
    RaspberryCamera.start_preview()
    sleep(1)
    print('HDMI -> CSI2 Bridge Initialised')

def main():

    InitialiseCamera()

    while (True):
        UpdateScreenshot()
        sleep(.5)

    print('Initialising HTTP on port 8082')
    http_server = StreamingHttpServer()
    http_thread = Thread(target=http_server.serve_forever)

    try:
        http_thread.start()
        print('Application started, listening...')
        while(True):
            UpdateScreenshot()
            sleep(.75)
    except KeyboardInterrupt:
        pass
    finally:
        print('Shutting down HTTP server')
        http_server.shutdown()
        print('Waiting for HTTP server thread to finish')
        http_thread.join()

if __name__ == '__main__':
    main()



