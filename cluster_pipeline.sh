gears-cli run --host 127.0.0.1 --port 30001 gears_pipeline_sentence_register.py --requirements requirements_gears_pipeline.txt
echo "NLP Pipeline registered."
gears-cli run --host 127.0.0.1 --port 30001 edges_to_graph_streamed.py --requirements requirements_gears_graph.txt
echo "edges_to_graph_streamed.py registered"
sleep 30 
echo "30 seconds for cluster to recover"
gears-cli run --host 127.0.0.1 --port 30001 sentences_matcher_gears.py --requirements requirements_gears_aho.txt
echo "sentences_matcher_streamed.py registered."


