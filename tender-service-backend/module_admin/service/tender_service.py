import json

from curl_cffi import requests as curl_requests

URL = 'https://ggzyfw.beijing.gov.cn/elasticsearch/searchList'

PAYLOAD = {
    'channel_id': '284',
    'channel_first': 'jyxx',
    'channel_second': 'jyxxgcjs',
    'channel_third': 'jyxxgcjszbjh',
    'channel_fourth': '',
    'ext': 'A98',
    'ext8': '',
    'starttime': '2025-12-05',
    'endtime': '2026-01-05',
    'sort': 'time',
    'page': '1',
    'size': '100',
}
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/x-www-form-urlencoded',
}

def _fetch_json_text() -> str:
    resp = curl_requests.post(
        URL,
        headers=HEADERS,
        data=PAYLOAD,
        timeout=30,
        verify=False,
        impersonate='chrome',
    )
    return resp.content.decode('utf-8', errors='replace')

def fetch_tender_json() -> dict:
    raw_text = _fetch_json_text()
    data: dict = json.loads(raw_text)
    result_field = data.get('result')
    if isinstance(result_field, str):
        try:
            data['result'] = json.loads(result_field)
        except json.JSONDecodeError:
            data['result'] = result_field
    return data


if __name__ == '__main__':
    tender_data = fetch_tender_json()

    print(json.dumps(tender_data.get("result")[0], ensure_ascii=False, indent=2))

