FROM ubuntu:xenial

RUN mkdir -p /usr/src/app && mkdir -p /usr/src/install
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install clang-3.8 -y

RUN apt-get install build-essential -y
RUN apt-get install cmake -y
#RUN apt-get install libc++-dev -y
RUN apt-get install wget -y
RUN mkdir -p /usr/include/boost
WORKDIR /usr/include/boost
RUN wget -q -S -O - 'http://downloads.sourceforge.net/project/boost/boost/1.61.0/boost_1_61_0.tar.gz' | tar xz


RUN apt-get install python3 -y
RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip
ADD ./mp5slicer/requirements.txt /usr/src/install/
RUN pip3 install -r /usr/src/install/requirements.txt
RUN apt-get install python3-mysql.connector
RUN pip3 install --upgrade setuptools

ADD ./implisolid /usr/src/install/implisolid/




WORKDIR /usr/src/install/implisolid/lib/
RUN apt-get install mercurial -y
RUN hg clone https://bitbucket.org/eigen/eigen
WORKDIR /usr/src/install/implisolid/pyInterface/
RUN python3 /usr/src/install/implisolid/pyInterface/setupPyInterface.py install




ADD ./mp5slicer/ /usr/src/app/mp5slicer/
WORKDIR /usr/src/app

CMD ["python3", "./mp5slicer/wrapper.py"]
