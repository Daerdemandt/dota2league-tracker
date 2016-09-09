from flask import Flask, abort, request
from config import parse
from bson.json_util import dumps

config = parse('config.yml')

app = Flask(__name__)

#TODO: add more depth here
@app.route('/health')
def get_health():
    return "Ok"

@app.route('/config')
def get_config():
    return dumps(config)

class Dummy:
    def __init__(self, data):
        self._data = data
    def __str__(self):
        return "Object containing " + str(self._data)
    def method1(self):
        return "Yay, it's method1!"
    def method2(self, param):
        return "Yay, it's method2 with param value of " + str(param)

o = Dummy('Sikret data')

def expose_as_api(info, path):
    if not path.endswith('/'):
        path = path + '/'
    if not path.startswith('/'):
        path = '/' + path

    @app.route(path)
    def get_string_repr():
        return dumps({'info':str(info)})

    @app.route(path + '<action>/')
    def get_object_action(action):
        try:
            getter = getattr(o, action) #TODO what if it's not a GET action?
            args = {_:request.args.get(_) for _ in request.args} # '?value=a&value=b'? No way!
            return dumps(getter(**args))
        except AttributeError:
            abort(404)

expose_as_api(Dummy('sikret data'), '/object')

@app.route('/obj/')
def get():
    args = request.args
    key = args.get('key')
    #return str([_ for _ in args])
    #args = dict(request.args)
    args = {_:args.get(_) for _ in args}
    return str(args)
    return str(args[key])

if __name__ == "__main__":
    app.run(host='0.0.0.0', **config['server'])
