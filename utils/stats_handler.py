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
            
        return {
            'total': total_stats,
            'match_number': match_stats
        }
    
    def update_stats(self):
        """통계를 계산하여 stats.csv 파일에 저장합니다."""
        stats = self.calculate_stats()
        stats_df = pd.DataFrame({
            'total_votes': [sum(stats['total'].values())],
            'vote_percentage': [json.dumps(stats)]
        })
        stats_df.to_csv(self.stats_path, index=False) 