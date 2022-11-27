from datetime import datetime
import os
from enum import Enum
import numpy as np
from cellpose import utils, io
import cv2
import rasterio.features
from shapely.geometry import Polygon
import imutils
from Deetect.Projection import Projection
import SimpleITK as sitk

text_size = 0.28
text_font = cv2.FONT_HERSHEY_SIMPLEX


def check_and_mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def createBGR(imgB):
    if len(imgB.shape) == 2:
        h, w = imgB.shape
        imgBGR = np.zeros((h, w, 3), imgB.dtype)
        imgBGR[:, :, 0] = imgB
        return imgBGR
    else:
        return imgB


def read_tif_apply_stacking(img_path, stack_size, output_dir, rotation, projection_type=Projection.MAX):
    imgs = io.imread(img_path)
    if stack_size == 1:
        stacked_imgs, files = no_stacking(imgs, os.path.basename(img_path))
    elif stack_size == 2 or stack_size == 5:
        stacked_imgs, files = apply_stacking(imgs, os.path.basename(img_path), stack_size, projection_type)
    else:
        stacked_imgs, files = stack_all_scans(imgs, os.path.basename(img_path), projection_type)
    # degree 0: cv2.ROTATE_90_CLOCKWISE, 1: cv2.ROTATE_180, 2: 270, cv2.ROTATE_90_COUNTERCLOCKWISE
    if rotation is not None:
        rotate_images(stacked_imgs, rotation)
        # rotate_warpAffine_images(stacked_imgs, 270)

    # pre-process

    # rolling_ball(stacked_imgs)
    # apply_clahe(stacked_imgs)
    # blur_images(stacked_imgs, 3)
    list_imgBGR = []
    for i in list(stacked_imgs):
        list_imgBGR.append(createBGR(i))

    save_all_images(f'{output_dir}png_stck{stack_size}/', list_imgBGR, files)
    return list_imgBGR, files


def no_stacking(imgs, img_path):
    img_list = []
    file_list = []
    img_base_path = os.path.splitext(img_path)[0]
    for i in range(len(imgs)):
        file_list.append(img_base_path + '_s' + str(i + 1) + '.png')
        img_list.append(imgs[i])

    return img_list, file_list


def apply_stacking(imgs, img_path, stack_size, projection_type):
    number_of_slices = len(imgs)
    # number_of_slices = 2
    img_list = []
    file_list = []
    if number_of_slices % stack_size == 0:
        img_base_path = os.path.splitext(img_path)[0]
        for x in range(0, number_of_slices, stack_size):
            # for x in range(0, len(imgs), stack_size):
            filename = img_base_path + '_s' + str(x + 1) + "-" + str(x + stack_size) + '.png'
            file_list.append(filename)
            # img_s1 = np.maximum.reduce(imgs[x:x + stack_size])
            img_project = apply_projection(imgs[x:x + stack_size], projection_type)
            img_list.append(img_project)
    else:
        raise ValueError(f'{number_of_slices} slices cannot be grouped in {stack_size}')
    return img_list, file_list


def stack_all_scans(imgs, img_path, projection_type):
    img_list = []
    file_list = []
    file_list.append(os.path.splitext(img_path)[0] + '_all' + '.png')
    img_list.append(apply_projection(imgs, projection_type))
    return img_list, file_list


def apply_projection(imgs, type):
    axe = 2  # projection along axe z.
    img_sitk = sitk.GetImageFromArray(imgs)  # Get a SimpleITK Image from a numpy array.
    if type == Projection.MAX:
        # projection_np = np.maximum.reduce(imgs)
        projection = sitk.GetArrayFromImage(sitk.MaximumProjection(img_sitk, axe))[0]
    elif type == Projection.MIN:
        # projection_np = np.minimum.reduce(imgs)
        projection = sitk.GetArrayFromImage(sitk.MinimumProjection(img_sitk, axe))[0]
    elif type == Projection.MEAN:
        # projection_np = np.mean(imgs,axis=0)
        projection_64 = sitk.GetArrayFromImage(sitk.MeanProjection(img_sitk, axe))[0]
        projection = normalize_uint8(projection_64)
    elif type == Projection.MEDIAN:
        #projection_np = np.median(imgs,axis=0)
        projection_64 = sitk.GetArrayFromImage(sitk.MedianProjection(img_sitk, axe))[0]
        projection = normalize_uint8(projection_64)
    elif type == Projection.STD:
        # projection_np = np.std(imgs,axis=0)
        projection_64 = sitk.GetArrayFromImage(sitk.StandardDeviationProjection(img_sitk, axe))[0]
        projection = normalize_uint8(projection_64)
    elif type == Projection.SUM:
        # projection_np = np.sum(imgs,axis=0)
        projection_64 = sitk.GetArrayFromImage(sitk.SumProjection(img_sitk, axe))[0]
        projection = normalize_uint8(projection_64)
    return projection


def normalize_uint8(img):
    return cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)


def apply_clahe(img_list):
    for i, img in enumerate(img_list):
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        # TODO after that apply rolling ball to remove background
        img_list[i] = clahe.apply(img)


def rolling_ball(img_list):
    from skimage import restoration
    for i, img in enumerate(img_list):
        background = restoration.rolling_ball(img, kernel=restoration.ellipsoid_kernel((21, 21), 0.1))
        img_list[i] = img - background


def rotate_images(img_list, degree):
    # degree 0: cv2.ROTATE_90_CLOCKWISE, 1: cv2.ROTATE_180, 2: 270, cv2.ROTATE_90_COUNTERCLOCKWISE
    for i, img in enumerate(img_list):
        img_list[i] = cv2.rotate(img, degree)


def rotate_warpAffine_images(img_list, degree):
    for i, img in enumerate(img_list):
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), degree, 1.0)
        img_list[i] = cv2.warpAffine(img, M, (w, h))


def blur_images(img_list, ksize):
    for i, img in enumerate(img_list):
        img_list[i] = cv2.blur(img, (ksize, ksize))


def save_all_images(png, img_list, file_list):
    check_and_mkdir(png)
    print('Stacking results:')
    for i, [img, file] in enumerate(zip(img_list, file_list)):
        save_path = os.path.splitext(file)[0]
        cv2.imwrite(png + save_path + '_img.png', img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        cv2.imwrite(png + save_path + '_B.png', img[:, :, 0], [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print("file saved: " + png + save_path)


def max_aggregation(img1, img2):
    max_cv = cv2.max(img1, img2)
    # max_np = np.maximum(img1, img2)
    return max_cv


def createOutlinedImgFromMask(img0, maski, color=None):
    if color is None:
        color = [0, 255, 0]
    outlines = utils.masks_to_outlines(maski)
    outX, outY = np.nonzero(outlines)
    if len(img0.shape) == 2:
        img0 = createBGR(img0)
    img0[outX, outY] = np.array(color)  # green border
    return img0


def putNumbersOnImage(img0, masks, color=None):
    if color is None:
        color = [0, 0, 255]
    for label in np.unique(masks)[1:]:  # first label is zero, we are examining the 'background' so simply ignore it
        x, y = get_center_info(masks, label)
        img0 = cv2.putText(img0, str(label), (int(x), int(y)), text_font, text_size, color, 1)
    return img0


def put_mask_number_with_same_color(img, masks, diff_masks):
    for label in np.unique(masks)[1:]:  # first label is zero, we are examining the 'background' so simply ignore it
        color = generate_random_color()
        img[diff_masks == label] = color
        x, y = get_center_info(masks, label)
        img = cv2.putText(img, str(label), (int(x), int(y)), text_font, text_size, color, 1)
    return img


def maskoverlay_and_number_with_same_color(img, masks, diff_masks, colors):
    for label in np.unique(masks)[1:]:  # first label is zero, we are examining the 'background' so simply ignore it
        color = colors[label - 1]
        img[diff_masks == label] = np.array(color)
        x, y = get_center_info(masks, label)
        img = cv2.putText(img, str(label), (int(x), int(y)), text_font, text_size, color, 1)

        # cv2.imshow("mask", img)
        # cv2.waitKey(0)
    return img


def get_center_info(masks, label):
    x, y = get_center_of_biggest_polygon(masks, label)
    # TODO there is a problem with new function
    # x, y = get_center_of_component(masks, label)
    return x, y


def get_center_of_biggest_polygon(masks1, label):
    p1 = get_biggest_polygon(masks1, label)
    x, y = p1.centroid.coords[0]
    return x, y


def get_biggest_polygon(masks1, label):
    # create a polygon
    maskimg1 = np.zeros(masks1.shape, dtype="uint8")
    maskimg1[masks1 == label] = 1
    shapes = rasterio.features.shapes(maskimg1)
    # p1 = [Polygon(shape[0]["coordinates"][0]) for shape in shapes if shape[1] == 1][0]
    poly_list = []
    for shape in shapes:
        if shape[1] == 1:
            poly_list.append([Polygon(shape[0]["coordinates"][0])][0])
    p1 = poly_list[0]
    for p in poly_list[1:]:
        if p1.area < p.area:
            p1 = p
    return p1


def get_center_of_component(masks1, label):
    # create an image contains only specific label
    maskimg1 = np.zeros(masks1.shape, dtype="uint8")
    maskimg1[masks1 == label] = 1

    # Find contours:
    # im, contours, hierarchy = cv2.findContours(maskimg1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = cv2.findContours(maskimg1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(contours)
    # Calculate image moments of the detected contour

    # TODO check if there is more than one contours and also look at ERROR
    n = 0
    center_x = 0
    center_y = 0
    for c in cnts:
        n = n + 1
        M = cv2.moments(c)
        center_x = round(M['m10'] / M['m00'])  # ZeroDivisionError: float division by zero
        center_y = round(M['m01'] / M['m00'])
        if n > 1:
            print('!!! WARNING: utils.get_center_of_component: multiple contour')
            break
    return center_x, center_y


def create_bottom_border_add_info(img, info):
    if info == 'outline':
        text = 'Color Legend for Cell Outline > green: detected via cellpose, red: double counted-ignored, ' \
               'blue: invisible-ignored, yellow: small-ignored, gray: big'
    elif info == 'intersect':
        text = 'Color Legend for intersection Area > green: intersection percent bigger than the ' \
               'threshold-double counting,  red: intersection percent smaller than the threshold'
    img = cv2.copyMakeBorder(img, 0, 30, 0, 0, cv2.BORDER_CONSTANT, value=(250, 250, 250))
    img = cv2.putText(img, text, (0, img.shape[0] - 10), text_font, text_size * 1.4, (0, 0, 0), 1)
    # img = cv2.putText(img, 'denememememmemme', (0, img.shape[0] + 5), text_font, text_size * 1.5, (0, 0, 255), 1)

    return img


class Color(Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    # ORANGE = (48, 130, 245)
    GRAY = (128, 128, 128)


def generate_random_color():
    color = np.random.randint(0, 256, size=(3,))
    color = (int(color[0] + 50), int(color[1]), int(color[2]))
    return color


def generate_n_random_colors(n):
    colors = []
    for i in range(n):
        colors.append(generate_random_color())
    return colors


def get_formatted_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_stats(values):
    stats = [round(np.mean(values)), np.max(values), np.min(values), round(np.median(values))]
    return stats


def perform_preprocess(ch_raw, processes):
    if 'gauss' in processes:
        ch_pre = apply_blurring(ch_raw)
    elif 'usm' in processes:  # result is not acceptable
        ch_pre = perform_usm(ch_raw)
    return ch_pre


def apply_blurring(ch_raw):
    ch_blur = []
    for c in ch_raw:
        ch_blur.append(cv2.GaussianBlur(c, (5, 5), 0))

    return ch_blur


def perform_usm(ch_raw):
    ch_sharp = []
    for c in ch_raw:
        # ch_sharp.append(unsharp_mask(c, radius=2, amount=2))
        c_gauss = cv2.GaussianBlur(c, (5, 5), 0)
        c_usm = cv2.addWeighted(c, 2.0, c_gauss, -1.0, 0)
        ch_sharp.append(c_usm)
    return ch_sharp
