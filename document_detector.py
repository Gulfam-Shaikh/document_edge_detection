import cv2
import numpy as np

def detect_document_border(image_bytes: bytes) -> bytes:
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Could not decode image")

    # Resize for better processing speed and accuracy
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = cv2.resize(image, (int(image.shape[1] * (500.0 / image.shape[0])), 500))

    # Convert to grayscale and blur
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    # Use thresholding to map the contrast (document vs background)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Apply morphological operations to close gaps and merge inner details (like QR codes)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Get structured edges from the modified image
    edged = cv2.Canny(morph, 75, 200)
    edged = cv2.dilate(edged, kernel, iterations=1)

    # Find ONLY external contours to completely ignore anything inside the document (like a QR code)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort by area to find the largest shape (the document)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    document_contour = None

    for c in contours:
        # Only look at reasonably sized contours
        if cv2.contourArea(c) < 1000:
            continue
            
        # Approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        # If it has 4 points, assume it's the document
        if len(approx) == 4:
            document_contour = approx
            break
            
    # Fallback: if we didn't find a perfect 4-point shape, just use the bounding box of the largest contour
    if document_contour is None and len(contours) > 0:
        rect = cv2.minAreaRect(contours[0])
        box = cv2.boxPoints(rect)
        document_contour = np.intp(box)

    # Scale the contour back to original size and draw it
    if document_contour is not None:
        cv2.drawContours(orig, [np.int32(document_contour * ratio)], -1, (0, 255, 0), 3)

    # Encode the modified image back to bytes
    success, encoded_image = cv2.imencode('.jpg', orig)
    if not success:
        raise ValueError("Could not encode image")

    return encoded_image.tobytes()
