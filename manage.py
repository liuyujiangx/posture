from app import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

if __name__ == "__main__":
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(5566)  # flask默认的端口
    # IOLoop.instance().start()
    app.run(port=5566,host='0.0.0.0')