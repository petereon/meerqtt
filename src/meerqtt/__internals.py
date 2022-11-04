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


def apply_arguments(fn: Callable, args: List[Any], kwargs: Dict[str, Any], message: bytes) -> Tuple[bool, Union[Exception, None]]:

    fn_kwargs = {}

    fn_signature_items_list = list(signature(fn).parameters.items())
    fn_signature_items_list_args = fn_signature_items_list[: len(args)]

    fn_signature_items_list_kwargs = fn_signature_items_list[len(args) :]

    for arg_value, (key, type_wrapper) in zip(args, fn_signature_items_list_args):
        fn_kwargs[key] = json.loads(arg_value) if issubclass(type_wrapper.annotation, BaseModel) else arg_value

    message_set = False

    for key_signature, type_wrapper in fn_signature_items_list_kwargs:
        try:
            kwarg_value = kwargs[key_signature]
            fn_kwargs[key_signature] = json.loads(kwarg_value) if issubclass(type_wrapper.annotation, BaseModel) else kwarg_value
        except KeyError:
            if not message_set:
                fn_kwargs[key_signature] = json.loads(message) if issubclass(type_wrapper.annotation, BaseModel) else message
            else:
                return False, ValueError(f'No argument provided for parameter `{key_signature}`')
    print(fn_kwargs)
    try:
        validate_arguments(fn)(**fn_kwargs)
        return True, None
    except Exception as e:
        return False, e
