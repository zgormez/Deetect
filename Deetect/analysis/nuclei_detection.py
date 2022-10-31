import gc
import os
import time
import cv2
import numpy as np
import torch
from cellpose import models, io, plot
from cellpose import utils as cp_utils
import utils


def save_cellpose_results_separately_as_png(img, maski, flowi, cp_png_out, file_name, channels=[0, 0]):
    """ plot segmentation results (like on website)

    Can save each panel of figure with file_name option. Use channels option if
    img input is not an RGB image with 3 channels.

    Parameters
    -------------

    img: 2D or 3D array
        image input into cellpose

    maski: int, 2D array
        for image k, masks[k] output from Cellpose.eval, where 0=NO masks; 1,2,...=mask labels

    flowi: int, 2D array
        for image k, flows[k][0] output from Cellpose.eval (RGB of flows)

    channels: list of int (optional, default [0,0])
        channels used to run Cellpose, no need to use if image is RGB

    file_name: (list of) str
        names of files of images
    """

    img0 = img.copy()
    if img0.shape[0] < 4:
        img0 = np.transpose(img0, (1, 2, 0))
    if img0.shape[-1] < 3 or img0.ndim < 3:
        img0 = plot.image_to_rgb(img0, channels=channels)
    else:
        if img0.max() <= 50.0:
            img0 = np.uint8(np.clip(img0 * 255, 0, 1))

    outlines = cp_utils.masks_to_outlines(maski)
    overlay = plot.mask_overlay(img0, maski)

    outX, outY = np.nonzero(outlines)
    imgout = img0.copy()
    imgout[outX, outY] = np.array([0, 255, 0])  # green border
    imgout = utils.putNumbersOnImage(imgout, maski, utils.Color.GREEN.value)

    save_path = os.path.splitext(file_name)[0]

    cv2.imwrite(cp_png_out + save_path + '_overlay_mask.png', overlay, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    cv2.imwrite(cp_png_out + save_path + '_outlines.png', imgout, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    cv2.imwrite(cp_png_out + save_path + '_flows_cellpose.png', flowi, [cv2.IMWRITE_PNG_COMPRESSION, 0])


def save_cellpose_results(img, masks, flows, diams, cp_orj_out, filename, chan):
    # save results so you can load in cellpose gui
    io.masks_flows_to_seg(img, masks, flows, diams, cp_orj_out + filename, chan)
    # save results as png
    io.save_masks(img, masks, flows, filename, png=True, savedir=cp_orj_out)


def cellpose_eval(img, channels, cp_model, flow_thresh, mask_thresh, filename, cp_png_out, cp_orj_out):
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.empty_cache()
    tic = time.time()
    # define CHANNELS to run segementation on
    # grayscale=0, R=1, G=2, B=3
    # channels = [cytoplasm, nucleus]
    # if NUCLEUS channel does not exist, set the second channel to 0
    # channels = [[0, 0]]
    # IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
    # channels = [0,0] # IF YOU HAVE GRAYSCALE
    # channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
    # channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

    # if diameter is set to None, the size of the cells is estimated on a per image basis
    # you can set the average cell `diameter` in pixels yourself (recommended)
    # diameter can be a list or a single number for all images

    # model_type='cyto' or model_type='nuclei'
    model = models.Cellpose(gpu=True, model_type=cp_model)
    print(utils.get_formatted_datetime(), '####CP-INFO:Nuclei Detection started for file:', filename)
    masks, flows, styles, diams = model.eval(img, diameter=None, channels=channels, flow_threshold=flow_thresh,
                                             mask_threshold=mask_thresh, net_avg=2)
    print('----CP-INFO the process took  %0.3f seconds' % (time.time() - tic))

    save_cellpose_results(img, masks, flows, diams, cp_orj_out, filename, channels)
    save_cellpose_results_separately_as_png(img, masks, flows[0], cp_png_out, filename, channels)
    imgOutlined = utils.createOutlinedImgFromMask(img, masks, utils.Color.GREEN.value)
    imgOutlined = utils.putNumbersOnImage(imgOutlined, masks, utils.Color.RED.value)
    print('----CP-INFO %d cells found with cellpose net' % (len(np.unique(masks)[1:])))
    return masks, flows, styles, diams, imgOutlined



