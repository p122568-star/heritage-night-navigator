import requests
import datetime
import os
import json

# ==========================================
# 사용자님의 인증키 (KorService2)
# ==========================================
MY_API_KEY = "113da232de1ecb11673d38f4e6e9678ac3421c7a9fc91cc55fff22c1f9cab317"
BASE_URL = "https://apis.data.go.kr/B551011/KorService2"

# ------------------------------------------
# [수동 추가] 국가유산청 선정 2026 야행 55선
# ------------------------------------------
MANUAL_NIGHTS = [
    {"title": "서대문 국가유산 야행", "addr": "서울 성북구"},
    {"title": "송파 국가유산 야행", "addr": "서울 송파구"},
    {"title": "종로 국가유산 야행", "addr": "서울 종로구"},
    {"title": "정동야행", "addr": "서울 중구"},
    {"title": "피란수도 부산 국가유산 야행", "addr": "부산"},
    {"title": "대구 국가유산 야행", "addr": "대구 중구"},
    {"title": "인천개항장 국가유산 야행", "addr": "인천 중구"},
    {"title": "광주 국가유산 야행", "addr": "광주 동구"},
    {"title": "대전 중구 국가유산 야행", "addr": "대전 중구"},
    {"title": "동헌 달빛 한 조각, 병영 별빛 한 바퀴", "addr": "울산 중구"},
    {"title": "고양 행주산성 야행", "addr": "경기 고양시"},
    {"title": "광주시 야행", "addr": "경기 광주시"},
    {"title": "군하(郡下) 야행", "addr": "경기 김포시"},
    {"title": "수원 밤빛 품는 성곽도시", "addr": "경기 수원시"},
    {"title": "양주관아지 야행", "addr": "경기 양주시"},
    {"title": "강릉 국가유산 야행", "addr": "강원 강릉시"},
    {"title": "원주 국가유산 야행", "addr": "강원 원주시"},
    {"title": "정선 국가유산 걷는 박물관", "addr": "강원 정선군"},
    {"title": "철원 국가유산 야행", "addr": "강원 철원군"},
    {"title": "보은 회인 국가유산 야행", "addr": "충북 보은군"},
    {"title": "청주 국가유산 야행", "addr": "충북 청주시"},
    {"title": "충주시 국가유산 야행", "addr": "충북 충주시"},
    {"title": "공주 국가유산 야행", "addr": "충남 공주시"},
    {"title": "강경 국가유산 야행", "addr": "충남 논산시"},
    {"title": "당진 국가유산 야행", "addr": "충남 당진시"},
    {"title": "보령 국가유산 야행", "addr": "충남 보령시"},
    {"title": "부여 국가유산 야행", "addr": "충남 부여군", "start": "20260418", "end": "20260420"},
    {"title": "서천 국가유산 야행", "addr": "충남 서천군"},
    {"title": "아산 외암마을 야행", "addr": "충남 아산시"},
    {"title": "홍주읍성 야행", "addr": "충남 홍성군"},
    {"title": "군산 국가유산 야행", "addr": "전북 군산시"},
    {"title": "김제 국가유산 야행", "addr": "전북 김제시"},
    {"title": "무주 국가유산 야행", "addr": "전북 무주군"},
    {"title": "익산 국가유산 야행", "addr": "전북 익산시"},
    {"title": "전주 국가유산 야행", "addr": "전북 전주시"},
    {"title": "정읍 국가유산 야행", "addr": "전북 정읍시"},
    {"title": "고흥 국가유산 야행", "addr": "전남 고흥군"},
    {"title": "담양 국가유산 야행", "addr": "전남 담양군"},
    {"title": "목포 문화유산 야행", "addr": "전남 목포시"},
    {"title": "순천 국가유산 야행", "addr": "전남 순천시"},
    {"title": "여수 국가유산 야행", "addr": "전남 여수시"},
    {"title": "영암 국가유산 야행", "addr": "전남 영암군"},
    {"title": "경주 국가유산 야행", "addr": "경북 경주시"},
    {"title": "고령 국가유산 야행", "addr": "경북 고령군"},
    {"title": "상주 국가유산 야행", "addr": "경북 상주시"},
    {"title": "안동 월영야행", "addr": "경북 안동시"},
    {"title": "영덕 국가유산 야행", "addr": "경북 영덕군"},
    {"title": "포항 흥해야행", "addr": "경북 포항시"},
    {"title": "고성 국가유산 야행", "addr": "경남 고성군"},
    {"title": "김해 국가유산 야행", "addr": "경남 김해시"},
    {"title": "밀양 국가유산 야행", "addr": "경남 밀양시"},
    {"title": "진주 국가유산 야행", "addr": "경남 진주시"},
    {"title": "함안 국가유산 야행", "addr": "경남 함안군"},
    {"title": "함양 고운길 달빛 기행", "addr": "경남 함양군"},
    {"title": "제주 국가유산 야행", "addr": "제주"}
]

def fetch_tour_data(operation, params):
    """TourAPI 4.0 (KorService2) 호출 함수"""
    url = f"{BASE_URL}/{operation}"
    all_params = params.copy()
    all_params['serviceKey'] = MY_API_KEY
    all_params['_type'] = 'json'
    all_params['MobileOS'] = 'WIN'
    all_params['MobileApp'] = 'FestivalNavigator'
    
    try:
        resp = requests.get(url, params=all_params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            body = data.get('response', {}).get('body', {})
            items_container = body.get('items', {})
            if not items_container: return []
            
            item_list = items_container.get('item', [])
            if isinstance(item_list, dict):
                return [item_list]
            return item_list
        return []
    except Exception as e:
        print(f"에러 발생: {e}")
        return []

def main():
    print("=" * 50)
    print("Heritage Night & Festival Navigator (PRO)")
    print("=" * 50)
    
    today = datetime.datetime.now().strftime("%Y%m%d")
    print(f"데이터 수집 중... (기준일: {today})")
    
    # 1. API 데이터 수집 (축제)
    print("- 전국 실시간 축제 정보 수집 중...")
    festivals = fetch_tour_data("searchFestival2", {
        "numOfRows": "500",
        "pageNo": "1",
        "eventStartDate": "20260101", # 올해 전체 데이터를 가져오도록 변경
        "arrange": "A"
    })
    
    # 데이터 가공
    all_items = []
    processed_titles = set()
    
    # 2. 수동 야행 데이터 추가 (55선)
    print("- 국가유산 야행 55선 데이터 통합 중...")
    for night in MANUAL_NIGHTS:
        processed_titles.add(night['title'])
        all_items.append({
            "title": night['title'],
            "eventstartdate": night.get('start', "20260501"), # 날짜 미정 시 임시 5월
            "eventenddate": night.get('end', "20261031"),
            "addr1": night['addr'],
            "type": "heritage_night",
            "firstimage": "",
            "description": f"국가유산청 선정 2026 주요 야행: {night['title']}입니다."
        })

    # 3. API 데이터 통합 (중복 제외)
    for item in (festivals or []):
        title = item.get('title', '')
        if not title or title in processed_titles: continue
        processed_titles.add(title)
        
        all_items.append({
            "title": title,
            "eventstartdate": str(item.get('eventstartdate', today)),
            "eventenddate": str(item.get('eventenddate', today)),
            "addr1": item.get('addr1', '주소 정보 없음'),
            "type": "heritage_night" if '야행' in title else "festival",
            "firstimage": item.get('firstimage', ''),
            "description": f"{title} 정보를 확인하세요."
        })

    # 시작일 순으로 정렬
    all_items.sort(key=lambda x: x['eventstartdate'])

    # JSON/JS 저장
    result = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": all_items
    }
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write("const festivalData = ")
        json.dump(result, f, ensure_ascii=False, indent=4)
        f.write(";")
        
    print(f"\n[성공] 총 {len(all_items)}개의 데이터를 통합 수집했습니다.")
    print(f"(부여 야행 등 주요 야행 55선이 포함되었습니다.)")

if __name__ == "__main__":
    main()
