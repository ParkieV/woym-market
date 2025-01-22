


class RequestException(Exception):
    """ Класс предназначенный для работы с исключениями из API """


class InitializationError(Exception):

    def __init__(self, api_type: str | None, detail: str) -> None:
        super().__init__(api_type, detail)
        self.api_type = api_type
        self.detail = detail

    def __str__(self):
        return f"Initialization of {self.api_type} API is failed. {self.detail}."
