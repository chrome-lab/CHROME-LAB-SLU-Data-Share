#!/usr/bin/env bash
set -e

# =========================
# User config (EDIT THESE)
# =========================

# Quori ROS master IP (EDIT THIS)
QUORI_IP="10.23.145.172"

# Open 3rd terminal and run vision node? true OR false
VISION=false

# Enable joystick nodes inside quori_setup.launch?
JOYSTICK=false

# Workspace + paths
CATKIN_WS="$HOME/catkin_ws"
GROQ_DIR="$HOME/catkin_ws/src/ros_stt/GPT"

# GROQ
GROQ_API_KEY="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"
UVICORN_HOST="0.0.0.0"
UVICORN_PORT="8080"

# =========================
# Derived env vars
# =========================
ROS_MASTER_URI_VALUE="http://${QUORI_IP}:11311"

# Helper: open a terminal and keep it open
open_term () {
  local title="$1"
  local cmd="$2"
  gnome-terminal --title="$title" -- bash -lc "$cmd; echo; echo '[DONE] Terminal will stay open.'; exec bash"
}

# =========================
# Terminal 1: quori_setup (with joystick flag)
# =========================
open_term "Quori Setup" "
  export ROS_MASTER_URI='${ROS_MASTER_URI_VALUE}';
  echo '[Terminal 1] ROS_MASTER_URI='\"\$ROS_MASTER_URI\";
  cd '${CATKIN_WS}';
  # If needed, uncomment:
  # source /opt/ros/noetic/setup.bash
  # source '${CATKIN_WS}/devel/setup.bash'

  echo '[Terminal 1] Running: roslaunch quori_gui quori_setup.launch joystick:=${JOYSTICK}';
  roslaunch quori_gui quori_setup.launch joystick:=${JOYSTICK}
"

# =========================
# Terminal 2: Uvicorn (GROQ)
# =========================
open_term "GROQ Uvicorn" "
  export ROS_MASTER_URI='${ROS_MASTER_URI_VALUE}';
  echo '[Terminal 2] ROS_MASTER_URI='\"\$ROS_MASTER_URI\";
  cd '${GROQ_DIR}';
  export GROQ_API_KEY='${GROQ_API_KEY}';
  echo '[Terminal 2] GROQ_API_KEY set. Running uvicorn...';
  uvicorn app:app --host '${UVICORN_HOST}' --port '${UVICORN_PORT}'
"

# =========================
# Terminal 3: Vision node (optional)
# =========================
if [[ \"${VISION}\" == \"true\" ]]; then
  open_term "Quori Vision" "
    export ROS_MASTER_URI='${ROS_MASTER_URI_VALUE}';
    echo '[Terminal 3] ROS_MASTER_URI='\"\$ROS_MASTER_URI\";
    cd '${CATKIN_WS}';
    # If needed, uncomment:
    # source /opt/ros/noetic/setup.bash
    # source '${CATKIN_WS}/devel/setup.bash'

    echo '[Terminal 3] Running: rosrun quori_gui vision.py';
    rosrun quori_gui vision.py
  "
else
  echo \"[INFO] VISION=false -> skipping vision terminal.\"
fi

