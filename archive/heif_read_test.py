import csv
import json
import subprocess
import exiftool
import os
from datetime import datetime

directory = "./1"

def parse_exif_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except:
        return None

def get_exif_metadata(file_path):
    try:
        cmd = ["exiftool", "-j", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            print(f"Error processing {file_path}: {result.stderr}")
            return {}
        data = json.loads(result.stdout)
        return data[0] if data else {}
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return {}

# 1. 폴더 내 모든 파일의 메타데이터 수집
metadata_list = []
for file in os.listdir(directory):
    if file.lower().endswith((".heic", ".jpg")):
        file_path = os.path.join(directory, file)
        metadata = get_exif_metadata(file_path)
        metadata["File Name"] = file
        metadata_list.append(metadata)

# 2. Galaxy S24 Ultra / iPhone 16 Pro Max 분류
galaxy_list = []
iphone_list = []
for md in metadata_list:
    model = md.get("Model", "")
    create_date_str = md.get("CreateDate", "")
    dt = parse_exif_date(create_date_str)
    if dt:
        md["_dt"] = dt  # 내부용(정렬·계산용)
    # 기기명은 예시
    if model == "Galaxy S24 Ultra":
        galaxy_list.append(md)
    elif model == "iPhone 16 Pro Max":
        iphone_list.append(md)

galaxy_list.sort(key=lambda x: x.get("_dt") or datetime.min)
iphone_list.sort(key=lambda x: x.get("_dt") or datetime.min)

# 3. 가장 가까운 CreateDate끼리 매칭
match_id = 1
for g in galaxy_list:
    if not g.get("_dt"):
        continue
    best_idx, best_diff = None, None
    for i, ip in enumerate(iphone_list):
        if not ip.get("_dt"):
            continue
        diff = abs(g["_dt"] - ip["_dt"])
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_idx = i
    if best_idx is not None:
        # 매칭된 두 사진에 동일한 Match 번호 부여
        g["Match"] = match_id
        iphone_list[best_idx]["Match"] = match_id
        iphone_list.pop(best_idx)  # 중복 매칭 방지
        match_id += 1

# 4. CSV로 저장
if metadata_list:
    # 모든 키(열) 수집
    fieldnames = set()
    for m in metadata_list:
        fieldnames.update(m.keys())
    fieldnames = list(fieldnames)

    with open(os.path.join(directory, "metadata.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)