from jinja2 import Template, Environment
import requests
from json import dumps

env = Environment()
env.filters['json'] = dumps

example = {
    'url' : 'http://httpbin.org/post',
    'type' : 'post',
    'data' : '{{match|json}}'
}

def dictmap(fun, d):
    return {key:fun(d[key]) for key in d}
#TODO: validation
class Trigger:
    def __init__(self, template):
        self._template = dictmap(env.from_string, template)

    def _render(self, **context):
        return dictmap(lambda t: t.render(**context), self._template)

    def process(self, **context):
        request_spec = self._render(**context)
        if request_spec['type'] == 'post':
            request = requests.post(request_spec['url'], data = request_spec['data'])
        elif request_spec['type'] == 'get':
            request = requests.get(request_spec['url'])
        return request.text


t = Trigger(example)
