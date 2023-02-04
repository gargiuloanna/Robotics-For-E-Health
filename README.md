# RoboticsProject

Code for the Robotics For E Health project, a.a. 2021/2022

GOAL: when the robot pronounces animal sounds, the patient imitates the vocal sounds after the
demonstration.
REALIZATION:
The robot is placed on the ground, in front of the patient in a predefined starting position. The objects of
interest, known a priori and provided for the project (cow, sheep, car, train, dog), are placed on the
ground in front of the robot in predefined positions. The robot knows a priori the position of each object
with respect to the initial position and the sound that must be reproduced "verbally" in correspondence
with each object. The robot moves towards the next object, stops at it and crouches (as in the figure). At
this point, as required by the procedure, it pronounces the name of the object and reproduce its sound
(the sound can be recorded).
Then, the robot waits for 5 seconds for the patient's reaction:
• If the patient reproduces the sound correctly, the robot gets up and moves on to the next object
in the sequence;
• Otherwise, it plays the sound again and waits for 5 seconds.
After 3 unsuccessful attempts, the activity is unsuccessful. Unanswered attempts add up across different
objects. At the end of the activity, if the result is positive, the robot pronounces "Very well".
