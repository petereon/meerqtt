import logging
import re
from typing import Any, Callable, Dict, List, Literal, TypeAlias, Union

import paho.mqtt.client as paho_mqtt  # type: ignore

from meerqtt.__internals import CustomFormatter, apply_arguments

UserData: TypeAlias = Any


class MeerQTT:
    logger: logging.Logger
    paho_client: paho_mqtt.Client
    _topic_handler_mapping: Dict[str, Callable] = {}

    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: Union[str, None] = None,
        password: Union[str, None] = None,
        keepalive: int = 60,
        bind_address: str = '',
        bind_port: int = 0,
        client_id: str = '',
        clean_session: bool = True,
        userdata: UserData = None,
        properties: paho_mqtt.Properties = None,
        protocol: int = paho_mqtt.MQTTv311,
        clean_start: int = paho_mqtt.MQTT_CLEAN_START_FIRST_ONLY,
        transport: Literal['websockets', 'tcp'] = 'tcp',
        logger: Union[logging.Logger, None] = None,
    ) -> None:
        if logger:
            self.logger = logger
        else:
            self.logger = logging.Logger('meerqtt', level=logging.INFO)
            self.logger.setLevel(logging.INFO)

            ch = logging.StreamHandler()
            ch.setFormatter(CustomFormatter())

            self.logger.addHandler(ch)

        self.logger.info(f'Connecting to {host}:{port}')

        self.paho_client = paho_mqtt.Client(
            client_id=client_id,
            clean_session=clean_session,
            userdata=userdata,
            protocol=protocol,
            transport=transport,
        )

        if username:
            self.paho_client.username_pw_set(username, password)

        self.paho_client.connect(
            host=host,
            port=port,
            keepalive=keepalive,
            bind_address=bind_address,
            bind_port=bind_port,
            clean_start=clean_start,
            properties=properties,
        )

    def __handle_message(self, client: paho_mqtt.Client, userdata: UserData, msg: paho_mqtt.MQTTMessage) -> None:
        for topic, handler in self._topic_handler_mapping.items():
            topic_cleaned = topic.replace('+', '{}')
            topic_regex = re.sub(r'\{(.*?)\}', '(.+?)', topic_cleaned)
            values = re.findall(f'^{topic_regex}$', msg.topic)
            args: List[Any] = []
            kwargs: Dict[str, Any] = {}
            if values:
                params = re.findall(r'\{(.*?)\}', topic_cleaned)
                for param, value in zip(params, values[0]):
                    if param == '':
                        args.append(value)
                    else:
                        kwargs[param] = value

            success, exc = apply_arguments(fn=handler, args=args, kwargs=kwargs, message=msg.payload)

            if success:
                self.logger.info(f'TOPIC {msg.topic}')
                self.logger.debug(f'Caught by {topic}')
            else:
                self.logger.error(f'TOPIC {topic} - Error: {exc}')

    def subscribe(self, topic: str) -> Callable[[Callable], None]:
        self.paho_client.subscribe(topic=re.sub(r'\{(.*?)\}', '+', topic))

        def __subscribe(fn: Callable) -> None:
            self._topic_handler_mapping[topic] = fn

        return __subscribe

    def publish(self, topic: str, payload: Any = None, qos: int = 0, retain: bool = False) -> None:
        self.paho_client.publish(topic, payload, qos, retain)

    def start(self, log_level: int = logging.INFO) -> None:
        logging.basicConfig(level=log_level)
        self.paho_client.on_message = self.__handle_message
        self.paho_client.loop_forever()
