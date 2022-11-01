from meerqtt import MeerQTT

meerqtt = MeerQTT('127.0.0.1', client_id='new_client')

@meerqtt.subscribe('/some_topic')
def _(message):
    print(message)


meerqtt.start()
