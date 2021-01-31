Automata=None 

rconn=None 
def enable_debug():
    debug=execute('GET','debug{%s}'% hashtag())
    if debug=='1':
        debug=True
    else:
        debug=False
    return debug

def connecttoRedis():
    import redis 
    redis_client=redis.Redis(host='redisgraph',port=6379,charset="utf-8", decode_responses=True)
    return redis_client


def loadAutomata():
    from urllib.request import urlopen
    import ahocorasick 
    import joblib
    
    try:
        Automata=joblib.load("./automata/automata_fresh.pkl")
    except:
        Automata=joblib.load(urlopen("https://github.com/AlexMikhalev/cord19redisknowledgegraph/raw/master/automata/automata_syns.pkl.bz2"))
    
    log("Automata properties " + str(Automata.get_stats()))
    return Automata

def find_matches(sent_text, A):
    matched_ents = []
    for char_end, (eid, ent_text) in A.iter(sent_text):
        char_start = char_end - len(ent_text)
        matched_ents.append((eid, ent_text, char_start, char_end))
    # remove shorter subsumed matches
    longest_matched_ents = []
    for matched_ent in sorted(matched_ents, key=lambda x: len(x[1]), reverse=True):
        longest_match_exists = False
        char_start, char_end = matched_ent[2], matched_ent[3]
        for _, _, ref_start, ref_end in longest_matched_ents:
            if ref_start <= char_start and ref_end >= char_end:
                longest_match_exists = True
                break
        if not longest_match_exists:
            # print("adding match to longest")
            longest_matched_ents.append(matched_ent)
    return [t for t in longest_matched_ents if len(t[1])>3] 



def OnRegisteredAutomata():
    global Automata
    Automata=loadAutomata()
    return Automata



def process_item(record):
    import httpimport
    with httpimport.remote_repo(['stop_words'], "https://raw.githubusercontent.com/explosion/spaCy/master/spacy/lang/en/"):
        import stop_words
    from stop_words import STOP_WORDS
    from string import punctuation
    import itertools
    import re
    debug=enable_debug()

    global Automata
    if not Automata:
        Automata=loadAutomata()

    global rconn
    if not rconn:
        rconn=connecttoRedis()

    
    shard_id=hashtag()
    article_id=record['key'].split(':')[1]
    if debug:
        log(f"Matcher received {record['key']} and my {shard_id}")
    for each_key in record['value']:
        sentence_key=record['key']+f':{each_key}'
        tokens=set(record['value'][each_key].split(' '))
        processed=execute('SISMEMBER','processed_docs_stage3{%s}' % shard_id,sentence_key)
        if not processed:
            if debug:
                log("Matcher: length of tokens " + str(len(tokens)))
            
            tokens.difference_update(set(punctuation))
            tokens.difference_update(STOP_WORDS) 
            matched_ents = find_matches(" ".join(tokens), Automata)
            if len(matched_ents)<1:
                if debug:
                    log("Error matching sentence "+sentence_key)
            else:
                if debug: 
                    log("Matcher: Matching sentence "+sentence_key)
                for pair in itertools.combinations(matched_ents, 2):
                    source_entity_id=pair[0][0]
                    destination_entity_id=pair[1][0]
                    label_source=pair[0][1]
                    label_destination=pair[1][1]
                    source_canonical_name=re.sub('[^A-Za-z0-9]+', ' ', str(label_source))
                    destination_canonical_name=re.sub('[^A-Za-z0-9]+', ' ', str(label_destination))
                    #TODO: this candidate for rgsync
                    # execute('XADD', 'nodes_matched_{%s}' % shard_id, '*','node_id',f'{source_entity_id}','node_name',f'{source_canonical_name}')
                    # execute('XADD', 'nodes_matched {%s}' % shard_id,'*','node_id',f'{destination_entity_id}','node_name',f'{destination_canonical_name}')
                    year=rconn.hget(f"article_id:{article_id}",'year')
                    if not year:
                        year='2021'
                    execute('XADD', 'edges_matched_{%s}' % shard_id, '*','source',f'{source_entity_id}','destination',f'{destination_entity_id}','source_name',source_canonical_name,'destination_name',destination_canonical_name,'rank',1,'year',year)

                    #FIXME: this breaks design pattern of NLP processing to support microservices pattern on front end
                    rconn.zincrby(f'edges_scored:{source_entity_id}:{destination_entity_id}',1, sentence_key)

            execute('SADD','processed_docs_stage3{%s}' % shard_id,sentence_key)
        else:
            if debug:
                log(f"Matcher Alteady processed {sentence_key}")



bg = GearsBuilder('KeysReader')
bg.foreach(process_item)
bg.count()
bg.register('sentence:*',  mode="async_local",onRegistered=OnRegisteredAutomata)
