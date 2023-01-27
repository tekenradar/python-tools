import requests
from datetime import timedelta

api_key = "secret-api-key1"
url = 'http://localhost:5015/sampler/germany/status'

r = requests.get(url, headers={
                    "Api-Key": api_key
                },
            )

if r.status_code != 200:
    print(r.content)
    exit()
resp = r.json()


print('\n\nTime since beginning of the interval: {} ({}s)'.format(timedelta(seconds=resp['currentTimeInInterval']), resp['currentTimeInInterval'] ))

print('Slots (target currently - used = available): {} - {} = {}'.format(resp['openSlotsTarget'], resp['usedSlots'], resp['availableSlots']))
print('Max slots at the end of interval: {}'.format(resp['maxSlots']))

