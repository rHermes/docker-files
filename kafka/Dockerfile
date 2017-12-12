FROM openjdk:8-jre-alpine

# install bash because we need it
RUN apk add --no-cache bash

WORKDIR /setup

RUN wget -q "https://www.apache.org/dist/kafka/1.0.0/kafka_2.11-1.0.0.tgz"

RUN tar -xf kafka_2.11-1.0.0.tgz
RUN rm kafka_2.11-1.0.0.tgz

WORKDIR kafka_2.11-1.0.0



# Figure out this authentication later.
# RUN wget -q "https://www.apache.org/dist/kafka/1.0.0/kafka_2.11-1.0.0.tgz.asc"

# bin/kafka-server-start.sh config/server.properties --override zookeeper.connect=zookeeper:2181 --override broker.id=-1<Paste>

# ENV JMX_PORT=9999

EXPOSE 9092
# EXPOSE 9999

