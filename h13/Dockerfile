FROM debian:9-slim

WORKDIR /root/cext
COPY . /root/cext

RUN echo "deb http://archive.debian.org/debian/ stretch main contrib" >/etc/apt/sources.list
RUN echo "deb-src  http://archive.debian.org/debian/ stretch main contrib" >>/etc/apt/sources.list

RUN apt update \
    && apt clean \
    && apt -y --no-install-recommends --allow-downgrades install \
        gcc protobuf-c-compiler libprotobuf-c-dev zlib1g=1:1.2.8.dfsg-5 zlib1g-dev \
        python3 python3-dev python3-pip python3-setuptools \
    && pip3 install --no-cache-dir -q -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

RUN protoc-c --c_out=deviceapps/. deviceapps/deviceapps.proto
RUN python3 setup.py build_ext --inplace \
    && python3 setup.py test

