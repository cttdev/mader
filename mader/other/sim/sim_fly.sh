
#!/bin/bash

# this script creates multiple windows for fly and mader
# referred to fly script used for voxl setup, which is in /extras

# if deleting old .bag and .active in voxl and .txt on nuc
ifDELETE=$1
howMany=$2
snapsim_or_perfect=$3

# session name
SESSION=sim_mader
WINDOW=base_station

# creates the session with a name and renames the window name
cmd="new-session -d -s $SESSION -x- -y-; rename-window $WINDOW"
tmux -2 $cmd

# window number
w=1

#split tmux into 2x6
for i in {1..6}
do
	tmux split-window -h
	tmux select-layout -t $SESSION:$w.$i even-horizontal
	tmux select-pane -t $SESSION:$w.$i
done

for i in 1 3 5 7 9 11
do 
	tmux select-pane -t $SESSION:$w.$i
	tmux split-window -v
done

# for i in 0 2 4 6 8 10
# do
# 	tmux resize-pane -t $SESSION:$w.$i -y 300
# done

# wait for .bashrc to load
sleep 1

# send commands to each pane

# run mader hw_onboard and save termial data into txt files

if [[ $ifDELETE == 'true' ]]; then 
	tmux send-keys -t $SESSION:$w.1 "cd ~/Research/data/txt_files && rm *.txt" C-m
fi

sleep 1

# run mader hw_onboard and save termial data into txt files

tmux send-keys -t $SESSION:$w.3 "(roscd mader && git rev-parse HEAD && git diff --color && roslaunch mader onboard.launch veh:=SQ num:=02 x:=0 y:=3) 2>&1 | tee ~/Research/data/txt_files/SQ02_mader_$(date '+%Y_%m_%d_%H_%M_%S').txt" C-m
tmux send-keys -t $SESSION:$w.9 "(roscd mader && git rev-parse HEAD && git diff --color && roslaunch mader onboard.launch veh:=SQ num:=05 x:=0 y:=-3) 2>&1 | tee ~/Research/data/txt_files/SQ05_mader_$(date '+%Y_%m_%d_%H_%M_%S').txt" C-m

if [[ $howMany != 2 ]]; then
	tmux send-keys -t $SESSION:$w.1 "(roscd mader && git rev-parse HEAD && git diff --color && roslaunch mader onboard.launch veh:=SQ num:=01 x:=-3 y:=3) 2>&1 | tee ~/Research/data/txt_files/SQ01_mader_$(date '+%Y_%m_%d_%H_%M_%S').txt" C-m 
	tmux send-keys -t $SESSION:$w.5 "(roscd mader && git rev-parse HEAD && git diff --color && roslaunch mader onboard.launch veh:=SQ num:=03 x:=3 y:=3) 2>&1 | tee ~/Research/data/txt_files/SQ03_mader_$(date '+%Y_%m_%d_%H_%M_%S').txt" C-m
	tmux send-keys -t $SESSION:$w.7 "(roscd mader && git rev-parse HEAD && git diff --color && roslaunch mader onboard.launch veh:=SQ num:=04 x:=-3 y:=-3) 2>&1 | tee ~/Research/data/txt_files/SQ04_mader_$(date '+%Y_%m_%d_%H_%M_%S').txt" C-m
	tmux send-keys -t $SESSION:$w.11 "(roscd mader && git rev-parse HEAD && git diff --color && roslaunch mader onboard.launch veh:=SQ num:=06 x:=3 y:=-3) 2>&1 | tee ~/Research/data/txt_files/SQ06_mader_$(date '+%Y_%m_%d_%H_%M_%S').txt" C-m
fi

# snap sim or perfect tracker

if [[ $snapsim_or_perfect == "snap_sim" ]]; then
	tmux send-keys -t $SESSION:$w.4 "roslaunch snap_sim sim.launch veh:=SQ num:=02 x:=0 y:=3" C-m
	tmux send-keys -t $SESSION:$w.10 "roslaunch snap_sim sim.launch veh:=SQ num:=05 x:=0 y:=-3" C-m

	if [[ $howMany != 2 ]]; then
		tmux send-keys -t $SESSION:$w.2 "roslaunch snap_sim sim.launch veh:=SQ num:=01 x:=-3 y:=3" C-m
		tmux send-keys -t $SESSION:$w.6 "roslaunch snap_sim sim.launch veh:=SQ num:=03 x:=3 y:=3" C-m
		tmux send-keys -t $SESSION:$w.8 "roslaunch snap_sim sim.launch veh:=SQ num:=04 x:=-3 y:=-3" C-m
		tmux send-keys -t $SESSION:$w.12 "roslaunch snap_sim sim.launch veh:=SQ num:=06 x:=3 y:=-3" C-m
	fi

else
	tmux send-keys -t $SESSION:$w.4 "roslaunch mader perfect_tracker_and_sim.launch quad:=SQ02s x:=0 y:=3" C-m
	tmux send-keys -t $SESSION:$w.10 "roslaunch mader perfect_tracker_and_sim.launch quad:=SQ05s x:=0 y:=-3" C-m

	if [[ $howMany != 2 ]]; then
		tmux send-keys -t $SESSION:$w.2 "roslaunch mader perfect_tracker_and_sim.launch quad:=SQ01s x:=-3 y:=3" C-m
		tmux send-keys -t $SESSION:$w.6 "roslaunch mader perfect_tracker_and_sim.launch quad:=SQ03s x:=3 y:=3" C-m
		tmux send-keys -t $SESSION:$w.8 "roslaunch mader perfect_tracker_and_sim.launch quad:=SQ04s x:=-3 y:=-3" C-m
		tmux send-keys -t $SESSION:$w.12 "roslaunch mader perfect_tracker_and_sim.launch quad:=SQ06s x:=3 y:=-3" C-m
	fi
fi

# base station
tmux send-keys -t $SESSION:$w.13 "roslaunch mader base_station.launch" C-m

tmux -2 attach-session -t $SESSION