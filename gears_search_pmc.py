
async def search_cached_keymiss(record):
    val=record['key'].split('_')
    cache_key='search:article{%s}_%s' % (hashtag(), val[1])
    log("Search PMC called from keymiss")
    processed=execute('get',cache_key)
    if processed:
        log("Already done search with cache key "+str(cache_key))
        return processed
    res = await search_pmc(val)
    log("Result "+str(res))
    log("Cache key "+str(cache_key))
    execute('set',cache_key, res)
    override_reply(res)
    return res

async def search_pmc(record):
    import requests
    import json
    db = 'pmc'
    domain = 'https://www.ncbi.nlm.nih.gov/entrez/eutils'
    nresults = 60
    query = record[1]
    retmode='json'
    # FIXME: cache response for at least 2 hours
    # standard query
    queryLinkSearch = f'{domain}/esearch.fcgi?db={db}&retmax={nresults}&retmode={retmode}&term={query}'
    response = requests.get(queryLinkSearch)
    pubmedJson = response.json()

    results = []

    for paperId in pubmedJson["esearchresult"]["idlist"]:
        execute('set','pmc:article:{%s}:%s'% (hashtag(),paperId), 1)

    log("Called with "+ str(record))
    hash_tag="{%s}" % hashtag()
    log("Shard_id "+hash_tag)
    return 1

gb = GB('KeysReader')
gb.foreach(search_cached_keymiss)
gb.register(prefix='search:article*', commands=['get'], eventTypes=['keymiss'], mode="async_local")
