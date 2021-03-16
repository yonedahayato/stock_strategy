ARG VERSION=latest
ARG ECR_REPO=gcr.io/gothic-handbook-179013
FROM ${ECR_REPO}/select_stock_code_lib:${VERSION}

WORKDIR /select_stock_code

COPY . .

# CMD ./stock_strategy/strategies_back_test.sh
# CMD ./stock_strategy/strategies.sh
CMD ["cron", "-f"]
