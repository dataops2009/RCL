import cv2
import numpy as np
import easyocr

class OCRProcessor:
    def __init__(self, image_data, language='en'):
        self.image_data = image_data
        self.image = cv2.imdecode(np.frombuffer(image_data, np.uint8), -1)
        self.reader = easyocr.Reader([language], gpu=False)

    def perform_ocr(self):
        # Convert the image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Perform OCR
        return self.reader.readtext(gray)

# Example usage
if __name__ == "__main__":
    # Example: Load an image file, call the OCR processor
    with open('path_to_image.jpg', 'rb') as image_file:
        image_data = image_file.read()

    ocr_processor = OCRProcessor(image_data)
    ocr_results = ocr_processor.perform_ocr()

    # Output the results
    for result in ocr_results:
        print(result)
