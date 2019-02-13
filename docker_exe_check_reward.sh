# check reward

# docker build
# docker build -t select_stock_code_lib -f dockerfile/select_stock_code/Dockerfile_lib .
docker build -t check_reward -f dockerfile/select_stock_code/Dockerfile .

# check reward directory
if [! -d "check_reward/result/reward" ]; then
  mkdir check_reward/result/reward
fi

# environment
SCRIPT_DIR=$(cd $(dirname $0); pwd)

DOWNLOAD_DIR=$SCRIPT_DIR/get_stock_info/stock_data
CHECK_REWARD_RESULT_DIR=$SCRIPT_DIR/check_reward/result/reward
LOG_DIR=$SCRIPT_DIR/helper/log
SELECT_CODE_DIR=$SCRIPT_DIR/check_reward/result/selected_code

export DOWNLOAD_DIR=$DOWNLOAD_DIR
export CHECK_REWARD_RESULT_DIR=$CHECK_REWARD_RESULT_DIR
export LOG_DIR=$LOG_DIR
export SELECT_CODE_DIR=$SELECT_CODE_DIR

echo "DOWNLOAD_DIR: " $DOWNLOAD_DIR
echo "CHECK_REWARD_RESULT_DIR: " $CHECK_REWARD_RESULT_DIR
echo "LOG_DIR: " $LOG_DIR
echo "SELECT_CODE_DIR: " $SELECT_CODE_DIR

# check reward
export COMPOSE_FILE=dockerfile/docker-compose.check_reward.yml
docker-compose up

# remove docker image
docker-compose down -v
docker rmi check_reward
