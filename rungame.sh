./bin/bzrflag --world=maps/four_ls.bzw --red-port=50100 --default-true-positive=.97 --default-true-negative=.9 --occgrid-width=100 --no-report-obstacles $@ &
sleep 2
python bots/grid_filter_agent.py localhost 50100 &