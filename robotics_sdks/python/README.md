# 1.0 Installing the Python SDK
1) Add the watson.py and the config.ini to a python path on your on your computer. Below you can see two .*rc commands that accomplish this:

`export PATH_TO_IBM_ROBOT_SDK=$REPO_ROOT/robot_gateway_client/robotics_sdks/python`

`export PYTHONPATH=${PYTHONPATH}:${PATH_TO_IBM_ROBOT_SDK}:/usr/local/pynaoqi-python2.7-2.1.2.17-mac64`

# 2.0 Generating and adding a Licence file
A licence file can be generated using a QR code. This file will generated at ~/.watson/licence.wat and will take the format of:

`{"ROBOT_KEY":"ROBOT_KEY_FROM_EMAIL","ROBOT_GATEWAY_URL":"ROBOT_URL_FROM_EMAIL"}`

This licence can also be manually added or through and platform dependent SDK hook into the robot's vision sensor data. For Aldebaran robots this can be done using

`$REPO_ROOT/robot_gateway_client/robotics_platforms/aldebaran/choregraphe/QR reader`

If the user is manually adding the licence file the ROBOT_KEY_FROM_EMAIL and the ROBOT_URL_FROM_EMAIL can be found in the registration email from the `robot_gateway_core` admin page.

# 3.0 Making a Test Call
You now should be able to use watson calls from anywhere in your computer now. This can be done by 
```python
import watson
w = watson.Watson()
w.translate( languageFrom='english', languageTo='spanish', 'So long and thanks for all the fish')
```