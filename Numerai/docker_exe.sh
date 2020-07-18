IMAGE_NAME=numerai

docker rmi ${IMAGE_NAME}
docker build -t ${IMAGE_NAME} .
docker run -it --rm \
           -v $PWD:/home/numerai \
           -p 8888:8888 \
           ${IMAGE_NAME} /bin/bash
