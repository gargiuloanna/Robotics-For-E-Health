#!/bin/bash

cd Documents/GitHub/RoboticsProject
catkin clean
catkin build
catkin init
source devel/setup.bash
roslaunch project system.launch test:=0

