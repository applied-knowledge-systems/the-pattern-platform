Automata=None 



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
    from spacy.lang.en.stop_words import STOP_WORDS
    from string import punctuation
    import itertools
    import re

    global Automata
    if not Automata:
        Automata=loadAutomata()

    sentence_key=":".join(record['value']['sentence_key'].split(':')[0:-1])
    shard_id=hashtag()
    log(f"Matcher received {sentence_key} and my {shard_id}")
    tokens=set(record['value']['content'].split(' '))
    log("Matcher: length of tokens " + str(len(tokens)))
    tokens.difference_update(STOP_WORDS)
    tokens.difference_update(set(punctuation)) 
    matched_ents = find_matches(" ".join(tokens), Automata)
    if len(matched_ents)<1:
        log("Error matching sentence "+sentence_key)
    else:
        log("Matcher: Matching sentence "+sentence_key)
        for pair in itertools.combinations(matched_ents, 2):
            source_entity_id=pair[0][0]
            destination_entity_id=pair[1][0]
            label_source=pair[0][1]
            label_destination=pair[1][1]
            source_canonical_name=re.sub('[^A-Za-z0-9]+', ' ', str(label_source))
            destination_canonical_name=re.sub('[^A-Za-z0-9]+', ' ', str(label_destination))
            execute('XADD', 'edges_matched_{%s}' % hashtag(), '*','source',f'{source_entity_id}','destination',f'{destination_entity_id}','rank',1)
            # log(f'Matcher HSETNX nodes:{source_entity_id} id {source_entity_id}')
            # execute('RPUSHX', 'edges_matched_{%s}' % hashtag(), f'edges_scored:{source_entity_id}:{destination_entity_id}'+":"+shard_id)
            # execute('HSETNX', f"nodes:{source_entity_id}",'id',source_entity_id)
            # execute('HSETNX', f'nodes:{source_entity_id}','name',source_canonical_name)
            # execute('HSETNX', f'nodes:{destination_entity_id}','id',destination_entity_id)
            # execute('HSETNX', f'nodes:{destination_entity_id}','name',destination_canonical_name)
            # execute('HINCRBY', f'nodes:{source_entity_id}' ,'rank',1)
            # execute('HINCRBY', f'nodes:{destination_entity_id}','rank',1)
            # log(f'Matcher Command ZINCRBY  edges_scored:{source_entity_id}:{destination_entity_id},1, {sentence_key}')
            execute('ZINCRBY', f'edges_scored:{source_entity_id}:{destination_entity_id}'+":"+shard_id,1, sentence_key)
            # execute('HINCRBY', f'edges:{source_entity_id}:{destination_entity_id}','rank',1)
            log(f'Matcher finished')
    # if value:
    #     execute('XADD', 'sentences_matched_{%s}' % hashtag(), '*', 'sentence_key', f"{sentence_key}",'content',f"{value}")
    #     log("Successfully spellchecked sentence "+str(sentence_key),level='notice')
    # else:
    #     execute('SADD','matcher_screw_ups{%s}' % hashtag(), sentence_key)


bg = GearsBuilder('StreamReader')
bg.foreach(process_item)
bg.register('sentence_to_tokenise*', batch=1, mode="async_local",onRegistered=OnRegisteredAutomata, onFailedPolicy='continue', trimStream=True)
