# result output
## format
```
{
  "code_json_file": select_code の 結果のjson fileのパス,
  "method": method name,
  "data_range_start": 使用したデータの範囲
  "data_range_end": 使用したデータの範囲,
  "stock_list": select_code にて選択した銘柄一覧,
  "reward_results": 各銘柄ごとの成果の結果,
  "creat_time": selecte_code の結果を作成した時間,
  "reward_rate_mean_in_method": 各銘柄ごとの利益の平均,
  "count_winner_brand": {利益が0%以上の銘柄数} / {選択した銘柄数})
  }
```

## setup
1. check_list.pyにバックテストする戦略を追加

## command
```
python check_reward.py
```

# select code output
##format
```
{
  "result_code_list": 選択した銘柄,
  "method": method name,
  "creat_time": 実行した時間,
  "data_range_start_to_compute": 使用したデータの範囲,
  "data_range_end_to_compute": 使用したデータの範囲,
  "back_test_return_date": 使用したデータ直近から何本前のデータまでを使ったか,
  "elapsed_time_average": １銘柄あたりの処理時間
}
