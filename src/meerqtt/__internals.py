import json
import logging
from inspect import signature
from typing import Any, Callable, Dict, List, Tuple, Union

from pydantic import BaseModel, validate_arguments


class CustomFormatter(logging.Formatter):

    grey = '\x1b[38;20m'
    yellow = '\x1b[33;20m'
    red = '\x1b[31;20m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    formatting = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    FORMATS = {
        logging.DEBUG: grey + formatting + reset,
        logging.INFO: grey + formatting + reset,
        logging.WARNING: yellow + formatting + reset,
        logging.ERROR: red + formatting + reset,
        logging.CRITICAL: bold_red + formatting + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def apply_arguments(fn: Callable, arguments: Union[List[Any], Dict[str, Any]], message: bytes) -> Tuple[bool, Union[Exception, None]]:
    fn_signature = signature(fn).parameters
    if isinstance(arguments, dict):
        keys = list(set(fn_signature.keys()) - set(arguments.keys()))
        if len(keys) == 0:
            return False, ValueError('No parameter to handle the message is provided')
        arguments[keys[0]] = message
        for param, typ in fn_signature.items():
            if issubclass(typ.annotation, BaseModel):
                try:
                    arguments[param] = json.loads(arguments[param])
                except KeyError:
                    return (False, ValueError(f'Value for parameter `{param}` not provided'))
        try:
            validate_arguments(fn)(**arguments)
            return (True, None)
        except Exception as e:
            return (False, e)
    else:
        arguments.append(message)

        for index, (_, typ) in enumerate(fn_signature.items()):
            if issubclass(typ.annotation, BaseModel):
                arguments[index] = json.loads(arguments[index])
        try:
            validate_arguments(fn)(*arguments)
            return (True, None)
        except Exception as e:
            return (False, e)
