# Using the Robotics Gateway Client Code

The structure of top level folders are:

`$REPO_ROOT/robot_gateway_client/robotics_sdks`

The robotics_sdks folder includes libraries that allow you to call the robot_gateway_app on your local device/robot. Within this folder you will find various language specific SDKs. Right now python is fully supported and objective c code is under active development. More languages will be added in the future.

`$REPO_ROOT/robot_gateway_client/robotics_platforms`

Folders under robotics_platforms host code that is specific a robotics platform. This code is not necessary to get started with the SDK but depending on the platform it may help you integrate the SDK into the system. Right now Aldebaran is our primary supported device and we are working to get several other platforms integrated and using the SDK.

Please take a look at the README.md files that are in each of the nested directories. Generally you will want to check the `robotics_platforms` directory first and see if you platform is supported. If it is not please look directly at the `robotics_sdks`

