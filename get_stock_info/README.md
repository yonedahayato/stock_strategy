# get code list nikkei 225
```
python get_stock_info/get_new_stock_code.py
```

```
東証１部リスト
,日付,コード,銘柄名,市場・商品区分,33業種コード,33業種区分,17業種コード,17業種区分,規模コード,規模区分
0,20181130,1301,極洋,市場第一部（内国株）,50,水産・農林業,1,食品 ,7,TOPIX Small 2
21,20181130,1332,日本水産,市場第一部（内国株）,50,水産・農林業,1,食品 ,4,TOPIX Mid400
22,20181130,1333,マルハニチロ,市場第一部（内国株）,50,水産・農林業,1,食品 ,4,TOPIX Mid400
29,20181130,1352,ホウスイ,市場第一部（内国株）,6050,卸売業,13,商社・卸売 ,7,TOPIX Small 2

日経２２５リスト
,コード
0,4151
1,4502
2,4503
3,4506
4,4507
5,4519
6,4523
```

# get historical data
- jsm APIを使用
```
python get_stock_info/get_stock_data.py
```

```
Date,Open,High,Low,Close,Adj_Close,Vloume
2017-01-04,568,576,563,571,571,2798500
2017-01-05,572,573,565,568,568,2162900
2017-01-06,567,576,563,575,575,2125600
2017-01-10,573,576,561,562,562,2744600
2017-01-11,559,562,551,553,553,2231800
2017-01-12,553,556,543,544,544,2579700
2017-01-13,543,554,541,553,553,2485700
2017-01-16,547,549,535,538,538,2797800
2017-01-17,536,538,520,520,520,2814100
2017-01-18,524,544,523,537,537,4200700
```

# get historical data and save to local
使用する前にスレッド数を設定
```
sudo python get_stock_data_to_local.py
```

# get exchange data
- get_exchange_data/get_exchange_data.py
  - 為替や指標のヒストリカルデータを取得
  - pandas data reader を利用してのデータの取得が可能
   - [参考](https://python.askbox.net/2018/06/10/python%E3%81%A7%E7%82%BA%E6%9B%BF%E3%83%AC%E3%83%BC%E3%83%88%E3%82%92csv%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AB%E6%9B%B8%E3%81%8D%E5%87%BA%E3%81%99/)

- get_exchange_data/get_exchange_data_from_oanda.py
  - OANDA API を使用を利用して、ヒストリカルデータを使用
    - [参考: pythonで為替データを取ってきて移動平均、ボリンジャーバンド、ゴールデンクロス、デッドクロスを可視化](http://swdrsker.hatenablog.com/entry/2018/05/18/070000)
    - [参考: 過去の為替レートデータをPandasで読み込んでティックから1分へ変更してみた](http://www.algo-fx-blog.com/archived-fx-dataset-tick-to-1min/)

- get_exchange_data/get_exchange_data_from_yahooF.py
  - yahoo finance からスクレイピンングしてヒストリカルデータをクローリングする。
  - 高頻度の使用は厳禁

```
python get_exchange_data/get_exchange_data.py
```

```
DATE,Close
2016-01-01,
2016-01-04,119.3
2016-01-05,118.95
2016-01-06,118.54
2016-01-07,118.0
2016-01-08,117.74
2016-01-11,117.48
2016-01-12,117.78
2016-01-13,118.06
2016-01-14,118.03
2016-01-15,116.78
2016-01-18,
2016-01-19,117.66
```
