./bin/bzrflag --world=maps/none.bzw --red-port=50100 --red-tanks=1 --green-port=50101 --green-tanks=1 --default-posnoise=5 $@ &
sleep 2
python bots/kalman_agent.py localhost 50100 &
python bots/wild_agent.py localhost 50101 &