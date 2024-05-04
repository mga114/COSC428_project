# Wireframe Design to HTML and CSS using Computer Vision

This is a tool to easily convert a screenshot of a website wireframe design into a webpage using HTML and Tailwind CSS.

### Running
To run this tool, ensure python3 and tesseract OCR are installed on your system. A virtual environment can then be created from the `requirements.txt` file provided.

Some input images are provided in the `inputs` directory for ease of use, and the outputs for these are in the `results` directory, however feel free to add your own. 

To run this program, run `cv_object_detector.py`, and change the input image on line 140 to whatever your desired input is.

The output will be placed into `index.html` in the root directory, and can be opened in the browser to view the output.

### Requirements
- python3
- opencv-contrib-python
- opencv-python
- pytesseract (and tesseract installed locally)
- numpy

### Notes
Feel free to extend this tool, would be super cool to see this working with a deep learning based solution, or modify the output styles by changing `css_converter.py` to be in another CSS framework, or port over to a completely different frontend framework, like JavaFX!

When creating your own wireframe designs for this, for any images that you want in your HTML, create a shape, and put the text "img" inside it. This will automatically convert it to an image. Buttons are similar, however with the interior text of "Button"