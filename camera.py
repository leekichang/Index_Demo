import cv2

class Camera:
    def __init__(self, IMAGE_SIZE=(512,512)):
        # Create a VideoCapture object
        self.cap = cv2.VideoCapture(0)  # 0 corresponds to the first available webcam
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_SIZE[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_SIZE[1])
        # Check if the webcam is successfully opened
        if not self.cap.isOpened():
            print("Failed to open the webcam")
            
    def stream(self):
        # Read and display frames from the webcam
        while True:
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            # Check if the frame is successfully captured
            if not ret:
                print("Failed to capture frame")
                break
            # Display the resulting frame
            cv2.imshow('Webcam', frame)
            # Check for the 'q' key to quit
            k = cv2.waitKey(1)
            if  k == ord('c'):
                # self.capture(frame)
                self.frame = frame
        # Release the VideoCapture object and close all windows
        self.cap.release()
        cv2.destroyAllWindows()
    
    def capture(self, frame, file_name='test'):
        cv2.imwrite(f'{file_name}.png', frame)

if __name__ == '__main__':
    camera = Camera()
    camera.stream()