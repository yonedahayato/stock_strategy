# Stock Strategy
- 投資戦略のためのスクリプト

# 内容
- データの収集
- データのアップロード / ダウンロード
- 購入 / 売却明羅の決定

# スクリプト
|Name|Description|Date|
|---|---|---|
|(以下フォルダ)|---|
|Numerai|Numerai 用のコード|2020/07|
|check_reward|投資戦略の評価 / バックテスト|
|draw_graph|画像の描写処理? <-これなんのため？ |
|get_stock_info|データの取得 / アップロード / ダウンロード|
|helper|---|
|notification|通知用|
|stock_strategy|メインの投資戦略処理|
|test|test script|
|dockerfile|Dovkerfile まとめ|
|(以下ファイル)|---|
|docker_exe_check_reward.sh|環境構築 / 実行|
|docker_exe_downloader_to_local.sh|環境構築 / 実行|
|docker_exe_select_stock_code.sh|環境構築 / 実行|
|docker_exe_uploader_to_cloud.sh|環境構築 / 実行|
|requirements.txt|環境構築|

---

# 使用方法
# get code list

## get code list nikkei 225
`python get_stock_info/get_new_stock_code.py`

## get historical data
`python get_stock_info/get_stock_data.py`

# get stock data

## to cloud
`./docker_exe_uploader.sh`  

## to local
`./docker_exe_download_to_local.sh`

# select stock code to buy or sell

## docker
`./docker_exe_select_stock_code.sh`

## python
`python stock_strategy/move_average.py`

## shell script
`./stock_strategy/strategies.sh`

# check reward
`./docker_exe_check_reward.sh`
