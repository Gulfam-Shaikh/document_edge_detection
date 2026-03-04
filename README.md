# Document Border Detection API

A robust REST API built with Python that detects the outer boundaries of a document within an image and draws a green border around it. It is designed to be highly accurate and resilient against complex internal document elements, such as QR codes, text blocks, and images, by focusing purely on the outer contrast between the document and its background.

## 🛠️ Technologies Used

* **Python 3.x**: The core programming language.
* **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
* **OpenCV (`opencv-python`)**: An open-source computer vision and machine learning software library used for all image processing algorithms.
* **NumPy**: Used for highly optimized array operations (image matrices).
* **Uvicorn**: An ASGI web server implementation for Python to run the FastAPI application.
* **python-multipart**: Required by FastAPI to handle `multipart/form-data` (file uploads).

## 🧠 How It Works

The core logic resides in `document_detector.py`. When an image is sent to the API, the following pipeline is executed:

1. **Decoding & Resizing**: The uploaded byte stream is converted into an OpenCV image matrix. It is resized to a standard height (500px) to drastically speed up processing while maintaining aspect ratio.
2. **Grayscale & Blurring**: The image is converted to grayscale to remove color complexity, and slightly blurred (Gaussian Blur) to remove high-frequency noise.
3. **Contrast Mapping (Otsu's Thresholding)**: The algorithm maps the contrast of the document against the background by creating a stark binary (black & white) mask. 
4. **Morphological Operations (Closing)**: *This is the key to ignoring QR codes!* We apply a morphological "close" operation using a rectangular kernel. This merges dense inner details (like text and QR codes) into solid blocks, effectively hiding their internal edges from the detector.
5. **Edge & Contour Detection**: After smoothing out the inner details, Canny Edge Detection highlights the prominent outer edges. We then search strictly for **External Contours** (`cv2.RETR_EXTERNAL`), guaranteeing we don't accidentally detect a square QR code inside the page.
6. **Shape Approximation**: We sort the found contours by area, pick the largest one, and check if it has 4 points (a standard document).
   * *Fallback:* If the document is warped or cut off and doesn't perfect form 4 corners, the algorithm intelligently falls back to drawing a rectangular bounding box around the largest continuous shape.
7. **Drawing & Encoding**: The boundary is scaled back up to the original image dimensions, drawn in green `(0, 255, 0)`, re-encoded to JPEG bytes, and sent back as a direct HTTP response.

## 🚀 How to Build & Run

### Prerequisites
Make sure you have Python 3.7+ installed on your system.

### 1. Install Dependencies
Open your terminal in the project directory and install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Start the Server
Run the FastAPI application. You can simply run the main file:
```bash
python main.py
```
*The server will start locally at `http://localhost:8000`.*

## 🧪 How to Test

### Method 1: Interactive Swagger UI (Recommended)
FastAPI automatically generates a beautiful interactive testing interface.
1. Start the server.
2. Open your web browser and go to: **http://localhost:8000/docs**
3. Click on the `POST /detect-border/` endpoint to expand it.
4. Click the **"Try it out"** button.
5. Upload an image file containing a document (even one with a QR code).
6. Click **"Execute"**. 
7. Scroll down to the response window; you will be able to click directly on the "Download file" link to see your successfully processed image with the green border!

### Method 2: Using cURL
You can also test the API via the command line:
```bash
curl -X 'POST' \
  'http://localhost:8000/detect-border/' \
  -H 'accept: image/jpeg' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path_to_your_image.jpg' \
  --output result.jpg
```
*This will send the image and save the bordered output locally as `result.jpg`.*
