IMAGE_NAME=cron_test

docker rmi ${IMAGE_NAME}
docker build -t ${IMAGE_NAME} -f ./dockerfile/Dockerfile_cron .

docker run -it --rm \
           -v $PWD/test:/home/test \
           ${IMAGE_NAME}

# docker rmi ${IMAGE_NAME}
