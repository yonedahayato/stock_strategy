# get stock data

# docker build
# docker build -t get_stock_data_lib -f dockerfile/get_stock_data/Dockerfile_lib .
docker build -t get_stock_data -f dockerfile/get_stock_data/Dockerfile .

# log directory
if [ ! -d "helper/log" ]; then
  mkdir helper/log
fi

# environment
SCRIPT_DIR=$(cd $(dirname $0); pwd)
LOG_DIR=$SCRIPT_DIR/helper/log
export LOG_DIR=$LOG_DIR

. ./dockerfile/get_stock_data/environment.txt
export UPLOAD_DIR=$UPLOAD_DIR

echo "LOG_DIR: " $LOG_DIR
echo "UPLOAD_DIR: " $UPLOAD_DIR

# get stock data
export COMPOSE_FILE=dockerfile/docker-compose.get_stock_data.yml
# docker run -it --rm get_stock_data python get_stock_info/get_stock_data.py
docker-compose up

# remove docker image
# docker rmi get_stock_data_lib
docker rmi get_stock_data
docker-compose down -v
