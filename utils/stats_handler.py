import pandas as pd
import json
from typing import Dict, List
import os

class StatsHandler:
    def __init__(self, contest_dir: str):
        self.contest_dir = contest_dir
        self.votes_path = os.path.join(contest_dir, "votes.csv")
        self.stats_path = os.path.join(contest_dir, "stats.csv")
    
    def calculate_stats(self) -> Dict:
        """투표 데이터를 집계하여 통계를 계산합니다."""
        votes_df = pd.read_csv(self.votes_path)
        
        # 전체 통계 계산
        total_stats = votes_df.groupby('chosen_option').size().to_dict()
        
        # 매치별 통계 계산
        match_stats = {}
        for match_num in votes_df['match_number'].unique():
            match_votes = votes_df[votes_df['match_number'] == match_num]
            match_stats[str(match_num)] = match_votes.groupby('chosen_option').size().to_dict()
            
        # 모델과 태그 조합별 통계 계산
        model_tag_stats = votes_df.groupby(['model', 'tag']).size().reset_index(name='count').to_dict(orient='records')
        
        return {
            'total': total_stats,
            'match_number': match_stats,
            'model_tag': model_tag_stats
        }
    
    def update_stats(self):
        """통계를 계산하여 stats.csv 파일에 저장합니다."""
        stats = self.calculate_stats()
        stats_df = pd.DataFrame({
            'total_votes': [sum(stats['total'].values())],
            'vote_percentage': [json.dumps(stats)]
        })
        stats_df.to_csv(self.stats_path, index=False) 

def process_all_contest_dirs(base_dir: str):
    # base_dir 안의 모든 디렉토리를 순회
    for contest_dir in os.listdir(base_dir):
        full_path = os.path.join(base_dir, contest_dir)
        if os.path.isdir(full_path):
            # 각 디렉토리에 대해 StatsHandler 인스턴스 생성 및 업데이트
            stats_handler = StatsHandler(full_path)
            stats_handler.update_stats()

if __name__ == "__main__":
    base_directory = '/Users/jonhpark/Documents/GitHub/blind-test/data/contests'  # 각 contest 디렉토리가 있는 상위 디렉토리 경로
    process_all_contest_dirs(base_directory)