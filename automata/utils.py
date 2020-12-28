from common.utils import *

def loadAutomata():
    from urllib.request import urlopen
    import ahocorasick 
    import joblib
    Automata=joblib.load("./automata/automata_fresh.pkl")
    # try:
    #     Automata=joblib.load("./automata/automata_syns_filtered_direct.pkl")
    # except:
    #     Automata=joblib.load(urlopen("https://github.com/AlexMikhalev/cord19redisknowledgegraph/raw/master/automata/automata_syns.pkl.bz2"))
    
    log("Automata properties" + str(Automata.get_stats()))
    return Automata

def find_matches(sent_text, A):
    matched_ents = []
    for char_end, (eid, ent_text) in A.iter_long(sent_text):
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

Automata=loadAutomata()