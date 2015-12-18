# 0.0 Pepper Robot only Steps (Not needed for Nao)
The Pepper robot, as of writing this document, does not allow for root access to its filesystem. That means all code must be installed in the user space. To install python dependencies in the user space the below steps need to do be completed.

Add the below to your ~/.*rc (then re-source your termainal)

`PATH=$PATH:~/.local/bin`

`easy_install --user pip`

Then you can install any pip libraries using 

`pip install --user <package_name>`

# 0.1 Prerequisites to Complete on your Aldebaran Robot
[See Prerequisites.md](Prerequisites.md)

#1.0 To install new front end SDK

1) Upload alwatson.py, watson.py, and config.ini to the robot file system. Place the files where anywhere on the file system.

`scp watson.py nao@ROBOT_IP.local:~/`

`scp config.ini nao@ROBOT_IP.local:~/`

`scp alwatson.py nao@ROBOT_IP.local:~/`


2) On the Nao/Pepper robot you need to edit ~/preferences/autoload.ini. This will allow the system to start up with the SDK enabled.

The file ~/preferences/autoload.ini will look something like this:


		# autoload.ini
		
		# Use this file to list the cross-compiled modules that you wish to load.
		
		# You must specify the full path to the module, python module or program.

		[user]	
		#the/full/path/to/your/liblibraryname.so  # load liblibraryname.so

		[python]
		#the/full/path/to/your/python_module.py   # load python_module.py
		/home/nao/alwatson.py
			
		[program]
		#the/full/path/to/your/program            # load program

2) Licence file
A licence file can be generated using a QR code. This file will generated at ~/.watson/licence.wat and will take the format of:

`{"ROBOT_KEY":"ROBOT_KEY_FROM_EMAIL","ROBOT_GATEWAY_URL":"ROBOT_URL_FROM_EMAIL"}`

This licence can be manually added or through using the SDK to hook into the robot's vision sensor data. This is currently can be done using the `$REPO_ROOT/robot_gateway_client/robotics_platforms/aldebaran/choregraphe/QR reader`. If the user is manually adding the licence file the ROBOT_KEY_FROM_EMAIL and the ROBOT_URL_FROM_EMAIL can be found in the registration email from robot gateway apps admin page.

4) Restart robot


#2.0 Notes:
To develop on the Front End SDK

1. Comment out the path to alwatson.py in autoload.ini
2. Restart the robot
3. Run `python alwatson.py` in the terminal on the robot
4. Run any behavior you want to test in Choregraphe
5. Watson.py logs will show up in terminal window where you ran python.py
6. To redeploy changes, just ctrl+c, save alwatson.py on the robot and run it again





