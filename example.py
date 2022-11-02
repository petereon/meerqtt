import pydantic
from meerqtt import MeerQTT

meerqtt = MeerQTT('127.0.0.1', client_id='new_client')


class Person(pydantic.BaseModel):
    name: str
    age: int

@meerqtt.subscribe('/sensor/{sensor_number}/{variable}')
def _(sensor_number: int, variable: str, person: Person):
    print(sensor_number, variable, person)


meerqtt.start()
