import cv2

# Create a VideoCapture object
cap = cv2.VideoCapture(0)  # 0 corresponds to the first available webcam

# Check if the webcam is successfully opened
if not cap.isOpened():
    print("Failed to open the webcam")
    exit()

# Read and display frames from the webcam
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if the frame is successfully captured
    if not ret:
        print("Failed to capture frame")
        break

    # Display the resulting frame
    cv2.imshow('Webcam', frame)

    # Check for the 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()