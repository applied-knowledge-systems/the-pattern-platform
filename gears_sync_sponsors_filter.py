rconn=None

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def connecttoRedisEnterise():
    import redis 
    import os 
    log(str(os.environ))
    # Get environment variables

    HOST = os.getenv('REDISENT_HOST')
    PASSWORD = os.getenv('REDISENT_PWD')
    PORT = os.getenv('REDISENT_PORT')

    redis_client=redis.Redis(host=HOST,port=PORT,charset="utf-8", password=PASSWORD, decode_responses=True)
    return redis_client

def filter_sponsors(record):
    org_name="applied-knowledge-systems"
    user_id = remove_prefix(record['key'],'user:')
    sponsor=execute('SISMEMBER',f'sponsors:{org_name}',user_id)
    return bool(sponsor==True)

def sync_sponsors(record):
    global rconn
    if not rconn:
        rconn=connecttoRedisEnterise()

    log(str(record['key']))
    values=execute('SMEMBERS',record['key'])
    log(str(values))
    for each_value in values:    
        rconn.sadd(record['key'],each_value)

gb = GB()
gb.filter(filter_sponsors)
gb.foreach(sync_sponsors)
gb.count()
gb.run('user:*')