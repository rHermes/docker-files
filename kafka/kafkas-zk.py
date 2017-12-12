#!/usr/bin/env python
import docker
import time

PREFIX = 'kafkas'

ZK_IMAGE = 'zookeeper:3.5'
KF_IMAGE = 'rhermes/kafka:latest'

NW_NAME = 'heaven'

ZK_N_INSTANCES = 3
KF_N_INSTANCES = 5

ZK_LABEL_SERVICE = 'bid.boii.service={}_zookeeper'.format(PREFIX)
KF_LABEL_SERVICE = 'bid.boii.service={}_kafka'.format(PREFIX)

# Remove containers who matches the filter.
def clean_f(c,fs):
    for ct in c.containers.list(all=True,filters=fs):
        print(ct)
        ct.stop()
        ct.remove()

def clean_v(c,fs):
    pass
    

def setup_zookeeper(c):
    # I just create the binds and go from there.
    conts = []
    for i in range(ZK_N_INSTANCES):
        j = i+1
        print("Setting up zookeeper instance number: {}".format(j))

        mdata = docker.types.Mount("/data", "{}_zk-{}-data".format(PREFIX,j), labels={'bid.boii.service': '{}_zookeeper'.format(PREFIX)})
        mdatalog = docker.types.Mount("/datalog", "{}_zk-{}-datalog".format(PREFIX,j), labels={'bid.boii.service': '{}_zookeeper'.format(PREFIX)})


        zookeeper_line = " ".join(["server.{}={}_zk-{}:2888:3888;2181".format(i+1, PREFIX, i+1) for i in range(ZK_N_INSTANCES)])
        

        # Creating the ping wait. This will make it so that it waits before launching the zookeeper server, untill all hosts are up.
        # this might prevent them from starting again, but it works for me as it gives good results.
        ping_line = ";".join(["until ping -c5 {}_zk-{} &>/dev/null; do :; done".format(PREFIX, i+1, i+1) for i in range(ZK_N_INSTANCES)])

        conts.append(c.containers.run(
                ZK_IMAGE,
                detach=True,
                name="{}_zk-{}".format(PREFIX,j),
                environment= { "ZOO_MY_ID": j,  "ZOO_SERVERS": zookeeper_line},
                labels={"bid.boii.service": "{}_zookeeper".format(PREFIX)},
                mounts=[mdata, mdatalog],
                network=NW_NAME,
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
                command=["bash", "-c", ping_line + " ; zkServer.sh start-foreground"]
        ))


def setup_kafka(c):
    for i in range(KF_N_INSTANCES):
        j = i+1
        print("Setting up kafka instance number: {}".format(j))

        mlog = docker.types.Mount("/data/kafka-logs", "{}_kf-{}-logs".format(PREFIX,j), labels={'bid.boii.service': '{}_kafka'.format(PREFIX)})


        zookeeper_line = ",".join(["{}_zk-{}:2181".format(PREFIX, i+1) for i in range(ZK_N_INSTANCES)])
        

        cont = c.containers.run(
                KF_IMAGE,
                detach=True,
                name="{}_kf-{}".format(PREFIX,j),
                labels={"bid.boii.service": "{}_kafka".format(PREFIX)},
                mounts=[mlog],
                network=NW_NAME,
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
                command=['bin/kafka-server-start.sh', 'config/server.properties', '--override', 'zookeeper.connect='+zookeeper_line, '--override', 'broker.id='+str(j), '--override', 'default.replication.factor=3', '--override', 'num.partitions=8', '--override', 'log.dirs=/data/kafka-logs']
        )

if __name__ == "__main__":
    client = docker.from_env()

    # Create the network if needed.

    # Make sure that the volumes are here.

    # Clean old zookeeper and old kafkas.
    #clean_f(client,{"label": ZK_LABEL_SERVICE})
    clean_f(client,{"label": KF_LABEL_SERVICE})

    # Create the zookeeper instances.
    #setup_zookeeper(client)


    # Create the kafka instances.
    setup_kafka(client)
    
