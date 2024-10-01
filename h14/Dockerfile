FROM python:3.8-slim

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir aiohttp async_timeout

EXPOSE 8080

CMD /bin/bash -c 'timeout 10 python3 ycrawler.py; /bin/bash'
