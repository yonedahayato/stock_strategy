back_test_return_date=5

sh stock_strategy/strategies_back_test.sh
python check_reward/check_reward.py --back_test_return_date $back_test_return_date
