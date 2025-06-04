import Leap, sys, time

class SampleListener(Leap.Listener):
    def on_connect(self, controller):
        print("Leap Motion device connected.")
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Leap Motion device disconnected.")

    def on_exit(self, controller):
        print("Exited.")

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        if not frame.hands.is_empty:
            print("Hands detected: ", len(frame.hands))
            for hand in frame.hands:
                handType = "Left hand" if hand.is_left else "Right hand"
                print(handType + ", id %d, position: %s" % (
                    hand.id, hand.palm_position))
                # You can add more details about the gestures and tools here.

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print("Press Enter to quit...")
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()
