try:
    import cv2
    _cv2_available = True
except Exception:
    cv2 = None
    _cv2_available = False

import numpy as np
import base64
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_path
import os


def _fallback_detect_pipelines(image_path, visualize=False):
    """Fallback line detection using simple thresholding if OpenCV is unavailable.

    This is a very rough approximation and intended only to allow tests to run
    in minimal environments.
    """
    pil = Image.open(image_path).convert('L')
    arr = np.array(pil)
    # simple edge detection via gradient magnitude
    gy, gx = np.gradient(arr.astype(float))
    mag = np.hypot(gx, gy)
    thresh = mag.mean() + mag.std()
    edges = mag > thresh

    # naive Hough-like: scan rows for runs of edge pixels and create segments
    pipelines = []
    h, w = edges.shape
    for y in range(0, h, max(1, h // 20)):
        xs = np.where(edges[y])[0]
        if xs.size >= 2:
            pipelines.append({'source': [int(xs[0]), int(y)], 'destination': [int(xs[-1]), int(y)]})

    visual = None
    if visualize:
        rgb = Image.open(image_path).convert('RGB')
        draw = Image.fromarray(np.array(rgb))
        buffered = BytesIO()
        rgb.save(buffered, format='PNG')
        img_b64 = base64.b64encode(buffered.getvalue()).decode('ascii')
        visual = f'data:image/png;base64,{img_b64}'

    return (pipelines, visual) if visualize else pipelines


def detect_pipelines(image_path, visualize=False):
    """
    Detect line segments in the image using Canny + HoughLinesP.

    Args:
        image_path (str): path to the image file (PNG, JPG, or PDF).
        visualize (bool): if True, returns a base64 PNG with drawn lines as well.

    Returns:
        pipelines (list): list of {"source": [x1,y1], "destination": [x2,y2]} dicts.
        optionally visual (str): base64 PNG data URL when visualize=True.
    """
    # Handle PDF input - convert first page to PNG
    if image_path.lower().endswith('.pdf'):
        pages = convert_from_path(image_path, first_page=1, last_page=1)
        if not pages:
            raise ValueError("Could not convert PDF to image")

        # Save first page as temporary PNG
        tmp_dir = '/tmp'  # Always use system temp for consistency
        tmp_png = os.path.join(tmp_dir, f'converted_{os.path.basename(image_path)}.png')
        pages[0].save(tmp_png, 'PNG')

        try:
            # Process the PNG
            result = _detect_pipelines_cv2(tmp_png, visualize=visualize) if _cv2_available else _fallback_detect_pipelines(tmp_png, visualize=visualize)
            print(f"Pipeline detection result type: {type(result)}")  # Debug log
            return result
        finally:
            # Clean up temporary PNG
            try:
                os.remove(tmp_png)
            except Exception:
                pass
    
    # Regular image input
    return _detect_pipelines_cv2(image_path, visualize=visualize) if _cv2_available else _fallback_detect_pipelines(image_path, visualize=visualize)

def _detect_pipelines_cv2(image_path, visualize=False):
    """OpenCV implementation of pipeline detection."""
    print(f"OpenCV: Detecting pipelines in {image_path}")  # Debug log
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError('Could not read image')

    print(f"OpenCV: Image loaded successfully, shape: {img.shape}")  # Debug log

    # Convert to grayscale and ensure proper type
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Canny edge detection
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150, apertureSize=3)

    # Hough line transform (probabilistic)
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)

    pipelines = []
    vis_img = img.copy() if visualize else None
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0].tolist()
            pipelines.append({"source": [int(x1), int(y1)], "destination": [int(x2), int(y2)]})
    print(f"OpenCV detected pipelines type: {type(pipelines)}, length: {len(pipelines)}")  # Debug log
    if lines is not None and visualize:
        for line in lines:
            x1, y1, x2, y2 = line[0].tolist()
            cv2.line(vis_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    if visualize:
        # Convert BGR to RGB for PIL
        vis_rgb = cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(vis_rgb)
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode('ascii')
        data_url = f'data:image/png;base64,{img_b64}'
        return pipelines, data_url

    return pipelines