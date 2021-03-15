# get stock data

# docker build
# docker build -t get_stock_data_lib -f dockerfile/get_stock_data/Dockerfile_lib .

export VERSION=v.0.1
IMAGE_NAME=get_stock_data_to_local:${VERSION}
# docker rmi ${IMAGE_NAME}
docker build -t ${IMAGE_NAME} -f dockerfile/get_stock_data/Dockerfile_to_local .

# log directory
if [ ! -d "helper/log" ]; then
  mkdir helper/log
fi

# environment
SCRIPT_DIR=$(cd $(dirname $0); pwd)
LOG_DIR=$SCRIPT_DIR/helper/log
export LOG_DIR=$LOG_DIR

. ./dockerfile/get_stock_data/environment.txt
export SAVE_DIR=$SAVE_DIR

echo "LOG_DIR: " $LOG_DIR
echo "SAVE_DIR: " $SAVE_DIR

# get stock data
export COMPOSE_FILE=dockerfile/docker-compose.get_stock_data_to_local.yml
docker-compose up
docker-compose down -v

# remove docker image
# docker rmi get_stock_data_lib
# docker rmi ${IMAGE_NAME}
