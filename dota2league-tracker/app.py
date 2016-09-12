from flask import Flask
from config import parse
from glue import expose_as_api

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
    def error(self, error):
        errors = {
            'key' : KeyError('keeeeey'),
            'value' : ValueError('bad food'),
            'ni' : NotImplementedError('totally')
        }
        raise errors[error]

expose_as_api(app, Dummy('sikret data'), '/object')

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
