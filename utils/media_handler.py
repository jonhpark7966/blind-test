from PIL import Image
import pillow_heif
import os
import streamlit as st

def load_media(file_path, metadata_handler):
    """이미지나 비디오 파일을 로드합니다."""
    file_ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.heic']:
        if file_ext == '.heic':
            heif_file = pillow_heif.read_heif(file_path)
            img = Image.frombytes(
                heif_file.mode, 
                heif_file.size, 
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            
        else:
            # GALAXY Orient handling
            img = Image.open(file_path)
        
            # metadata_handler에서 orientation 정보 가져오기
            orientation = metadata_handler.get_orientation(file_name)

            # orientation에 따라 이미지 회전
            if orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 5:
                img = img.rotate(90, expand=True)
            elif orientation == 8:
                img = img.rotate(180, expand=True)
        
        return img
    else:  # 비디오 파일
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
    
        if file_ext in ['.mov', '.mp4', '.avi']:
            return file_path
        else:
            return None
       # with open(file_path, 'rb') as f:
           # return f.read()

def display_media(col, media):
    """미디어를 화면에 표시합니다."""
    # 미디어 타입 확인, string 이면 video, image 는 PIL img
    is_video = (type(media) == str)

    if is_video:
        col.video(media)
    else:
        col.image(media, use_container_width=True) 