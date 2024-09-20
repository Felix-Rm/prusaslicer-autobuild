FROM ubuntu:latest

COPY setup_linux.sh /setup.sh

RUN chmod +x /setup.sh
RUN /setup.sh

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8