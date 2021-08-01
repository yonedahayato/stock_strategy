ARG LIB_VERSION=latest
ARG ECR_REPO=gcr.io/gothic-handbook-179013
FROM ${ECR_REPO}/select_stock_code_lib:${LIB_VERSION}

WORKDIR /select_stock_code

# cron setting
COPY ./cron /etc/cron.d
# RUN crontab /etc/cron.d/cron_setting_test.txt
RUN crontab /etc/cron.d/cron_setting.txt

COPY . .

# CMD ./stock_strategy/strategies_back_test.sh
# CMD ./stock_strategy/strategies.sh
CMD ["cron", "-f"]
