from decorator import decorator
from tg import validate as tgValidate, flash, redirect
from pylons import request
from tg.controllers import _object_dispatch
class validate(tgValidate):
    def __init__(self,*args,**kwds):
        super(validate,self).__init__(*args,**kwds)
        class Validators(object):
            def validate(self, params):
                controller=request.environ["pylons.controller"]
                url_path = request.path_info.split('/')[1:]
                controller, remainder = _object_dispatch(controller, url_path)
                sprocket = controller.im_self.sprockets[params['dbsprockets_id']]
                res= sprocket.view.widget.validate(params)
                return res
        self.validators=Validators()

class validate_explicit(tgValidate):
    def __init__(self,sprockets,*args,**kwds):
        super(validate_explicit,self).__init__(*args,**kwds)
        class Validators(object):
            def validate(self, params):
                sprocket = sprockets[params['dbsprockets_id']]
                return sprocket.view.widget.validate(params)
        self.validators=Validators()
def crudErrorCatcher(errorType=None, error_handler=None):
    def wrapper(func, self, *args, **kwargs):
        """Decorator Wrapper function"""
        try:
            value = func(self, *args, **kwargs)
        except errorType, e:
            message=None
            if hasattr(e,"message"):
                message=e.message
            if isinstance(message,str):
                try:
                    message=message.decode('utf-8')
                except:
                    message=None
            if message:
                flash(message,status="status_alert")
            request.environ['pylons.routes_dict'] = error_handler
            return self._perform_call(None, dict(url=error_handler))
        return value
    return decorator(wrapper)
