# VisNav  
Visual Navigation for ArduPilot  
  
## Preqs  
* Mavproxy  
* DroneKit  
  
## Setup 
* Navigate to your home directory:  
	`$ cd`  
  
* Download my fork of ardupilot:  
	`$ git clone https://github.com/djnugent/ardupilot`  
  
*  Download visnav:  
	`$ git clone https://github.com/djnugent/visnav`  
  
*  Download the most recent version of pymavlink:  
	`$ git clone https://github.com/mavlink/mavlink`  
  
*  Uninstall any previous versions of pymavlink:  
	`$ sudo pip uninstall pymavlink`  
  
*  Navigate into pymavlink directory:  
	`$ cd /mavlink/pymavlink`  
  
*  Install pymavlink:  
	`$ sudo python install setup.py`  
  
*  Add sim_vehicle.sh and PrecisionLand to your path:  
	`$ sudo nano ~/.bashrc`  
	ADD THE FOLLOWING TO THE END OF THE FILE: <br />
		`export PATH=$PATH:$HOME/ardupilot/Tools/autotest`<br />
		`export PYTHONPATH=$PYTHONPATH:$HOME/visnav`<br />
		*Use ctrl-x to exit and save the file*  
  
*  Re-run .bashrc / Reload PATH variables:  
	`$ . ~/.bashrc`  

*  Have Dronekit load on startup:  
	`$ echo "module load droneapi.module.api" >> ~/.mavinit.scr`   

*  Navigate to ardupilot/ArduCopter:  
	`$ cd /ardupilot/ArduCopter`  
  
*  Intialize SITL:  
	`$ sim_vehicle.sh -w`  
  
*  Disable prearm checks:  
	`$ param set ARMING_CHECK 0`  
  
*  Kill SITL:  
	*Press ctrl-c*  
  
  
  
## Run Precision land with SITL: 
*  Navigate to ardupilot/ArduCopter:  
	`$ cd /ardupilot/ArduCopter`  
  
*  Start SITL:  
	`$ sim_vehicle.sh --console --map`  
  
*  Arm vehicle:  
	`MAV> arm throttle`  
  
*  Switch to guided mode:  
	`MAV> mode guided`  
  
*  Takeoff:  
	`MAV> takeoff 20`  
  
*  Start PrecsionLand:  
	`MAV> api start /home/<your_username>/visnav/PrecisionLand.py`  
  
*  Kill SITL:  
	*Press ctrl-c*
  


## See my progress  
*  http://diydrones.com/profiles/blogs/precision-land-arducopter-demo  
*  http://diydrones.com/profiles/blogs/precision-land-arducopter
  


## Related projects
*  http://irlock.com/