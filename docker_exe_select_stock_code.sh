echo "select stock code"

echo "docker build"
ECR_REPO=gcr.io/gothic-handbook-179013
LIB_VERSION=v.0.4
MAIN_VERSION=v.0.4.1
LIB_IMAGE_NAME=${ECR_REPO}/select_stock_code_lib:${LIB_VERSION}
IMAGE_NAME=${ECR_REPO}/select_stock_code:${MAIN_VERSION}

# docker rmi ${LIB_IMAGE_NAME}
# docker rmi ${IMAGE_NAME}
docker build -t ${LIB_IMAGE_NAME} \
             -f dockerfile/select_stock_code/Dockerfile_lib .
docker build -t ${IMAGE_NAME} \
             -f dockerfile/select_stock_code/Dockerfile \
             --build-arg LIB_VERSION=${LIB_VERSION} .

echo "make log directory"
if [ ! -d "helper/log" ]; then
  mkdir helper/log
fi

echo "make selected code directory"
if [! -d "check_reward/result/selected_code" ]; then
  mkdir check_reward/result/selected_code
fi

echo "set environment"
SCRIPT_DIR=$(cd $(dirname $0); pwd)

DOWNLOAD_DIR=$SCRIPT_DIR/get_stock_info/stock_data
LOG_DIR=$SCRIPT_DIR/helper/log
SELECT_CODE_DIR=$SCRIPT_DIR/check_reward/result/selected_code
GRAPH_DIR=$SCRIPT_DIR/draw_graph/graphs
TEST_DIR=$SCRIPT_DIR/test

export SCRIPT_DIR=$SCRIPT_DIR
export DOWNLOAD_DIR=$DOWNLOAD_DIR
export LOG_DIR=$LOG_DIR
export SELECT_CODE_DIR=$SELECT_CODE_DIR
export GRAPH_DIR=$GRAPH_DIR
export TEST_DIR=$TEST_DIR
export IMAGE_NAME=$IMAGE_NAME

echo "DOWNLOAD_DIR: " $DOWNLOAD_DIR
echo "LOG_DIR: " $LOG_DIR
echo "SELECT_CODE_DIR: " $SELECT_CODE_DIR
echo "GRAPH_DIR: " $GRAPH_DIR

export COMPOSE_FILE=dockerfile/docker-compose.select_stock_code.yml

echo "docker compose up"
# docker run -it --rm get_stock_data python get_stock_info/get_stock_data.py
docker-compose run --service-ports select_stock_code /bin/bash
# docker-compose up

# remove docker image
# docker rmi select_stock_code_lib
docker-compose down -v
# docker rmi ${IMAGE_NAME}
