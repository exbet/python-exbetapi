# -*- coding: utf-8 -*-
""" Exceptions for exbet-api
"""


class JsonDecodingFailedException(Exception):
    """ Exception when decoding of server response failed
    """


class AlreadyLoggedinException(Exception):
    """ Instance is already logged in
    """


class ExecutionError(Exception):
    """ The execution on the API failed
    """


class APIError(Exception):
    """ The API raised an error
    """
