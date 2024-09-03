import argparse
import json
import requests
from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    target_url = f'https://modelyo-r:3003/{path}'
    req_data = request.get_json(force=True)
    if req_data is None:
        return {"error": "Invalid JSON payload"}, 400
    headers = {key: value for key,
               value in request.headers if key != 'Host'}
    print(headers)

    def get_stream():
        print('start')
        with requests.post(url=target_url, json=req_data, headers=headers,  verify=args['ca'], cert=(args['cert'], args['key']), stream=True, timeout=900) as test:
            print('in request')
            test.raise_for_status()
            for line in test.iter_lines():
                if line:
                    stream_data = json.loads(line.decode('utf-8'))
                    yield f"{json.dumps(stream_data)}\n"
            print("done iter")
        print("done request")
    return Response(get_stream(), mimetype='application/json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='python3 flowise_proxy.py --cert ~/modelyo/certs/user.pem --key ~/modelyo/certs/user.key --ca ~/modelyo/l/src/r_ca.pem\n')
    parser.add_argument(
        '--cert', help='user certificate, pem file path', required=True)
    parser.add_argument('--key', help='user key, key file path', required=True)
    parser.add_argument('--ca', help='r-ca, pem file path', required=True)
    args = vars(parser.parse_args())
    app.run(host='0.0.0.0', port=8080)
