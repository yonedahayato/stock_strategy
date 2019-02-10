# select stock code

# docker build
# docker build -t select_stock_code_lib -f dockerfile/select_stock_code/Dockerfile_lib .
docker build -t select_stock_code -f dockerfile/select_stock_code/Dockerfile .

# log directory
if [ ! -d "helper/log" ]; then
  mkdir helper/log
fi

# selected code directory
if [! -d "check_reward/result/selected_code" ]; then
  mkdir check_reward/result/selected_code
fi

# environment
SCRIPT_DIR=$(cd $(dirname $0); pwd)

DOWNLOAD_DIR=$SCRIPT_DIR/get_stock_info/stock_data
LOG_DIR=$SCRIPT_DIR/helper/log
SELECT_CODE_DIR=$SCRIPT_DIR/check_reward/result/selected_code
GRAPH_DIR=$SCRIPT_DIR/draw_graph/graphs

export DOWNLOAD_DIR=$DOWNLOAD_DIR
export LOG_DIR=$LOG_DIR
export SELECT_CODE_DIR=$SELECT_CODE_DIR
export GRAPH_DIR=$GRAPH_DIR

echo "DOWNLOAD_DIR: " $DOWNLOAD_DIR
echo "LOG_DIR: " $LOG_DIR
echo "SELECT_CODE_DIR: " $SELECT_CODE_DIR
echo "GRAPH_DIR: " $GRAPH_DIR

# get stock data
export COMPOSE_FILE=dockerfile/docker-compose.select_stock_code.yml
# docker run -it --rm get_stock_data python get_stock_info/get_stock_data.py
docker-compose up

# remove docker image
# docker rmi select_stock_code_lib
docker-compose down -v
docker rmi select_stock_code
