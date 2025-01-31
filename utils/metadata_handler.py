import csv
import os
import exiftool
from datetime import datetime
from typing import List, Dict, Optional

import pandas as pd
import streamlit as st


class MetadataHandler:
    def __init__(self, directory: str, read_from_csv: bool = False):
        self.directory = directory
        self.supported_images = ('.heic', '.jpg', '.jpeg', '.png')
        self.supported_videos = ('.mov', '.mp4', '.avi', '.mkv')
        self.read_from_csv = read_from_csv

        if read_from_csv:
            print("Reading metadata from csv")
            self.metadata = self.read_metadata_from_csv()
    
    def read_metadata_from_csv(self):
        metadata_df = pd.read_csv(os.path.join(self.directory, "metadata.csv"))
        return metadata_df.to_dict(orient='records')

    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except:
            return None

    @st.cache_data
    def extract_metadata(self, file_path: str) -> Dict:
        try:
            with exiftool.ExifTool() as et:
                metadata_str = et.execute("-j", "-G", file_path)
                if not metadata_str:
                    return {}
                import json
                metadata = json.loads(metadata_str)[0]
                
                filename = os.path.basename(file_path)
                create_date = metadata.get('QuickTime:CreateDate') or metadata.get('EXIF:CreateDate')
                model = (metadata.get('EXIF:Model') or 
                        metadata.get('QuickTime:Model') or 
                        metadata.get('MakerNotes:SamsungModel'))
                if model:
                    model = model.split(" , ")[0].strip()
                
                # 방향 정보 추출
                orientation = (metadata.get('EXIF:Orientation') or 
                             metadata.get('Composite:Rotation') or
                             metadata.get('File:Rotation'))
                
                dt = self.parse_date(create_date)
                base_metadata = {
                    'FileName': filename,
                    'Model': model,
                    'CreateDate': create_date,
                    'Orientation': orientation,  # 방향 정보 추가
                    '_dt': dt,
                    'Option': None,
                    'Tags': []
                }
                filtered_metadata = {
                    k: v for k, v in metadata.items() if v is not None and str(v).strip()
                }
                return {**base_metadata, **filtered_metadata}
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return {}

    @st.cache_data
    def match_files(self, metadata_list: List[Dict]) -> List[Dict]:
        valid_files = [m for m in metadata_list if m.get('_dt')]
        remaining_files = valid_files.copy()
        match_id = 1

        while len(remaining_files) > 1:
            base_file = remaining_files[0]
            best_match_idx = None
            best_time_diff = None

            for i, other_file in enumerate(remaining_files[1:], 1):
                if base_file['Model'] == other_file['Model']:
                    continue
                time_diff = abs(base_file['_dt'] - other_file['_dt'])
                if best_time_diff is None or time_diff < best_time_diff:
                    best_time_diff = time_diff
                    best_match_idx = i

            if best_match_idx is not None:
                base_file['Match'] = match_id
                base_file['Option'] = 'option1'
                remaining_files[best_match_idx]['Match'] = match_id
                remaining_files[best_match_idx]['Option'] = 'option2'
                remaining_files.pop(best_match_idx)
                remaining_files.pop(0)
                match_id += 1
            else:
                remaining_files.pop(0)

        for metadata in metadata_list:
            if 'Match' not in metadata:
                metadata['Match'] = None

        return metadata_list

    def process_directory(self) -> None:
        contests_dir = self.directory
        for contest_dir in os.listdir(contests_dir):
            contest_path = os.path.join(contests_dir, contest_dir)
            if not os.path.isdir(contest_path):
                continue

            print(f"Processing: {contest_path}")
            metadata_list = []

            for file in os.listdir(contest_path):
                if file.lower().endswith(self.supported_images + self.supported_videos):
                    file_path = os.path.join(contest_path, file)
                    metadata = self.extract_metadata(file_path)
                    if metadata:
                        metadata_list.append(metadata)

            if not metadata_list:
                print(f"No media files in: {contest_path}")
                continue

            matched = self.match_files(metadata_list)
            primary_cols = ['FileName', 'Model', 'CreateDate', 'Match', 'Orientation','tag']
            all_cols = set()
            for m in matched:
                all_cols.update(m.keys())
            ordered_cols = primary_cols + [c for c in sorted(all_cols) if c not in primary_cols and c != '_dt']

            output_csv = os.path.join(contest_path, "metadata.csv")
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ordered_cols)
                writer.writeheader()
                for data in matched:
                    row = {k: data.get(k) for k in ordered_cols}
                    writer.writerow(row)

            print(f"Created {output_csv} with {len(matched)} entries.")

    def get_matches(self) -> List[Dict]:
        """Returns a list of matched metadata pairs from the directory."""

        if self.read_from_csv:
            return self.metadata

        metadata_list = []
        
        # Collect metadata from all files in directory
        for file in os.listdir(self.directory):
            if file.lower().endswith(self.supported_images + self.supported_videos):
                file_path = os.path.join(self.directory, file)
                metadata = self.extract_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)
        
        # Match the files and return the result
        return self.match_files(metadata_list)
    
    def get_orientation(self, filename: str) -> Optional[int]:
        """
        Get the orientation value for a given filename from its metadata.
        
        Args:
            filename (str): The name of the file to get orientation for
            
        Returns:
            Optional[int]: The orientation value if found, None otherwise
        """
        if self.read_from_csv:
            metadata = next((m for m in self.metadata if m['FileName'] == filename), None)
            return metadata.get('Orientation')

        file_path = os.path.join(self.directory, filename)
        if os.path.exists(file_path):
            metadata = self.extract_metadata(file_path)
            return metadata.get('Orientation')
        return None
    
    def get_tag(self, filename: str) -> Optional[str]:
        if self.read_from_csv:
            metadata = next((m for m in self.metadata if m['FileName'] == filename), None)
            return metadata.get('tag')

    @staticmethod
    def get_contests_for_session(session_id: str) -> List[Dict]:
        """Retrieve all contests associated with a given session ID."""
        contests_dir = "data/contests"
        contests = []

        for contest_id in os.listdir(contests_dir):
            contest_path = os.path.join(contests_dir, contest_id)
            if not os.path.isdir(contest_path):
                continue

            votes_file = os.path.join(contest_path, "votes.csv")
            if not os.path.exists(votes_file):
                continue

            votes_df = pd.read_csv(votes_file)
            if session_id in votes_df['session_id'].values:
                contest_metadata = {
                    'contest_id': contest_id,
                    'name': contest_id  # Assuming contest_id is used as the name; adjust if there's a different naming convention
                }
                contests.append(contest_metadata)

        return contests


@st.cache_data
def get_metadata_handler(dir_path):
    return MetadataHandler(dir_path, read_from_csv=True)


if __name__ == "__main__":
    # Example Usage: python3 metadata_handler.py ../data/contests/
    import sys
    if len(sys.argv) != 2:
        print("Usage: python metadata_handler.py <directory_path>")
        sys.exit(1)
    
    handler = MetadataHandler(sys.argv[1])
    handler.process_directory()
