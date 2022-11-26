FROM redislabs/redisai:edge-cpu-bionic AS builder 
FROM ghcr.io/applied-knowledge-systems/rgcluster@sha256:e3c807944e3ee550794f578c2ace3ea410adceab3dceb3dc9ba3f30d9f49ea83
# FROM ghcr.io/applied-knowledge-systems/rgcluster:edge
RUN apt-get update && apt-get install -y build-essential libgomp1
ENV REDIS_MODULES /usr/lib/redis/modules
ENV LD_LIBRARY_PATH $REDIS_MODULES

RUN mkdir -p $REDIS_MODULES/

COPY --from=builder /usr/lib/redis/modules/ $REDIS_MODULES/

COPY --from=builder /var/opt/redislabs/artifacts/ /var/opt/redislabs/artifacts

WORKDIR /cluster

CMD []
