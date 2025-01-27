import csv
import os
import exiftool

def extract_model(meta_dict):
    model_keys = [key for key in meta_dict.keys() if 'Model' in key]
    if 'Model' in model_keys:
        val = meta_dict['Model']
        return val.split(" , ")[0].strip() if " , " in val else val
    for k in model_keys:
        val = meta_dict[k]
        return val.split(" , ")[0].strip() if " , " in val else val
    return None

def extract_create_date(meta_dict):
    if "QuickTime:CreateDate" in meta_dict:
        return meta_dict["QuickTime:CreateDate"]
    return None

def gather_all_keys(meta_list):
    keys = set()
    for d in meta_list:
        keys.update(d.keys())
    return list(keys)

def save_metadata_to_csv(files, output_csv):
    if not files:  # 파일 리스트가 비어있는 경우 처리
        print("처리할 파일이 없습니다.")
        return

    try:
        meta_list = []
        with exiftool.ExifTool() as et:
            # 각 파일별로 메타데이터 추출
            for file in files:
                metadata = et.execute("-j", "-G", file)  # execute 메서드 사용
                if metadata:
                    import json
                    metadata = json.loads(metadata)[0]
                    # CreateDate를 datetime 객체로 변환
                    create_date = extract_create_date(metadata)
                    if create_date:
                        from datetime import datetime
                        try:
                            dt = datetime.strptime(create_date, "%Y:%m:%d %H:%M:%S")
                            metadata["_dt"] = dt
                        except ValueError:
                            metadata["_dt"] = None
                    meta_list.append(metadata)

        if not meta_list:
            print("메타데이터를 추출할 수 없습니다.")
            return

        # 시간 기반 매칭 수행
        match_id = 1
        remaining_videos = meta_list.copy()
        
        while len(remaining_videos) > 1:  # 최소 2개의 영상이 남아있을 때까지
            base_video = remaining_videos[0]
            if not base_video.get("_dt"):
                remaining_videos.pop(0)
                continue
                
            best_idx, best_diff = None, None
            for i, other_video in enumerate(remaining_videos[1:], 1):
                if not other_video.get("_dt"):
                    continue
                diff = abs(base_video["_dt"] - other_video["_dt"])
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    best_idx = i
            
            if best_idx is not None:
                # 매칭된 두 영상에 동일한 Match 번호 부여
                base_video["Match"] = match_id
                remaining_videos[best_idx]["Match"] = match_id
                remaining_videos.pop(best_idx)  # 매칭된 두 번째 영상 제거
                remaining_videos.pop(0)  # 매칭된 첫 번째 영상 제거
                match_id += 1
            else:
                remaining_videos.pop(0)

        # 메타데이터에서 전체 키 수집
        all_keys = gather_all_keys(meta_list)
        
        # CSV 컬럼 순서 결정 (Match 컬럼 추가)
        header = ["Model", "QuickTime:CreateDate", "Match"] + sorted(all_keys)

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()

            for meta_dict in meta_list:
                row = {}
                # Model, Create Date 표준화 추출
                row["Model"] = extract_model(meta_dict)
                row["QuickTime:CreateDate"] = extract_create_date(meta_dict)
                # 나머지 키는 그대로
                for k in all_keys:
                    row[k] = meta_dict.get(k, None)
                writer.writerow(row)
        
        print(f"메타데이터 추출 완료: {len(meta_list)}개 파일 처리됨")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print(f"처리하려던 파일들: {files}")

if __name__ == "__main__":
    directory_path = "/Users/jonhpark/Documents/GitHub/blind-test/contests/2"
    video_files = []
    for file in os.listdir(directory_path):
        if file.lower().endswith(('.mov', '.mp4', '.avi', '.mkv')):
            video_files.append(os.path.join(directory_path, file))

    output_path = os.path.join(directory_path, "video_metadata.csv")
    save_metadata_to_csv(video_files, output_path)