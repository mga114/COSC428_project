# Import required packages
import cv2
import pytesseract as tess
import numpy as np
import object_converter as oc
import css_converter as css

# This determines the maximum number of pixels between characters before classified as a space character
TEXT_HORIZONTAL_PIXEL_THRESHOLD = 10
# (percent) Maximum distance between shapes to be classified as equivalent shapes
SHAPE_EQUIVALENCE_THRESHOLD = 0.4
# Minimum shape size, any with an area smaller than this will be treated as noise and discarded
SHAPE_MINIMUM_SIZE_THRESHOLD = 20

"""
Handy class for managing the text. Because this solution only identifies individual characters,
this class is used for initially storing each character and then updates with characters that 
belong to this string, while updating the bounding box at the same time
"""
class Text:
    def __init__(self, data, height, scale=1):
        self.text = data[0]
        self.x = int(data[1]) // scale
        self.y = (height - int(data[4])) // scale  # Subtract from height for correct y-coordinate
        self.w = (int(data[3]) - int(data[1])) // scale
        self.h = (int(data[4]) - int(data[2])) // scale

    # add a character to this string. This will also update the bounding box
    def add_char(self, char):
        if type(char) != Text:
            raise Exception("Invalid type")
        # check if char has a space character before the actual character
        space_threshold = 4.601
        if abs(self.x + self.w - char.x) > (self.h + char.w) / space_threshold:
            char.text = " " + char.text
        self.text += char.text
        # update bounding box
        self.w = char.x + char.w - self.x
        self.y = min(self.y, char.y)
        self.h = max(self.y + self.h, char.y + char.h) - self.y
    
    # Checks if a given character could belong to this string
    def char_belong_to_text(self, char):
        return (abs((self.x + self.w) - char.x) < char.w + TEXT_HORIZONTAL_PIXEL_THRESHOLD
                and abs(self.y - char.y) < self.h)
    
    def __str__(self):
        return f"Text: {self.text}, x: {self.x}, y: {self.y}, w: {self.w}, h: {self.h}"

"""
Stores all shape information. This makes it easier to access properties, and also provides an equivalence function
"""
class Shape:
    def __init__(self, type, x, y, w, h):
        self.type = type
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __eq__ (self, other):
        return (abs(self.x - other.x) <= SHAPE_EQUIVALENCE_THRESHOLD * self.x 
                and abs(self.y - other.y) <= SHAPE_EQUIVALENCE_THRESHOLD * self.y 
                and abs(self.w - other.w) <= SHAPE_EQUIVALENCE_THRESHOLD * self.w 
                and abs(self.h - other.h) <= SHAPE_EQUIVALENCE_THRESHOLD * self.h)

# Uses Tesseract to detect each individual character in the input image. Returns a list of all valid characters
def extract_all_text_from_image (image):
    height = image.shape[0]
    # image grayscale conversion
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    boxes = tess.image_to_boxes(gray) # use tesseract to get the characters
    all_chars = []
    for line in boxes.splitlines():
        data = line.split(' ')
        all_chars.append(Text(data, height))
    
    # this is important as noise can be detected as a ~ character
    def is_erroneous_data(data):
        return data.text == "~"
    
    clean_chars = []
    for char in all_chars:
        if not is_erroneous_data(char):
            clean_chars.append(char)
    return clean_chars

# Handles sorting all of the individual characters into their corresponding strings.
# Returns the formatted strings
def format_extracted_chars (all_text):
    formatted_text = []
    for char in all_text:
        added = False
        for text in formatted_text:
            if text.char_belong_to_text(char):
                text.add_char(char)
                added = True
                break
        if not added:
            formatted_text.append(char)
    return formatted_text

# Removes all text from the image. This uses the bounding box of the detected strings as mask for removal.
# Returns the image without the text information
def remove_text_from_image(image, all_text):
    image_no_text = image.copy()
    for text in all_text:
        # get colour directly above the text
        fill_colour = image[text.y + text.h + 10, text.x]
        cv2.rectangle(image_no_text, (text.x, text.y), (text.x + text.w, text.y + text.h),
                       (int(fill_colour[0]), int(fill_colour[1]), int(fill_colour[2])), -1)
    return image_no_text

# Detects and sorts all shapes found in the (hopefully) textless image
# Returns a list of all unique shapes found in the image
def detect_shapes(img):
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (5, 5)) # blurring image
    r, thres = cv2.threshold(blur,220,255,cv2.THRESH_BINARY) # thresholds the image
    # gets all detected contours in the image
    contours, hierarchy = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    shapes = []
    for i, contour in enumerate(contours):
        epsilon = 0.01*cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv2.boundingRect(approx)  
        # ignore small shapes, likely an artifact from filtering
        if w >= SHAPE_MINIMUM_SIZE_THRESHOLD and h >= SHAPE_MINIMUM_SIZE_THRESHOLD and len(approx) == 4 :
            shapes.append(Shape("box" if len(approx) <= 4 else "circle", x, y, w, h))
    # remove equivalent shapes
    unique_shapes = []
    for shape in shapes:
        if all(shape != other_shape for other_shape in unique_shapes):
            unique_shapes.append(shape)
    return unique_shapes


if __name__ == "__main__":
    image = cv2.imread("inputs/demo7.png")
    all_chars = extract_all_text_from_image(image)
    all_text = format_extracted_chars(all_chars)
    image_no_text = remove_text_from_image(image, all_chars)
    all_shapes = detect_shapes(image_no_text)
    layout = oc.convert_layout_to_objects(all_shapes, all_text)
    css.generate_html(layout)