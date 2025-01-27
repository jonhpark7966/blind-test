import pandas as pd
import os
import json
from typing import Dict, List, Optional

class MetadataHandler:
    def __init__(self, contest_dir: str):
        self.contest_dir = contest_dir
        self.metadata_path = os.path.join(contest_dir, "metadata.csv")
    
    def read_metadata(self) -> pd.DataFrame:
        """메타데이터 CSV 파일을 읽어옵니다."""
        if os.path.exists(self.metadata_path):
            return pd.read_csv(self.metadata_path)
        return pd.DataFrame()
    
    def get_match_metadata(self, match_number: int) -> Dict:
        """특정 매치 번호의 메타데이터를 반환합니다."""
        df = self.read_metadata()
        match_data = df[df['match_number'] == match_number]
        if match_data.empty:
            return {}
        return match_data.to_dict('records')
    
    def update_metadata(self, metadata_df: pd.DataFrame):
        """메타데이터를 CSV 파일에 저장합니다."""
        metadata_df.to_csv(self.metadata_path, index=False) 