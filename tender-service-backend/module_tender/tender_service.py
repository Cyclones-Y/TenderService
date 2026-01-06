import asyncio
import json
import os
import re
import sys
from datetime import date, datetime

from curl_cffi import requests as curl_requests

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import AsyncSessionLocal
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.tender_service import TenderService

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

def _abs_url(link: str) -> str:
    if not link:
        return ''
    if link.startswith('http'):
        return link
    return f'https://ggzyfw.beijing.gov.cn{link}'

def _parse_content_fields(content: str) -> dict:
    fields = {
        'construction_unit': None,
        'bid_control_price': None,
        'construction_scale': None,
        'construction_content': None,
        'expected_announcement_date': None,
        'tender_scope': None,
    }
    content_str = content or ''

    def _norm_text(s: str) -> str:
        return re.sub(r'\s+', ' ', (s or '')).strip()

    m_unit = re.search(
        r'招标人[：:]\s*(.*?)(?:。|；|;|项目概况|投资估算|招标范围|建设规模|预计招标公告发布时间|招标公告发布时间|其他说明|项目名称|$)',
        content_str,
        flags=re.S,
    )
    if m_unit:
        fields['construction_unit'] = _norm_text(m_unit.group(1))

    m_content = re.search(r'项目概况[：:]\s*(.*?)(?=投资估算(?:[：:]|\\s))', content_str, flags=re.S)
    if m_content:
        fields['construction_content'] = _norm_text(m_content.group(1))

    m_scope = re.search(
        r'招标范围[：:]\s*(.*?)(?=建设规模[：:]|建设面积[：:]|施工面积[：:])',
        content_str,
        flags=re.S,
    )
    if m_scope:
        fields['tender_scope'] = _norm_text(m_scope.group(1))

    def _extract_scale_text(text: str) -> str | None:
        if not text:
            return None
        t = _norm_text(text).replace('，', ',')
        return t or None

    m_scale_text = re.search(
        r'建设规模[：:]\s*(.*?)(?=(?:预计)?招标公告发布时间|招标公告发布时间|其他说明|$)',
        content_str,
        flags=re.S,
    )
    if m_scale_text:
        fields['construction_scale'] = _extract_scale_text(m_scale_text.group(1))

    m_price = re.search(r'(?:招标控制价|投资估算)[：:]\s*([\d\.]+)\s*万元', content_str)
    if m_price:
        try:
            fields['bid_control_price'] = float(m_price.group(1))
        except ValueError:
            fields['bid_control_price'] = None

    if fields['construction_scale'] is None:
        m_scale_fallback = re.search(
            r'(?:建设规模|建设面积|施工面积)[：: ]?\s*(.*?)(?=(?:预计)?招标公告发布时间|招标公告发布时间|其他说明|$)',
            content_str,
            flags=re.S,
        )
        if m_scale_fallback:
            fields['construction_scale'] = _extract_scale_text(m_scale_fallback.group(1))
    m_expected = re.search(
        r'预计招标公告发布时间[：:]\s*(.*?)(?=其他说明|$)',
        content_str,
        flags=re.S,
    )
    if m_expected:
        tmp = _norm_text(m_expected.group(1))
        fields['expected_announcement_date'] = tmp or None
    return fields

def _parse_release_date(s: str) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None

async def save_tenders_to_db(items: list[dict]) -> None:
    async with AsyncSessionLocal() as db:
        try:
            from module_tender.service.tender_service import TenderService as _Svc
            await _Svc.ensure_tender_table_schema(db)
        except Exception:
            pass
        print(f"Starting to process {len(items)} items...")
        for item in items or []:
            content = item.get('content') or ''
            parsed = _parse_content_fields(content)

            p_code = item.get('projectCode')
            print(f"Processing project: {p_code} - {item.get('title')}")

            tender = TenderModel(
                project_code=p_code,
                project_name=item.get('title'),
                district=item.get('region'),
                construction_unit=parsed.get('construction_unit'),
                project_stage='招标计划',
                bid_control_price=parsed.get('bid_control_price'),
                construction_scale=parsed.get('construction_scale'),
                construction_content=parsed.get('construction_content'),
                tender_scope=parsed.get('tender_scope'),
                expected_announcement_date=parsed.get('expected_announcement_date'),
                release_time=_parse_release_date(item.get('releaseDate')),
                announcement_website='公共资源',
                pre_qualification_url=_abs_url(item.get('link')),
            )

            try:
                await TenderService.add_tender(tender, db)
                print(f"  -> Inserted successfully: {p_code}")
            except Exception as e:
                print(f"  -> Failed to insert {p_code}: {e}")
                # Print traceback if needed
                # import traceback
                # traceback.print_exc()
                continue

if __name__ == '__main__':
    data = fetch_tender_json()
    results = data.get('result') or []
    asyncio.run(save_tenders_to_db(results))
