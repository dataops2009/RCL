import cv2
import numpy as np
import easyocr

class OCR_Request_Scores:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.reader = easyocr.Reader(['en'], gpu=False)

    def get_skew_angle(self) -> float:
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        edges = cv2.Canny(binary_image, 50, 150, apertureSize=3)
        kernel = np.ones((3,3), np.uint8)
        dilated = cv2.dilate(edges, kernel)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        largest_contour = max(contours, key=cv2.contourArea)

        moments = cv2.moments(largest_contour)
        if moments['mu02'] != 0:
            angle = 0.5 * np.arctan(2 * moments['mu11'] / (moments['mu02'] - moments['mu20']))
            angle = angle * (180/np.pi)
        else:
            angle = 0
        return angle

    def rotate_image(self, angle):
        (h, w) = self.image.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
        rotated = cv2.warpAffine(self.image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def select_corners(self, image):
        points = []

        def draw_circle(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
                points.append((x, y))

        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Image', image)
        cv2.setMouseCallback('Image', draw_circle)

        while len(points) < 4:
            cv2.waitKey(1)

        cv2.destroyAllWindows()
        return points

    def correct_perspective(self, image, points):
        src_pts = np.float32(points)
        width_a = np.linalg.norm(src_pts[0] - src_pts[1])
        width_b = np.linalg.norm(src_pts[2] - src_pts[3])
        max_width = max(int(width_a), int(width_b))

        height_a = np.linalg.norm(src_pts[1] - src_pts[2])
        height_b = np.linalg.norm(src_pts[3] - src_pts[0])
        max_height = max(int(height_a), int(height_b))

        dst_pts = np.float32([[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]])
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped_image = cv2.warpPerspective(image, M, (max_width, max_height))
        return warped_image

    def perform_ocr(self, image):
        return self.reader.readtext(image)

    def preprocess(self):
        angle = self.get_skew_angle()
        rotated_image = self.rotate_image(angle)
        selected_corners = self.select_corners(rotated_image)
        self.corrected_image = self.correct_perspective(rotated_image, selected_corners)
        self.save_image(self.corrected_image, 'corrected_image.jpg')
        self.save_image(self.image, 'original_image.jpg')
        print('Preprocessing Completed - saved as class.corrected_image')
    
    def save_image(self, image, path):
        cv2.imwrite(path, image)

    def show_image(self, image):
        cv2.imshow('Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def sharpen_image(self, image):
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened
    
    def invert_colour(self, image):
        inverted = cv2.bitwise_not(image)
        return inverted
    
    def grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray
    
    def denoise(self, image):
        denoised = cv2.fastNlMeansDenoising(image, h=10)
        return denoised
    
    def adaptive_threshold(self, image, blockSize=11, C=2, blur=False, blur_intensity=5, met_ops = False,  met_ops_size=1):
        gray = self.grayscale(image)

        if blur:
            gray = cv2.GaussianBlur(gray, (blur_intensity, blur_intensity), 0)

        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize, C)
    
        # Optional: Apply morphological operations
        if met_ops:
            kernel = np.ones((met_ops_size, met_ops_size), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        return thresh

    



