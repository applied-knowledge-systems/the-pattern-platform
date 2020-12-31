rconn=None 

def connecttoRedis():
    import redis 
    redis_client=redis.Redis(host='127.0.0.1',port=9001,charset="utf-8", decode_responses=True)
    return redis_client

def OnRegisteredConnect():
    global rconn
    rconn=connecttoRedis()
    return rconn

def process_item(record):
    global rconn
    if not rconn:
        rconn=connecttoRedis()
    source=record['value']['source']
    destination=record['value']['destination']
    log(f"Edges to Graph got source {source} and {destination}")
    response=rconn.execute_command("GRAPH.QUERY", "cord19medical","""MERGE (source: entity { id: '%s' , label:'entity'}) 
         ON CREATE SET source.rank=1
         ON MATCH SET source.rank=(source.rank+1)
         MERGE (destination: entity { id: '%s', label:'entity' })
         ON CREATE SET destination.rank=1
         ON MATCH SET destination.rank=(destination.rank+1)
         MERGE (source)-[r:related]->(destination)
         ON CREATE SET r.rank=1
         ON MATCH SET r.rank=(r.rank+1)
         ON CREATE SET r.rank=1
         ON MATCH SET r.rank=(r.rank+1)""" % (source,destination))
    log('Edges to graph finished with response '+" ".join(map(str,response)))


bg = GearsBuilder('StreamReader')
bg.foreach(process_item)
bg.register('edges_matched*', batch=1, mode="async_local",onRegistered=OnRegisteredConnect, onFailedPolicy='continue', trimStream=True)
