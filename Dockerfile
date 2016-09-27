FROM ubuntu:trusty

RUN mkdir -p /usr/src/app && mkdir -p /usr/src/install
WORKDIR /usr/src/app

RUN apt-get update

RUN apt-get install python3 -y
RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip
ADD ./requirements.txt /usr/src/install/
RUN pip3 install -r /usr/src/install/requirements.txt
RUN apt-get install python3-mysql.connector

RUN apt-get install clang-3.8 -y

RUN apt-get install libboost-all-dev -y

RUN apt-get install libeigen3-dev -y

RUN python ../solidmodeler/setupPyInterface.py install



ADD ./slicer/ /usr/src/app

#RUN pip2 install --no-cache-dir -r ./requirement.txt
CMD ["python3", "./slicer/wrapper.py"]