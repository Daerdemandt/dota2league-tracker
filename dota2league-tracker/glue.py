
class MongoCRUD:
    def __init__(self, db, name, validate):
        self._db, self.name, self.validate = db, name, validate

    def create(self, data):
        # Validate data. If it's ok - create new, else ValueError
        pass
    def read(self, id):
        # return, if not exists - ??? 
        pass
    def update(self, id, update):
        # Read up on Mongo updates
        pass
    def delete(self, id):
        # return contents, on fail - error
        pass
    

def expose_as_api(app, info, path):
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


