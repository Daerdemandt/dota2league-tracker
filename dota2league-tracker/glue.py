from flask import abort, request
from inspect import getargspec
from bson.json_util import dumps
from bson.objectid import ObjectId
from good import Invalid
import sys
import time
import threading

def lexic_join(expressions):
    *most, last = expressions
    if most:
        return ', '.join(str(e) for e in most) + ' and ' + str(last)
    else:
        return str(last)

#TODO: decorator that translates Invalid to ValueError
#TODO: context manager that lets exceptions seep through cathces - so that they hit top level, useful for debug mode

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
        # TODO: support validating the update, not post-update entity
        update_validation_supported = False
        if not update_validation_supported: # We'll have to update document in Python and validate the result.
            if not isinstance(update, dict):
                raise ValueError('Improperly formed update')
            data = self.read(id)
            def recursive_update(data, update): # beware: passing immutable object on the top level would not work in-place
                try:
                    for key, value in update.items():
                        if key in data:
                            data[key] = recursive_update(data[key], update[key])
                        else:
                            data[key] = update[key]
                    return data
                except AttributeError: # update is not a dict. Or maybe something else?
                    return update
                except TypeError: # update is a dict but data is not
                    return update
            recursive_update(data, update) # should work in-place because both are dicts
            del data['_id']

            try:
                new_data = self.validate(data)
            except Invalid as e:
                raise ValueError(str(e))

            query = {'_id' : ObjectId(id)}
            # Note: by the time we actually write something, original data could have already changed. Need transactions? See somewhere else
            result = self._collection.find_one_and_replace(query, new_data)
            return result # returns old value

    def delete(self, id):
        result = self._collection.delete_one({'_id' : ObjectId(id)}).deleted_count
        if 0 == result:
            raise KeyError('Found no element with id `{}`'.format(id))
        elif 1 == result:
            return id
        else:
            raise RuntimeError('`delete_one` reports to have deleted `{}` elements, not 0 or 1'.format(result))

    def list(self, **kwargs):
        query = kwargs if kwargs else None
        result = self._collection.find(query)
        return list(result)

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
        #TODO: support dicts in input query as php does
        args = {_:request.args.get(_) for _ in request.args} # '?value=a&value=b'? No way!
        try:
            result = getter(**args)
        except TypeError as e:
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

            status = 422
            if errors:
                result = {'error': ' '.join(errors)}
            else:
                result = {'error': 'Something is wrong: ' + str(e)}

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


def p(*args):
    print(*args, file=sys.stderr)

def forever(function, delay=10):
    def loop():
        while True:
            try:
                function()
            except KeyboardInterrupt:
                raise
            except Exception:
                pass
            time.sleep(delay)
            #break # that's for debugging purposes
    thread = threading.Thread(target=loop)
    thread.start()


