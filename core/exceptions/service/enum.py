class ServiceAPIResponseStatus:
    SUCCESS = 200
    CREATED = 201
    DELETED = 204
    GENERAL_ERROR = 500
    CONFLICT_DATA = 409
    NOT_FOUND_DATA = 404
    BAD_REQUEST = 400


class ServiceAPIResponseMessage:
    SUCCESS = "Success"
    CREATED = "Create data success"
    GENERAL_ERROR = "General error"
    CONFLICT_DATA = "Duplicate data"
    NOT_FOUND_DATA = "Not found data"
    BAD_REQUEST = "Request error"
