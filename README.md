# Autonomous-PiCar
A Raspberry Pi 3 with SunFounder PiCar-V as a body and numerous ultrasonic sensors to build a model autonomous car from scratch.

###Hi there.

I'm Viktor Cef Inselberg and this is my Senior Design Project (Senior thesis) for my Computer Engineering BSc degree in MEF University. Firstly, I have designed a model car hardware that is capable of:

 - perceiving its surroundings with multiple sensors
 - receiving and correctly executing orders on its movement
 - performing complex calculations on the road
 
It is obviously very important that these elements are in communication with one another as they will form the decision-making cognition of the agent. 

I had minor knowledge on machine learning and robotics at the beginning of the project, but this component has become part of the premise because I wanted to see if anyone with programming knowledge and access to basic necessary tools could accomplish a personally conceived artificial intelligence venture.

This project was a tedious process of trial-and-error and required some cooperation of people studying on different disciplines and many iterations of a Q-Learning algorithm that was tailored for its conditions, but it was an overall success.

I produced a functional model car skeleton with a mounted Raspberry Pi 3 and six HC-SR04 ultrasound sensors, running on a reinforcement learning algorithm that evaluates its current state to formulate the next optimal course of action. I tested with different hyper-parameters (on randomness, learning and other variables depicting coefficients), alternated between them and plotted performance graphs to observe and decide on the most optimized settings, concluding my thesis. 
