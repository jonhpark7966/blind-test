# 블라인드 테스트 서비스 명세서

## 개요

- 사진·영상·텍스트 등을 1:1 비교·투표하는 블라인드 테스트 서비스
- 예) 아이폰 vs 갤럭시, 패션 스타일 vs 스타일, 등 다양한 주제
- 투표 결과를 통계적으로 집계 후 공유 (계정 연동·개인정보 기반 퍼스널라이즈)

## 요구사항

### 기능 요구사항

1. **투표 페이지**
   - 임의의 두 후보(또는 여러 후보)의 사진·영상·텍스트를 랜덤으로 표시
   - 사용자가 하나를 선택해 투표할 수 있음

2. **결과 확인 페이지**
   - 사용자가 투표 완료 후 자신의 결과를 일부 표시

3. **결과 통계 페이지**
   - 전체 투표 결과의 요약 통계, 사용자 개인 결과와 비교

4. **데이터 관리**
   - CSV 파일로 투표 결과·계정 등 관리

### 비기능 요구사항

- Streamlit 기반으로 빠른 UI 프로토타이핑
- 확장·유지보수 용이한 구조 (데이터 구조 변경 시에도 대응)

## 데이터 구조

### CSV 파일 (예시)

1. **contests.csv**
   - contest_id : uuid
   - subject_type : string, image, video, text, ...
   - dir_path : string, 파일 경로 ("./contests/1/")
   - contest_name : string, 컨테스트 이름
   - contest_description : string, 컨테스트 설명
   - metadata : json, 컨테스트 메타데이터 (empty 가능함)
   - contest_start_date : datetime, 컨테스트 시작 날짜

2. **votes.csv**
   - 참조 사항: contents 의 dir_path 에 있어야 함, 사용자들이 그 contest의 투표 한 결과를 모아둠.
   - vote_id : uuid
   - user_id : uuid
   - session_id : uuid
   - contest_id : uuid
   - match_number : int
   - chosen_option : string, 선택한 옵션
   - timestamp : datetime, 투표 시간

3. **stats.csv**
   - 참조 사항:  contents 의 dir_path 에 있어야 함, votes.csv에 있는 투표 결과를 집계해서 저장해 둠.
   - total_votes : int, 총 투표 수
   - vote_percentage : dictionary 형태, 전체 또는 각 매치별, 옵션별 투표 수
     (ex)
   { total: { option1 : 12314, option2 :102975},
     match_number: {
        1: { option1 : 12314, option2 :102975},
        2: { option1 : 12314, option2 :102975},
        3: { option1 : 12314, option2 :102975},
        ...
        }
    }

4. **metadata.csv**
   - 참조 사항:  contents 의 dir_path 에 있어야 함, 컨테스트 메타데이터를 저장해 둠.
   - match_number : int
   - filename : string, 파일 이름 ("IMG_0001.jpg")
   - option : string, 옵션 이름 ("iphone")
   - model: string, 모델 이름 ("iphone 15")
   - tags: string list, 태그 리스트
   - 기타 추출가능한 모든 정보들.

## 화면 흐름

### Page1: 투표 화면

1. Contest 목록 (사이드바 상단)
   - 좌측에 현재 진행 중인 컨테스트 및 매치 리스트를 나열한다. (예: 1. s25 vs 116, 2. s25 vs 116 …)  
     - contests.csv 에서 읽어온다, contest_start_date 기준으로 최근 투표가 위로 올라와야함.
   - 사용자가 특정 매치를 선택하면, 중앙 영역에 해당 매치의 콘텐츠(이미지·영상·텍스트 등)를 표시한다.
     - 특정 매치는 url 단계에서 구분이 가능해야 한다.
     - 특정 매치는 선택하면, 다음 매치가 자동으로 표시되어야 한다.
2. Results 메뉴 (사이드바 하단)
   - 내 결과: 내가 투표한 결과 목록, 또는 요약 정보로 Page2로 이동 가능.
   - 전체 통계: 전체 투표 통계 페이지(Page3)로 이동.
3. 콘텐츠 표시 영역
   - 선택된 매치에 대한 자료(예: image, video, text, 3D view)를 표시한다.
   - 각 contest의 metadata.csv 에 있는 정보를 활용해서 콘텐츠를 표시한다, match_number 에 따라 표시되는 콘텐츠가 다르다.
     - 모든 match_number 에서 random 하게 match_number 를 골라서 콘텐츠를 표시한다. 이미 투표한 match_number 는 제외한다.
   - 투표 옵션이 2개 이상인 경우, 무작위 순서로 콘텐츠가 표시된다.
   - 모든 match_number 를 다 소진해서 모든 투표를 완료한 경우, 자동으로 결과페이지(Page2)로 이동한다.
   - metadata.csv 에 있는 tags 를 활용해서 어떤 종류의 투표인지 태그를 표시한다.
4. 투표(Submit) 버튼
   - 사용자는 표시된 두 후보 중 하나를 연속적으로 계속 선택한다.
   - submit 버튼은 항상 존재하며, submit 버튼을 누르면 투표 결과가 기록되고, 투표가 끝난 후 페이지 2 로 이동한다.
   - submit 버튼을 누르기 전까지는 투표 결과를 session_state 에 저장해두고, 투표가 끝난 후 votes.csv 에 저장한다.
   - submit 버튼을 눌러도 투표 결과는 session_state 에 저장되어 있어야 한다.
   - submit을 눌러 투표를 종료한 후, 다시 이어서 투표를 계속 한 경우, votes.csv 에 저장될 때는 중복 검사를 votes.csv 의 uuid 로 검사해서 중복은 기록하지 않는다.
5. 주요 이동 흐름
   - 매치 선택 → 두 후보 중 택 1 → Submit 누르면 → Page2로 이동
   - 좌측 Results 메뉴 클릭 시 → 내 결과(Page2) 또는 전체 통계(Page3)로 이동

---

### Page2: 개인 결과 및 공유 화면

1. **남들 결과 보기**
   - 전체 통계(Page3)로 바로 이동할 수 있는 버튼(또는 링크)을 제공한다.

2. **공유하기**
   - 나의 투표 결과(예: 어떤 옵션을 골랐는지)를 공유할 수 있는 기능(링크 생성, SNS 연동 등)을 담는다.

3. **내 결과**
   - 각 contest 별로 내 투표 결과를 통계 표시한다. Contest 는 최신 결과가 위로 올라와야 한다.
   - 특정 contest 의 내 투표 결과가 없으면, "결과 없음, 투표하러 가기" 안내를 띄우고 Page1로 이동하는 링크를 제공한다.
   - 투표 이력이 전혀 없으면, "투표 이력이 없습니다. 투표하러 가기" 안내를 띄우고 Page1로 이동하는 링크를 제공한다.
   - 내 결과는 전체 투표 횟수와, 내가 고른 횟수, 고른 비율을 표시한다.  

4. **내 선택 돌아보기**
   - 내가 선택한 후보(이미지·영상) 등을 자세히 다시 확인할 수 있는 상세 페이지(Page4)로 이동시킨다.

5. 주요 이동 흐름
    - Page1에서 투표 완료 → 자동으로 Page2 진입
    - 남들 결과 보기 → Page3 이동  
    - 내 선택 돌아보기 → Page4 이동
    - 결과 없음, 투표하러 가기 → Page1 이동

---

### Page3: 전체 결과 통계 화면

1. **contest별 투표 결과**
   - 예: 1. s25 vs 116, 2. s25 vs 116 각각에 대해 투표 비율, 득표 수를 표시한다.
   - 통계는 stats.csv를 참조해서 보여준다.
   - 전체 투표 결과를 표시한다.
   - 태그별 투표 결과를 표시한다.

2. **다수의 선택 확인하기**
   - 각 매치별 "어떤 옵션이 몇 %로 선택되었는지" 등을 시각화(차트·바그래프)하여 제공한다.

3. **사용자 결과 비교**
   - 세션 정보가 있다면, 내 선택과 전체 선택을 비교해볼 수 있는 정보를 같이 표시한다.

4. **상세 페이지 이동**
   - 각 매치별 결과 항목에서 클릭 시, 해당 매치의 상세 보기 페이지(Page5)로 이동하여 구체적인 이미지·영상 확인이 가능하도록 한다.

5. **주요 이동 흐름**
    - Page2에서 "남들 결과 보기" 클릭 → Page3 진입
    - 매치별 결과 항목 클릭 → Page5로 이동

---

### Page4: '내 선택' 상세 화면

1. **현재 컨테스트 정보**
   - 상단에 Contest 이름을 표시한다.
   - Contest 는 드롭다운 메뉴로, 다른 contest 의 내 선택 결과를 볼 수 있도록 한다.

2. **내가 선택한 후보 표시**
   - 각 매치별로 내가 선택한 후보와 선택하지 않은 후보를 보여준다.
   - 스크롤뷰로 만들어서 모든 매치를 볼 수 있도록 한다.
   - 각 매치는 상단에 매치 번호와, 태그를 보여준다.
   - 각 매치는 이미지·영상 등의 원본과 내가 선택한 후보는 초록색 테두리로, 선택하지 않은 후보는 회색 테두리로 표시한다.
   - 각 매치의 후보는 모델 이름을 함께 표시한다.

3. **이전 화면으로 돌아가기**
   - Page2(개인 결과)나 Page1(투표 화면)로 돌아갈 수 있는 버튼을 제공한다.

4. **주요 이동 흐름**
   - Page2에서 '내 선택 돌아보기' 클릭 → Page4 진입
   - 확인 후, '뒤로 가기' 버튼 → Page2 혹은 Page1 이동

---

### Page5: '남이 선택한 것' 상세 화면

1. **현재 컨테스트 정보**
   - 상단에 컨테스트 이름 표시.

2. **남이 선택한 후보 표시**
   - 각 매치별로 모든 후보에 대해 남들이 선택한 투표수와 비율을 표시한다.
   - 스크롤뷰로 만들어서 모든 매치를 볼 수 있도록 한다.
   - 각 매치는 상단에 매치 번호와, 태그를 보여준다.
   - 각 매치는 이미지·영상 등의 원본과 남이 가장 많이 선택한 후보는 초록색 테두리로, 나머지 후보는 회색 테두리로 표시한다.
   - 각 매치의 후보는 모델 이름을 함께 표시한다.

3. **페이지 이동**
   - Page3(전체 통계)에서 어떤 매치를 선택하면 → Page5로 이동
   - 확인 후, Page3로 돌아갈 수 있는 버튼을 제공한다.

4. **주요 이동 흐름**
   - Page3에서 매치 항목 클릭 → Page5 진입
   - '뒤로 가기' 버튼 → Page3 이동

## 구현 가이드

### Streamlit

- Multi-Page 사용 (page1.py, page2.py 등)

### CSV 관리

- pandas 또는 표준 csv 모듈 사용
- 쓰기 시 동시성 주의(간단 구현: 매 투표마다 파일 append)

### 통계

- 투표 시 CSV 파일 업데이트 후, pandas groupby 등을 사용해 통계 계산
- 성능 이슈 시 임시 stats.csv에 요약본 저장



## 프로젝트 구조

```blind-test/
 ├─ docs/
 │   └─ specs.md                  # 설계 명세 문서(현재 작업 중인 파일)
 ├─ data/
 │   ├─ contests.csv
 │   └─ contests/                 # Contest media files and metadata
 │       ├─ 1/                   # Contest #1 directory
 │       │   ├─ IMG_0001.heic    # Image files
 │       │   ├─ A001_0001.jpg    
 │       │   ├─ votes.csv        # Vote records for contest 1
 │       │   ├─ stats.csv        # Statistics for contest 1
 │       │   └─ metadata.csv     # Metadata for contest 1
 │       │
 │       ├─ 2/                   # Contest #2 directory  
 │       │   ├─ IMG_0001.mp4     # Video files
 │       │   ├─ A001_0001.mov
 │       │   ├─ votes.csv        # Vote records for contest 2
 │       │   ├─ stats.csv        # Statistics for contest 2
 │       │   └─ metadata.csv     # Metadata for contest 2
 │       │
 │       └─ ...                  # Additional contest directories
 ├─ utils/
 │   ├─ metadata_handler.py       # 메타데이터 읽고 쓰는 함수
 │   ├─ stats_handler.py          # 투표 결과 집계·통계 계산 로직
 │   └─ session_manager.py        # session_state 제어, 중복검사 등
 ├─ pages/
 │   ├─ page1_vote.py            # Page1: 투표 화면
 │   ├─ page2_my_result.py       # Page2: 개인 결과/공유 화면
 │   ├─ page3_stats.py           # Page3: 전체 통계 화면
 │   ├─ page4_my_choice.py       # Page4: 내가 선택한 후보 상세 화면
 │   └─ page5_others_choice.py   # Page5: 남들이 선택한 후보 상세 화면
 ├─ main.py                      # Streamlit run 진입점, 페이지 라우팅
 ├─ requirements.txt             # 필요 라이브러리 명시(pandas, streamlit 등)
 └─ README.md                    # 프로젝트 세팅/실행 방법
 ```

### Directory and File Descriptions

1. docs/specs.md

- Overall service specifications, screen flows, and data structure definitions
- Core design document for implementation reference

2. data/*.csv

- Basic data files used in the service
- contests.csv: Contest information

2.1. data/contests/*/*.csv  

- votes.csv: Vote result records
- stats.csv: Statistical aggregation results
- metadata.csv: Match-specific information (filenames, options, models, tags, etc.)

3. utils/

- Collection of reusable logic
- metadata_handler.py:
  - read images or videos from data/contests/*/ and generate metadata.csv
  - metadata.csv 읽고 쓰는 함수
- stats_handler.py:
  - Statistical calculations from votes.csv (vote counts, percentages, etc.)
  - stats.csv updates, tag-based result aggregation
- session_manager.py:
  - Streamlit session_state initialization/control logic
  - Duplicate vote prevention logic

4. pages/

- page1_vote.py:
  - Display contest/match list, show two candidates (random)
  - Vote option selection and submit, save vote data to session_state
  - Auto-redirect to Page2 when all match_numbers are used
- page2_my_result.py:
  - Display personal results (recent vote summary)
  - Guide to voting screen (Page1) if no results exist
  - Sharing feature, link to "View Others' Results (Page3)"
  - Link to "Review My Choices (Page4)"
- page3_stats.py:
  - Overall voting statistics (votes by contest/match, tag-based statistics, etc.)
  - Graph/chart visualizations
  - Navigate to Page5 on match item click
- page4_my_choice.py:
  - Display detailed list/images/model names/tags of chosen candidates
  - Show unselected candidates with gray borders
  - Back button: to Page2 or Page1
- page5_others_choice.py:
  - Display popular candidates (green border) with selection ratios
  - Back button: to Page3

5. main.py

- Streamlit multi-page initial setup, page routing (st.set_page_config, st.sidebar.selectbox, etc.)
- Load or import files from pages directory to compose each page

6. requirements.txt

- Used libraries: pandas, streamlit, plotly (or matplotlib), uuid, etc.