import csv
import json
import subprocess
import exiftool
import os

directory = "./1"

def get_exif_metadata(file_path):
    """
    exiftool을 통해 메타데이터를 JSON으로 추출한 뒤 파싱해서 딕셔너리로 반환
    """
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


# 폴더 내 모든 파일 처리
# json 저장, 파일 명도 추가되어야함.
metadata_list = []
for file in os.listdir(directory):
    print(file)
    # heic or jpg (case insensitive)
    if file.lower().endswith((".heic", ".jpg")):
        file_path = os.path.join(directory, file)  # Create full path
        metadata = get_exif_metadata(file_path)
        metadata["File Name"] = file
        metadata_list.append(metadata)


# metadata 들을 모두 모아서 csv 파일로 저장
if metadata_list:
    # Get all unique keys from all metadata dictionaries to use as columns
    fieldnames = set()
    for metadata in metadata_list:
        fieldnames.update(metadata.keys())
    
    with open(f"{directory}/metadata.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()  # Write the column headers
        writer.writerows(metadata_list)  # Write each metadata dictionary as a row
