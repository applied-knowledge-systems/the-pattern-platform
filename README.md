# the-pattern-platform

This is a NLP pipeline based on RedisGears, this is evolution of  [Cord19Project](https://github.com/AlexMikhalev/cord19redisknowledgegraph)

The purpose of this part is NLP pipeline to turn text into knowledge graph ("it's about things, not strings") by matching text (terms) to Medical Methathesaurus UMLS (concepts).  As input this pipeline is using CORD19 competition Kaggle dataset - medical articles.



# Architecture 

Uses RedisGears using KeyReader, StreamReader

NLP Steps: 

* Identify language [LangDetect](./lang_detect_gears_paragraphs.py) (It should be English)
* Split paragraphs into sentences using Spacy [spacy_sentences_streams.py](spacy_sentences_streams.py)
  * It can be done differently, but the point was to use large NLP library for processing
* Spellcheck sentences using [symspell_sentences_streamed.py](symspell_sentences_streamed.py) 
* Match terms from sentences to UMLS concepts using pre-build Aho-Corasick Automata [sentences_matcher_streamed.py](sentences_matcher_streamed.py)
  * To build you own use aho_corasick_create_direct.py 
    * You need to download and unpack umls-2019AB-metathesaurus.zip 
* Populate RedisGraph [edges_to_graph_streamed.py](edges_to_graph_streamed.py)  from nodes (concepts) and edges (relationship between concepts, assumption is that if two concepts in the same sentence they are related). RedisGraph is separate instance listening on 9001. 



# Quickstart

To run locally:  

1. Compile RedisGears and Redis then use [conf/launch_cluster.sh](conf/launch_cluster.sh) to launch gears cluster, amend paths as needed 

2. Start RedisGraph on port 9001 (or amend ports in conf/database.ini and in edges_to_graph_streamed.py)

3. Install gears-cli (pip install -r requirements.txt) and run sh cluster_pipeline_streams.sh to register functions 

4. Populate cluster with sample of articles python RedisIntakeRedisClusterSample.py (modify STOPPER constant to increase size)

   1. Give a cluster kick using [lang_detect_gears_paragraphs_force.py](lang_detect_gears_paragraphs_force.py) if logs are not showing a lot of activity. Actual command will look like `gears-cli run --host 127.0.0.1 --port 30001 lang_detect_gears_paragraphs_force.py --requirements requirements_gears_lang.txt`

5. Validate RedisGraph is populated with `GRAPH.QUERY cord19medical "MATCH (n:entity) RETURN count(n) as entity_count"`

   

Alternatively, use Docker to launch RedisGears/RedisGraph, but pass commands from launch_cluster.sh via redis-cli -c 

If you want to create you own NLP processing step lang_detect_gears_paragraphs_force.py is simplest example of KeyReader in batch mode, start with batch and then create a registration for events. StreamsReaders is probably closer to production, but pain in the back to debug. 



# TODO

It's not ideal, most parts are hard coded, but I hope it's useful enough for NLP data scientists. Overall architecture is still as in [original](https://github.com/AlexMikhalev/cord19redisknowledgegraph)  project.

- [ ] Update the-pattern overall repository
- [ ] Publish API server repository
- [ ] Publish UI demo
- [ ] Publish demo BERT based QA
- [ ] Publish demo BERT based Summary