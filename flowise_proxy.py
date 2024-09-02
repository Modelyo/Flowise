import os
import time
from typing import Iterable
from flask import Flask, json, request, Response
import requests
import argparse

app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    target_url = f'https://modelyo-r:3003/{path}'
    print(target_url)
    req_data = request.get_json(force=True)
    if req_data is None:
        return {"error": "Invalid JSON payload"}, 400

    response = requests.post(
        url=target_url,
        headers={key: value for key,
                 value in request.headers if key != 'Host'},
        json=req_data,
        verify=args['ca'],
        cert=(args['cert'],
              args['key']),
        timeout=900
    )
    response_content = Response(response)
    return response_content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='python3 flowise_proxy.py --cert ~/modelyo/certs/user.pem --key ~/modelyo/certs/user.key --ca ~/modelyo/l/src/r_ca.pem\n')
    parser.add_argument(
        '--cert', help='user certificate, pem file path', required=True)
    parser.add_argument('--key', help='user key, key file path', required=True)
    parser.add_argument('--ca', help='r-ca, pem file path', required=True)
    args = vars(parser.parse_args())
    app.run(host='0.0.0.0', port=8080)
