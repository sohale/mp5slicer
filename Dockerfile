FROM ubuntu:trusty

RUN mkdir -p /usr/src/app && mkdir -p /usr/src/install
WORKDIR /usr/src/app

RUN apt-get update

RUN apt-get install python3 -y
RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip
ADD ./requirements.txt /usr/src/install/
RUN ls
RUN pip3 install -r /usr/src/install/requirements.txt
RUN apt-get install python3-mysql.connector

ADD . /usr/src/app

#RUN pip2 install --no-cache-dir -r ./requirement.txt
CMD ["python3", "wrapper.py"]