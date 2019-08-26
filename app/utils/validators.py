import importlib
from werkzeug.datastructures import MultiDict
import inspect

'''
    Gestión de validaciones y mensajes de error
'''


def validate_form(blueprint_import_path, class_name, data):
    m_data = MultiDict(data)
    module = importlib.import_module('{}.forms'.format(blueprint_import_path))
    form_class = getattr(module, class_name)
    form = form_class(m_data)

    resp = form.validate()
    return resp, form

class ResponseJSON():
    __code__ = None
    def __init__(self, data, status=False):
        self.status = status
        self.data = data

    @property
    def status(self):
        return 'success' if self.__status__ else 'fail'
    @status.setter
    def status(self, value):
        self.__status__ = value

    def __repr__(self):
        return 'Response <{}>:{}'.format(self.status, self.data)

'''
    Serializar JSON objetos (sólo parte pública)
'''
def public_attr_to_dict(obj):
    obj_dict = {}
    for key, value in inspect.getmembers(obj):
        if key[:2] != '__' and not inspect.ismethod(getattr(obj, key)):
            obj_dict[key] = value

    return obj_dict
