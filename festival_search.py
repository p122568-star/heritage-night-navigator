"""TourAPI festival updater. Failures never replace the last successful snapshot."""
import datetime as dt
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
BASE_URL = 'https://apis.data.go.kr/B551011/KorService2/searchFestival2'

def load_key():
    key = os.environ.get('TOUR_API_KEY', '')
    if not key and (ROOT / '.env').exists():
        for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
            if line.startswith('TOUR_API_KEY='):
                key = line.split('=', 1)[1].strip()
    if not key:
        raise RuntimeError('TOUR_API_KEY 설정이 필요합니다.')
    return key

def collect(key, now):
    items, seen = [], set()
    page = 1
    while True:
        params = dict(serviceKey=key, MobileOS='ETC', MobileApp='FamilyFestival',
                      _type='json', numOfRows=100, pageNo=page,
                      eventStartDate=f'{now.year - 1}0101', arrange='A')
        try:
            with urlopen(BASE_URL + '?' + urlencode(params), timeout=40) as response:
                payload = json.load(response)['response']
        except Exception:
            raise RuntimeError('축제 API 연결 또는 응답 오류입니다. 기존 데이터를 유지합니다.') from None
        header = payload.get('header', {})
        if header.get('resultCode') != '0000':
            raise RuntimeError('축제 API가 요청을 거절했습니다. 인증키와 이용 한도를 확인하세요.')
        body = payload['body']
        raw = (body.get('items') or {}).get('item', [])
        if isinstance(raw, dict):
            raw = [raw]
        for item in raw:
            start, end = str(item.get('eventstartdate', '')), str(item.get('eventenddate', ''))
            try:
                sd, ed = (dt.datetime.strptime(d, '%Y%m%d').date() for d in (start, end))
            except ValueError:
                continue
            if ed < now.date() or ed < sd:
                continue
            ident = str(item.get('contentid') or (item.get('title', '') + start))
            if ident in seen:
                continue
            seen.add(ident)
            items.append(dict(contentid=ident, title=item.get('title', ''),
                              eventstartdate=start, eventenddate=end,
                              addr1=item.get('addr1', '') or '주소 미확인',
                              type='heritage_night' if '야행' in item.get('title', '') else 'festival',
                              firstimage=item.get('firstimage', ''),
                              description='한국관광공사 제공 일정 · 방문 전 주최 측 공지를 확인하세요.'))
        total = int(body.get('totalCount', 0))
        if page * 100 >= total:
            break
        if not raw or page >= 200:
            raise RuntimeError('전체 페이지 수집에 실패했습니다. 기존 데이터를 유지합니다.')
        page += 1
    if not items:
        raise RuntimeError('유효한 행사가 없어 기존 데이터를 유지합니다.')
    items.sort(key=lambda item: item['eventstartdate'])
    return dict(last_updated=now.strftime('%Y-%m-%d %H:%M:%S KST'), items=items)

def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
    result = collect(load_key(), now)
    content = json.dumps(result, ensure_ascii=False, indent=2)
    temp = ROOT / 'data.js.tmp'
    temp.write_text('const festivalData = ' + content + ';\n', encoding='utf-8')
    temp.replace(ROOT / 'data.js')
    print(f"업데이트 완료: {len(result['items'])}개 행사 / {result['last_updated']}")

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(str(exc))
        raise SystemExit(1)
