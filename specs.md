# 블라인드 테스트 서비스 명세서

## 개요

- 사진·영상·텍스트 등을 1:1 또는 N:1 형식으로 비교·투표하는 블라인드 테스트 서비스
- 예) 아이폰 vs 갤럭시, 패션 스타일 vs 스타일, 등 다양한 주제
- 투표 결과를 통계적으로 집계 후 공유(계정 연동·개인정보 기반 퍼스널라이즈)

## 요구사항

### 기능 요구사항

1. **투표 페이지**
   - 임의의 두 후보(또는 여러 후보)의 사진·영상·텍스트를 랜덤으로 표시
   - 사용자가 하나를 선택해 투표할 수 있음

2. **결과 확인 페이지**
   - 사용자가 투표 완료 후 자신의 결과를 일부 표시
   - 다른 사용자들의 투표 결과도 통계적으로 표시(성별, 나이대 등)

3. **결과 통계 페이지**
   - 전체 투표 결과의 요약 통계, 사용자 개인 결과와 비교
   - 회원 가입(또는 계정 연동) 시 데이터 저장 및 유지

4. **데이터 관리**
   - 초기에 CSV 파일로 투표 결과·계정 등 관리
   - 향후 사용자가 늘어나면 PostgreSQL 등으로 이전

### 비기능 요구사항

- Streamlit 기반으로 빠른 UI 프로토타이핑
- 간단한 구글 OAuth 또는 계정 로그인
- 확장·유지보수 용이한 구조(데이터 구조 변경 시에도 대응)

## 데이터 구조

### CSV 파일 (예시)

1. **contests.csv**
   - contest_id, subject_type, file_path, metadata(json), ...

2. **votes.csv**
   - vote_id, user_id, session_id, contest_id, chosen_option, timestamp, tags(json), ...

3. **users.csv**
   - user_id, google_account, gender, age_range, ...

4. **stats.csv** (선택)
   - 집계된 결과(캐싱용)

### 이후 DB 전환 시 스키마

- **Contests 테이블**: (id, subject_type, metadata, …)
- **Votes 테이블**: (id, user_id, contest_id, chosen_option, timestamp, …)
- **Users 테이블**: (id, google_email, gender, age_range, …)

## 화면 흐름

1. **Page1**: 랜덤 대결(이미지·텍스트·영상 등) 표시 → 투표(submit)
2. **Page2**: 사용자 개인 결과 일부 표시, 공유 기능 → 다른 사람 결과 보기
3. **Page3**: 전체 결과 통계 및 사용자 결과 비교, 회원 가입 후 데이터 저장

## 구현 가이드

### Streamlit

- Multi-Page 사용 (page1.py, page2.py 등)
- st.file_uploader(이미지·영상), st.button, st.radio 등을 활용

### CSV 관리

- pandas 또는 표준 csv 모듈 사용
- 쓰기 시 동시성 주의(간단 구현: 매 투표마다 파일 append)

### 구글 OAuth

- streamlit-authenticator 또는 OAuth 라이브러리 검토

### 통계

- 투표 시 CSV 파일 업데이트 후, pandas groupby 등을 사용해 통계 계산
- 성능 이슈 시 임시 stats.csv에 요약본 저장

## 차후 확장

- PostgreSQL 등 DB로 이전
- 다양한 분석(나이·지역·선호도별 추천)
- 메타데이터(카메라 모델, EXIF) 등 자동 수집
- 이미지·영상 인퍼런스를 통한 태그 자동화
