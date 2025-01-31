import pandas as pd
from typing import Dict, List
import os

from utils.votes_handler import filter_and_count_by_tags, load_total_votes

class StatsHandler:
    def __init__(self, contest_dir: str):
        self.contest_dir = contest_dir
        self.votes_path = os.path.join(contest_dir, "votes.csv")
        self.stats_path = os.path.join(contest_dir, "stats.csv")
        self.stats_per_tag_path = os.path.join(contest_dir, "stats_per_tag.csv")
    
    def calculate_stats(self) -> Dict:
        """투표 데이터를 집계하여 통계를 계산합니다."""
        votes = load_total_votes(self.contest_dir)

        print(self.contest_dir)

        contest_votes = [v for v in votes]
        filtered_df, model_counts, unique_tags, tag_counts_per_model = filter_and_count_by_tags(contest_votes)

        # save tag_counts_per_model to stats.csv
        tag_counts_per_model_df = pd.DataFrame(tag_counts_per_model)
        tag_counts_per_model_df.to_csv(self.stats_per_tag_path, index=True)

        # save model_counts to stats.csv
        model_counts_df = pd.DataFrame(model_counts)
        model_counts_df.to_csv(self.stats_path, index=True)

    # load stats.csv
    def load_stats(self):
        # read to dataframe and convert to series
        return pd.read_csv(self.stats_path, index_col=0).squeeze()

    # load stats_per_tag.csv
    def load_stats_per_tag(self):
        return pd.read_csv(self.stats_per_tag_path, index_col=0)


def process_all_contest_dirs(base_dir: str):
    # base_dir 안의 모든 디렉토리를 순회
    for contest_dir in os.listdir(base_dir):
        full_path = os.path.join(base_dir, contest_dir)
        if os.path.isdir(full_path):
            # 각 디렉토리에 대해 StatsHandler 인스턴스 생성 및 업데이트
            stats_handler = StatsHandler(full_path)
            stats_handler.calculate_stats()

if __name__ == "__main__":

    base_directory = '/Users/jonhpark/Documents/GitHub/blind-test/data/contests'  # 각 contest 디렉토리가 있는 상위 디렉토리 경로
    process_all_contest_dirs(base_directory)