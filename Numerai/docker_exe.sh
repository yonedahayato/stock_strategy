IMAGE_NAME=numerai

docker rmi ${IMAGE_NAME}
docker build -t ${IMAGE_NAME} .

DATASET_DIR=$PWD/datasets
docker run -it --rm \
           -v $PWD:/home/numerai \
           -v ${DATASET_DIR}:/home/numerai/datasets \
           -p 8888:8888 \
           ${IMAGE_NAME} /bin/bash
