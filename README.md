# Stock Strategy
- 投資戦略のためのスクリプト

# 内容
- データの収集
- データのアップロード / ダウンロード
- 購入 / 売却明羅の決定

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
