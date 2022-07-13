import json
import argparse
import requests
from datetime import datetime


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--code_csv_path", help="path to the codes", required=True)
    parser.add_argument("--upload_url", help="upload url to send the codes to", required=True)
    parser.add_argument("--api_key", help="use this api key", required=True)

    args = parser.parse_args()

    csv_path = args.code_csv_path
    upload_url = args.upload_url
    api_key = args.api_key

    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        try:
            codes = [ line.strip().split(',')[1].replace('"', "") for line in lines[1:]]
        except:
            print('could not parse csv file')
            print(lines)
            exit()

        index = 0
        step_size = 200
        while index < len(codes):
            start_time = datetime.now()
            payload = {
                "codes": codes[index:min(index+step_size, len(codes))]
            }
            index = index + step_size

            r = requests.post(
                upload_url,
                data=json.dumps(payload),
                headers={
                    "Api-Key": api_key
                },
            )

            if r.status_code != 200:
                print(r.content)
                exit()
            resp = r.json()
            print("{} in {:.2f}s".format(str(resp),datetime.now().timestamp() - start_time.timestamp()))