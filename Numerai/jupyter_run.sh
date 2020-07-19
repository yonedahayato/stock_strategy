nohup jupyter notebook --no-browser --ip=0.0.0.0 >> jupyter.log 2>&1 &
cat jupyter.log | tail
