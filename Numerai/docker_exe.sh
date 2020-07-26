IMAGE_NAME=numerai

docker rmi ${IMAGE_NAME}
docker build -t ${IMAGE_NAME} .

DATASET_DIR=$PWD/dataset
HOST_JUPYTER_PORT=8888
docker run -it --rm \
           -v $PWD:/home/numerai \
           -v ${DATASET_DIR}:/home/numerai/dataset \
           -p HOST_JUPYTER_PORT:8888 \
           ${IMAGE_NAME} /bin/bash
