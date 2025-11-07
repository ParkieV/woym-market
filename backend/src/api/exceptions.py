


class RequestException(Exception):
    """ Исключения во время отправки запросов """


class InitializationError(Exception):

    def __init__(self, api_type: str | None, detail: str) -> None:
        super().__init__(api_type, detail)
        self.api_type = api_type
        self.detail = detail

    def __str__(self):
        return f"Initialization of {self.api_type} API is failed. {self.detail}."

class MarketplaceAPIException(Exception):
    """ Исключения при работе с API маркетплейсов """
    def __init__(self, api_type: str, details: str) -> None:
        super().__init__(f"[{api_type}], details: {details}")
