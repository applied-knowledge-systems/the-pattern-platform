gears-cli run --host 127.0.0.1 --port 30001 gears_pipeline_sentence_register.py --requirements requirements_gears_pipeline.txt
echo "NLP Pipeline registered."
gears-cli run --host 127.0.0.1 --port 30001 edges_to_graph_streamed.py --requirements requirements_gears_graph.txt
echo "edges_to_graph_streamed.py registered"
echo "10 seconds for cluster to recover"
sleep 10
echo "Submit 25 articles into pipeline" 
python RedisIntakeRedisClusterSample.py --nsamples 25
sleep 10
echo "Kick off matching"
gears-cli run --host 127.0.0.1 --port 30001 sentences_matcher_gears.py --requirements requirements_gears_aho.txt
#FIXME: this script brings down cluster cluster gears-cli run --host 127.0.0.1 --port 30001 sentences_matcher_register.py --requirements requirements_gears_aho.txt
#echo "sentences_matcher_register.py registered."
#echo "30 seconds for cluster to recover"
#sleep 30 


