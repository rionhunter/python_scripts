import cv2

def add_effects(video_path):
    try:
        # Load the video
        video = cv2.VideoCapture(video_path)

        # Check if the video is successfully loaded
        if not video.isOpened():
            raise Exception("Failed to load video")

        # Apply effects to each frame of the video
        while True:
            ret, frame = video.read()

            # Check if the frame is successfully read
            if not ret:
                break

            # Apply desired effects to the frame
            # ...
            # Code to apply effects goes here

            # Display the frame with effects
            cv2.imshow("Video", frame)

            # Check if the user wants to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture and close all windows
        video.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error: {str(e)}")