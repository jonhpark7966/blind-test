import os

# 이미지 폴더 경로
folder_path = "images"

# 폴더 내 파일 리스트 불러오기
files = sorted(os.listdir(folder_path))

# 파일 리스트에서 이미지 파일만 필터링 (확장자가 jpg, png 등인 경우)
image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

# 파일 개수 확인 및 반으로 나누기
total_files = len(image_files)
half = total_files // 2

# G 그룹 이름 변경
for idx, file_name in enumerate(image_files[:half], start=1):
    old_path = os.path.join(folder_path, file_name)
    new_name = f"G.{idx}{os.path.splitext(file_name)[1]}"  # 원래 확장자 유지
    new_path = os.path.join(folder_path, new_name)
    os.rename(old_path, new_path)

# I 그룹 이름 변경
for idx, file_name in enumerate(image_files[half:], start=1):
    old_path = os.path.join(folder_path, file_name)
    new_name = f"I.{idx}{os.path.splitext(file_name)[1]}"  # 원래 확장자 유지
    new_path = os.path.join(folder_path, new_name)
    os.rename(old_path, new_path)

print("이미지 이름 변경 완료!")