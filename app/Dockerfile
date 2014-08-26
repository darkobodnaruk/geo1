FROM ubuntu:14.04
MAINTAINER Darko Bodnaruk <darko.bodnaruk@gmail.com>

RUN apt-get update && apt-get install -y ssh libmysqlclient-dev python2.7 libgeoip-dev git wget python-pip python2.7-dev mysql-server

WORKDIR /root
RUN git clone https://github.com/darkobodnaruk/geo1.git

WORKDIR /root/geo1/app
RUN pip install -r requirements.txt

RUN chmod +x /root/geo1/app/seed_mysql.sh
RUN /root/geo1/app/seed_mysql.sh
RUN sed -i 's/bind-address\t\t= 127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/my.cnf

CMD python2.7 runserver.py
