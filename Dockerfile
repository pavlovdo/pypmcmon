FROM centos:latest
LABEL maintainer="Denis O. Pavlov pavlovdo@gmail.com"

ARG project

RUN dnf update -y && dnf install -y \ 
        cronie \
        git \
        epel-release \
        vi

RUN dnf install -y \
        python3-requests \
        python3-pip && \
        rm -rf /var/cache/dnf

COPY *.py requirements.txt /etc/zabbix/externalscripts/${project}/
WORKDIR /etc/zabbix/externalscripts/${project}

RUN pip3 install -r requirements.txt 

ENV TZ=Europe/Moscow
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime

RUN echo "*/1 * * * * /usr/local/orbit/pypmcmon/pypmcmon.py" > /tmp/crontab && \
        crontab /tmp/crontab && rm /tmp/crontab

CMD ["crond","-n"]