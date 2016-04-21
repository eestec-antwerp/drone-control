import os
import logging
import json
import subprocess
import signal

import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

from util import *

define("port", default=80, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

class Handler(tornado.web.RequestHandler):
    def answer(self, data):
        s = json.dumps(data)
        print("Answering", s)
        self.write(s)

class switch_ajax(switch):
    def select(self):
        return self.request.uri.split("/")[3]
    
    def default(self):
        self.answer({"message": "Error: no case found in switch"})

class MainHandler(Handler):
    def get(self):
        running = "RUNNING" if ardu_running() else "NOT RUNNING"
        self.render("index.html", ip=self.request.remote_ip, ardu_running=running)


def ardu_processes():
    try:
        s = subprocess.check_output(["pgrep", "ArduCopter-quad"]).decode("utf-8")
        return [int(p) for p in s.split("\n") if p != ""]
    except subprocess.CalledProcessError:
        return []

def ardu_running():
    return len(ardu_processes()) > 0


class ArduCopterHandler(Handler):
    class _post(switch_ajax):
        @case("start")
        def start(self):
            if ardu_running():
                self.answer({"message": "ArduCopter is already running"})
            else:
                os.system("ArduCopter-quad -A udp:{ip}:14550 & 2> /root/ardu_log".format(ip=self.request.remote_ip))
        
        @case("start_without_connection")
        def start_without_connection(self):
            if ardu_running():
                self.answer({"message": "ArduCopter is already running"})
            else:
                os.system("ArduCopter-quad & 2> /root/ardu_log")
        
        @case("stop")
        def stop(self):
            for pid in ardu_processes():
                os.kill(pid, signal.SIGTERM)  # Watch out!
    
    def post(self):
        return self._post(self)


class PowerHandler(Handler):
    class _post(switch_ajax):
        @case("shutdown")
        def shutdown(self):
            os.system("shutdown now")
        
        @case("reboot")
        def reboot(self):
            os.system("reboot")
    
    def post(self):
        if ardu_running():
            self.answer({"message": "Error: ArduCopter is still running"})
        else:
            return self._post(self)


def main():
    parse_command_line()
    app = tornado.web.Application([
            (r"/", MainHandler),
            (r"/ajax/arducopter/.*", ArduCopterHandler),
            (r"/ajax/power/.*", PowerHandler),
            ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

main()

