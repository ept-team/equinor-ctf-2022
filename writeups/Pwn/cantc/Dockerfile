# sudo docker build -t cantc .
# sudo docker run -d -p 1024:1024 --rm -it cantc

FROM ubuntu:22.04

RUN useradd -d /home/ept/ -m -p ept -s /bin/bash ept
RUN echo "ept:ept" | chpasswd

WORKDIR /home/ept

COPY flag.txt /opt/flag
COPY cantc .

RUN chown -R root:root /home/ept
RUN chmod  -R a+rx /home/ept
USER ept
CMD ./cantc 1024
