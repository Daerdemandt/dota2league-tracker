from jinja2 import Template, Environment
import requests
from json import dumps
from good import Schema, Optional

template_schema = Schema({ # TODO: not just a string, but valid Jinja template!
    'url' : str,
    'type' : str,
    Optional('data') : str
})

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

class Hooks:
    def __init__(self, hooks):
        self._hooks = dictmap(Trigger, hooks)

    def process(self, **context):
        for name, trigger in self._hooks.items():
            try:
                trigger.process(**context)
            except Exception as e:# TODO: actually handle exceptions here
                p(e)
