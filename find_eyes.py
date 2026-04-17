import cv2
import numpy as np
import time

WIDTH = 1280
HEIGHT = 720

def find_red_spot_vectorized(image):
    b = image[:, :, 0].astype(np.int16)
    g = image[:, :, 1].astype(np.int16)
    r = image[:, :, 2].astype(np.int16)
    mask = (r > (g + 100)) & (r > (b + 100))
    result = np.zeros_like(image)
    result[mask] = [0, 0, 255]
    return result

def get_biggest_red_bounding_box(image):
    b = image[:, :, 0].astype(np.int16)
    g = image[:, :, 1].astype(np.int16)
    r = image[:, :, 2].astype(np.int16)
    mask = ((r > (g + 100)) & (r > (b + 100))).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    coords = None # (x, y, w, h)
    output_img = image.copy()
    if contours:
        biggest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest_contour)
        coords = (x, y, x + w, y + h) # Returning as (x1, y1, x2, y2)
        cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return coords, output_img

def _middle_position_normalized(corners):
    if not corners or not len(corners) == 4:
        return None
    xmid = (corners[2] + corners[0]) / 2
    ymid = (corners[3] + corners[1]) / 2
    xlen = (corners[2] - corners[0])
    ylen = (corners[3] - corners[1])
    longest = max((xlen, ylen))
    if longest == xlen:
        z_pos = longest / WIDTH
    else:
        z_pos = longest / HEIGHT
    return (xmid / WIDTH, ymid / HEIGHT, z_pos)

def find_red_spot(image):
    for i, line in enumerate(image):
        for j, point in enumerate(line):
            if point[2] > int(point[1])+100 and point[2] > int(point[0])+100:
                point[2] = 255
                point[1] = 0
                point[0] = 0
            else:
                point[2] = 0
                point[1] = 0
                point[0] = 0
    return image

def showtime(image):
    cv2.imshow("Live",image)

def write_image_to_file(image, filename):
    cv2.imwrite(filename, image)

def write_matrix_to_file(frame, filename):
    with open(filename, "w") as f:
        for pixel in frame:
            pixel.tofile(f, sep=" ")
            f.write("\n")

def get_current_frame_matrix(cap):
    ret,frame= cap.read()
    cv2.waitKey(1)
    return frame

def setup_capture_device():
    cap=cv2.VideoCapture(cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    if not (cap.isOpened()):
        print("Could not open video device")
    return cap

def target_position(camera):
    frame = get_current_frame_matrix(camera)
    coordinates, frame = get_biggest_red_bounding_box(frame)
    return _middle_position_normalized(coordinates)

if __name__ == "__main__":
    camera = setup_capture_device()
    while True:
        frame = get_current_frame_matrix(camera)
        coordinates, frame = get_biggest_red_bounding_box(frame)
        print(_middle_position_normalized(coordinates))
        showtime(frame)