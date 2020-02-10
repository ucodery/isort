FROM python:3

RUN mkdir /isort && cd /isort
COPY . /isort

RUN python3 -m pip install poetry && poetry install

ENTRYPOINT /isort/scripts/test.sh
