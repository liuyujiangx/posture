from app import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
import logging

if __name__ == "__main__":
    #app.run(port=5566,host='0.0.0.0',threaded=True)
    options.parse_command_line()
    logging.info('[UOP] UOP is starting...')
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5566)
    IOLoop.instance().start()