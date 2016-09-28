FROM ubuntu:trusty

RUN mkdir -p /usr/src/app && mkdir -p /usr/src/install
WORKDIR /usr/src/app

RUN apt-get update

RUN apt-get install python3 -y
RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip
ADD ./slicer/requirements.txt /usr/src/install/
RUN pip3 install -r /usr/src/install/requirements.txt
RUN apt-get install python3-mysql.connector

RUN apt-get install clang-3.8 -y

RUN apt-get install libboost-all-dev -y

RUN pip3 install --upgrade setuptools

RUN apt-get install cmake -y
RUN apt-get install libc++-dev -y

ADD ./solidmodeler /usr/src/install/solidmodeler/


WORKDIR /usr/src/install/solidmodeler/
RUN python3 /usr/src/install/solidmodeler/setupPyInterface.py install




ADD ./slicer/ /usr/src/app

#RUN pip2 install --no-cache-dir -r ./requirement.txt
CMD ["python3", "./slicer/wrapper.py"]
