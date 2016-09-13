from flask import abort, request
from inspect import getargspec
from bson.json_util import dumps
from bson.objectid import ObjectId
from good import Invalid

def lexic_join(expressions):
    *most, last = expressions
    if most:
        return ', '.join(str(e) for e in most) + ' and ' + str(last)
    else:
        return str(last)

class MongoCRUD:
    def __init__(self, db, name, validate):
        self._collection = db[name]
        self.name, self.validate = name, validate

    def create(self, **kwargs):
        try:
            data = self.validate(kwargs)
        except Invalid as e:
            raise ValueError(str(e))
        return self._collection.insert_one(data).inserted_id

    def read(self, id = None, **kwargs):
        # TODO: use kwargs only and validate them
        if id == None and not kwargs:
            return ValueError('Object to be read must be identified')
        query = kwargs if kwargs else {}
        if (id):
            query['_id'] = ObjectId(id)
        result = self._collection.find_one(query)
        if None == result:
            if (id):
                del query['_id']
                query['id'] = id
            message = 'Found no elemens with' + lexic_join(map(lambda x:'`{}`:`{}`'.format(*x), query.items()))
            raise KeyError(message)
        return result

    def update(self, id, update):
        # Read up on Mongo updates
        pass
    def delete(self, id):
        # return contents, on fail - error
        pass
    
# TODO: consider using blueprints for that
def expose_as_api(app, info, path):
    if not path.endswith('/'):
        path = path + '/'
    if not path.startswith('/'):
        path = '/' + path

    @app.route(path, endpoint = path)
    def get_string_repr():
        return dumps({'info':str(info)})

    @app.route(path + '<action>/', endpoint = path + 'actions')
    def get_object_action(action):
        status = 200
        try:
            getter = getattr(info, action) #TODO what if it's not a GET action?
        except AttributeError:
            status = 404
            return dumps({'error' : action + ' is not found'}), status
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

            if not (signature.varargs or signature.keywords):
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
                status = 422
            else:
                raise
        except KeyError as e:
            result = {'error': 'Not found: ' + str(e)}
            status = 404
        except ValueError as e:
            result = {'error' : 'Something is wrong: ' + str(e)}
            status = 422
        except NotImplementedError as e:
            result = {'error' : 'Not implemented: ' + str(e)}
            status = 501
        except Exception as e:
            result = {'error' : 'Unexpected error: ' + str(e)}
            status = 500
        return dumps(result), status


