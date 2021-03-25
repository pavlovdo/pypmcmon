FROM centos:latest
LABEL maintainer="Denis O. Pavlov pavlovdo@gmail.com"

ARG project

RUN dnf update -y && \
        dnf install -y \
        epel-release

RUN dnf install -y \
        python3-requests \
        python3-pip && \
        rm -rf /var/cache/dnf

COPY *.py *.json requirements.txt /etc/zabbix/externalscripts/${project}/
WORKDIR /etc/zabbix/externalscripts/${project}

RUN pip3 install -r requirements.txt

ENV TZ=Europe/Moscow
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime

ENTRYPOINT ["/etc/zabbix/externalscripts/pypmcmon/pypmcmon.py"]