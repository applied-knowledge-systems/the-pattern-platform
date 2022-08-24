rconn=None

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

def sync_users(record):
    global rconn
    if not rconn:
        rconn=connecttoRedisEnterise()

    log(str(record['key']))
    log(str(record['value']))
        #     redis_client.hset("user_details:%s" % user_id,mapping={
        # 'access_token': access_token,
        # 'email': user_email,
        # 'id': user_id,
        # 'user_login': user_login,
        # 'graphql': response_graphql_data,
    rconn.hset(record['key'],mapping=record['value'])

gb = GB()
gb.foreach(sync_users)
gb.count()
gb.run('user_details:*')