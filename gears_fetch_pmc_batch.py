rconn=None

def connecttoRedis():
    import redis 
    redis_client=redis.Redis(host='redisgraph',port=6379,charset="utf-8", decode_responses=True)
    return redis_client

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def fetch_article(record):
    import xmltodict 
    import requests
    
    global rconn
    if not rconn:
        rconn=connecttoRedis()

    
    key_prefix='pmc:article:{%s}:'%hashtag()
    article_key=remove_prefix(record['key'],key_prefix)
    log(f"Processing article {article_key}")
    processed=execute('SISMEMBER','fetched_articles{%s}' % hashtag(),article_key)
    if not processed:
        fetch_abstract=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={article_key}&retmode=xml&rettype=abstract'
        log(fetch_abstract)
        log(f'article_id:{article_key}')
        my_pmc_dict=xmltodict.parse(requests.get(fetch_abstract).content)
        if '#text' in my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']:
            title=my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']['#text']
        else:
            title=my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']
        log(f'article_id:{article_key}:{title}')

        pub_date=my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['pub-date']
        (year,month,day)=(2022,2,1)
        if isinstance(pub_date, list):
            for each_t in pub_date:
                if 'year' in each_t:
                    year = each_t['year']
                if 'month' in each_t:
                    month=each_t['month']
                if 'day' in each_t:
                    day = each_t['day']
        else:
            year=pub_date['year']

        rconn.hset(f"article_id:{article_key}",mapping={'title': title})

        rconn.hset(f"article_id:{article_key}",mapping={'year':year})
        rconn.hset(f"article_id:{article_key}",mapping={'month':month})
        rconn.hset(f"article_id:{article_key}",mapping={'day':day})

        article_body=[]
        abstract_raw=my_pmc_dict['pmc-articleset']['article']['front']['article-meta']['abstract']
        if 'sec' in abstract_raw and isinstance(abstract_raw['sec'],list):
            for each_p in abstract_raw['sec']:
                if 'p' in each_p:
                    if '#text' in each_p['p']:
                        article_body.append(each_p['p']['#text'])
                    else:
                        article_body.append(each_p['p'])
                else:
                    article_body.append(each_p)
        else:
            if 'p' in abstract_raw:
                if '#text'in abstract_raw['p']:
                    article_body.append(abstract_raw['p']['#text'])
                else:
                    article_body.append(abstract_raw['p'])

        article_text=" ".join(article_body)
        log(f'paragraphs:PMC{article_key}:{article_text}')
        full_key='paragraphs:%s:{%s}' % (article_key,hashtag())
        log(f'Full key {full_key}')
        execute('SET',full_key,article_text)
        execute('SADD','fetched_articles{%s}' % hashtag(),article_key)
    else:
        log(f"Article {article_key} already processed")


gb = GB('KeysReader')
gb.foreach(fetch_article)
gb.count()
gb.run('pmc:article:*',mode="async_local")