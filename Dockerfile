FROM --platform=linux/amd64 amazon/aws-lambda-python:3.9

ENV IS_AWS_LAMBDA=1

ARG FUNCTION_DIR="/var/task"
WORKDIR ${FUNCTION_DIR}

RUN mkdir -p ${FUNCTION_DIR}/bin

COPY . ${FUNCTION_DIR}

RUN python -m pip install -r ${FUNCTION_DIR}/requirements-lock.txt \
        --target ${FUNCTION_DIR} \
        --no-cache-dir

CMD ["zappa.handler.lambda_handler"]
