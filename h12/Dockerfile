FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

COPY requirements.txt /
RUN pip install --no-cache-dir -q -r requirements.txt

WORKDIR /app
COPY . /app

#CMD ["python", "memc_load_fast.py", "--pattern=/data/*.tsv.gz"]