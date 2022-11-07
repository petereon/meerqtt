# Overview

> :warning: meerqtt is untested, use at your own risk

meerqtt (/ˈmɪr.kæt/) is a Python MQTT client

## Example

```python
from typing import Dict
import pydantic
from meerqtt import MeerQTT

meerqtt = MeerQTT('127.0.0.1', client_id='new_client')

cars: Dict[int, Dict[str, float]] = {}


class Data(pydantic.BaseModel):
    temperature: float
    humidity: float


@meerqtt.subscribe('/sensor/+')
def _(sensor_number: int, data: Data):
    with open('data.csv', 'a') as fh:
        fh.write(f'\n{sensor_number},{data.humidity},{data.temperature}')


@meerqtt.subscribe('/car/{number}/{measurement}')
def _(measurement: str, number: int, value: float):
    if number not in cars:
        cars[number] = {}
    cars[number][measurement] = value
    print(cars)


meerqtt.start()
```
