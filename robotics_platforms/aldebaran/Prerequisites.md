# Installing Dependencies (Prerequisites) on the Robot
Communicating with Watson on your robot requires installing a few small things first. First, you must download the get-pip.py python script, and copy it over to the robot to run it. To do this, open up a terminal, cd and ls into the directory with the get-pip.py file, and type the commands:
```sh
scp get-pip.py <robot_username>@<robot_name>.local:~/
ssh <robot_username>@<robot_name>.local
```
This copies over the file and logs you into the robot. Next, install pip, the python package installer with:
```sh
python get-pip.py
```
When this finishes, install the ‘requests’ and ‘ws4py’ packages by running:
```sh
pip install requests
pip install ws4py
```

**Note**: on a pepper robot this would be
```sh
pip install --user requests
pip install --user ws4py
```
These will each take a few minutes to download. They are both required for the Watson Behavior to run correctly.
