class MappingError(Exception):
    """ Исключение при неудачном представлении в виде Mapping-объекта """
    pass

class InitializationError(Exception):
    """ Исключение при неудочной инииализации веб-сервера """
    pass