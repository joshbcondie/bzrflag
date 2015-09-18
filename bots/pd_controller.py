####################################################
# Set a target position in the world (vector y)    #
# and have a robot track this position (vector x)  #
# using a PD controller.  Very simple physics      #
# are used.                                        #
####################################################

# Create a vector of times for the simulation, set delta t, 
# and store the length of the time vector.
t=[0:.01:20];dt=t(2)-t(1);
N=length(t);

# This is stuff that I used to teach the class, but isn't critical
# for your use.  The only important thing is that it sets the target
# value to y=1 for all time.  A cool experiment is to change the
# 0.0 multiplier in front of the cos to 1.0, and watch how the PD
# controller tracks.
y=zeros(1,N);
i=find(t==1);
y(i:N)= y(i:N)+1+0.0*cos(t(i:N)/5*2*pi);
#y=y+0.2*randn(1,N)

# Plot the target value and turn on some gridlines to help make
# the plot clear.
set(plot(t,y),'linewidth',5);
#axis([0,20,-.1,1.3]);
grid on;

# Define a vector of robot positions.  Initialize to zero,
# and then change as the simulation progresses.
x=zeros(1,N);

# Set initial robot velocity to zero, set robot mass to 
# 4.25 kg, and set initial error to zero.
v=0;m=4.25;e0=0;

# Define proportional and derivative constant
Kp=0.1;Kd=0*4.5;  #(Good response Kp=0.1,Kd=0.5)

# For N-2 steps of a simulation
for (i=2:N-1)

    e=y(i)-x(i); # Measure the difference between target and robot; error = e.
    #fprintf(1,'e=#.2f\n',e);
    de = (e-e0)/dt;e0=e;  # Measure how the error changes over time \dot{e}
    F=Kp*e + Kd*de;   # Set the force using the PD controller
    x(i+1) = x(i) + v * dt + 1/2*dt^2/m*F;  # Simulate the position changing 

    v=v+dt/m*F;   # Simulate the velocity changing
end;

 # Plot the robot's position over time.  Plot it on the same plot
# as the target's position so that you can compare.
hold on;
set(plot(t,x,'r--'),'linewidth',3);
hold off;