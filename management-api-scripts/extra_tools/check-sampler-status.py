import requests
from datetime import timedelta
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--status_url", help="url where status can be checked", required=True)
    parser.add_argument("--api_key", help="use this api key", required=True)

    args = parser.parse_args()


    url = args.status_url
    api_key = args.api_key

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

