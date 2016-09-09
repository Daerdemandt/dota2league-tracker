from flask import Flask, abort, request
from config import parse
from bson.json_util import dumps
from inspect import getargspec

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
    def method2(self, param, something_else = 'not mandatory'):
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
        except AttributeError:
            abort(404)
        args = {_:request.args.get(_) for _ in request.args} # '?value=a&value=b'? No way!
        try:
            result = getter(**args)
        except TypeError:
            signature = getargspec(getter)
            known_params = signature.args[1:] # this removes 'self' - or how it is called - from the list. TODO: handle classmethods too
            mandatory_params = known_params[:-len(signature.defaults)] if signature.defaults else known_params
            known_params, mandatory_params = set(known_params), set(mandatory_params)

            errors = []
            query_params = set(args.keys())

            unknown_params = query_params - known_params
            if 1 == len(unknown_params):
                errors.append('Unknown param: ' + next(iter(unknown_params)) + '.')
            elif 1 < len(unknown_params):
                errors.append('Unknown params: ' + ', '.join(str(param) for param in unknown_params) + '.')

            unsatisfied_params = mandatory_params - query_params
            if 1 == len(unsatisfied_params):
                errors.append('Mandatory param not provided: ' + next(iter(unsatisfied_params)) + '.')
            elif 1 < len(unsatisfied_params):
                errors.append('Mandatory params not provided: ' + ', '.join(str(param) for param in unsatisfied_params) + '.')

            if errors:
                result = {'error': ' '.join(errors)}
            else:
                raise
        return dumps(result)

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
