cmake_minimum_required(VERSION 3.0.2)
project(ros_stt)

## Compile as C++11 if you later add C++ nodes
# add_compile_options(-std=c++11)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_generation
)

################################################
## Declare ROS messages, services and actions ##
################################################

add_message_files(
  FILES
  speech_recognition.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

###################################
## catkin specific configuration ##
###################################
catkin_package(
  CATKIN_DEPENDS rospy std_msgs message_runtime
  # INCLUDE_DIRS include
  # LIBRARIES ros_stt
)

###########
## Build ##
###########

include_directories(
  ${catkin_INCLUDE_DIRS}
)

## (Optional) If you have Python scripts in scripts/, install them:
# catkin_install_python(
#   PROGRAMS
#     scripts/vosk_sr_verbose.py
#     scripts/mic_toggle_key.py
#   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

