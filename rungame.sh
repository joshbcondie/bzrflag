./bin/bzrflag --world=maps/grid.bzw --red-port=50100 --default-true-positive=.7 --default-true-negative=.65 --occgrid-width=100 --no-report-obstacles $@ &
sleep 2
python bots/grid_filter_agent.py localhost 50100 &