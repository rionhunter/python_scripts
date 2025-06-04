#!/bin/bash

# Set the index of the monitor you want to toggle
# 0 for the first monitor, 1 for the second, etc.
MONITOR_INDEX=2

# Define your preferred landscape and portrait modes
LANDSCAPE_MODE="normal"
PORTRAIT_MODE="right"

# Path to the file that keeps track of the current rotation state
STATE_FILE="/tmp/monitor_${MONITOR_INDEX}_rotation_state"

# Get the name of the monitor at the specified index
MONITOR_NAME=$(xrandr --query | grep " connected" | awk '{print $1}' | sed -n "$((MONITOR_INDEX+1))p")

# Check if the state file exists and read the current state
if [ -f "$STATE_FILE" ]; then
    CURRENT_STATE=$(cat "$STATE_FILE")
else
    CURRENT_STATE=$LANDSCAPE_MODE
    echo $LANDSCAPE_MODE > "$STATE_FILE"
fi

# Toggle between landscape and portrait mode
if [ "$CURRENT_STATE" = "$LANDSCAPE_MODE" ]; then
    xrandr --output $MONITOR_NAME --rotate $PORTRAIT_MODE
    echo $PORTRAIT_MODE > "$STATE_FILE"
else
    xrandr --output $MONITOR_NAME --rotate $LANDSCAPE_MODE
    echo $LANDSCAPE_MODE > "$STATE_FILE"
fi
