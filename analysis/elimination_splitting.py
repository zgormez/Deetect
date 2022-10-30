import os
import cv2
import numpy as np
from cellpose import utils as cp_utils
import utils

user_interaction = False


def split_masks(masks, img1, out_path, filename, parent_img_path):
    # TODO no need parent image path, use only filename
    fout_path = parent_img_path + os.path.splitext(filename)[0].split("_")[-1]

    fout = open(out_path + fout_path + '_maskInfo.txt', "w")
    infos_all = []

    big_masks = np.zeros(masks.shape, masks.dtype)
    small_masks = np.zeros(masks.shape, masks.dtype)
    invisible_masks = np.zeros(masks.shape, masks.dtype)
    imgOutlined = utils.createOutlinedImgFromMask(img1.copy(), masks)

    intensity_list = [13, 16, 24, 50, 100, 127, 200, 250, intensity_thresh]  # TODO get this list from gui
    fout.write("mNr\tdiam\tarea\tconv\tsolid\tcomp\tmean\tmax\tmin\t%intens>" +
               "\t".join(str(round(item)) for item in intensity_list) + "\tMASK_INFO\n")
    # loop over the unique labels returned by the Cellpose
    invisible_count = 0
    small_count = 0
    big_count = 0
    for label in np.unique(masks)[1:]:  # first label is zero, we are examining the 'background' so simply ignore it
        maski = np.zeros(masks.shape, dtype="uint8")
        maski[masks == label] = 1

        convexity, solidity, compactness = cp_utils.get_mask_stats(maski)  # TODO range(masks.max()) problemi

        masks_diam = cp_utils.diameters(maski)[1][0]
        area = np.unique(maski, return_counts=True)[1][1:][0]

        img_val = img1[masks == label][:, 0]
        infos = [label, round(masks_diam), area, round(convexity[0], 2), round(solidity[0], 2),
                 round(compactness[0], 2), round(np.mean(img_val), 1), np.max(img_val), np.min(img_val)]
        intensPercent = []
        for i in intensity_list:
            percent = round(len(np.where(img_val > i)[0]) * 100 / area, 1)
            infos.append(percent)
            intensPercent.append(percent)
        infos_all.append(infos[1:])
        if intensPercent[-1] < 50:
            infos.append("INVISIBLE: <%s" % intensity_thresh)
            invisible_count += 1
            invisible_masks[masks == label] = label
        elif area < small_areaLimit:
            infos.append("SMALL MASK <%s " % small_areaLimit)
            small_count += 1
            small_masks[masks == label] = label
        elif area // big_areaLimit > 1 and intensPercent[5] >= 50:
            big_count += int((area // big_areaLimit)) - 1
            infos.append("BIG MASK > {}:{}".format(big_areaLimit, area // big_areaLimit))
            big_masks[masks == label] = label
        fout.write("\t".join(str(item) for item in infos) + "\n")

    if infos_all:
        fout.write("mean\t" + "\t".join(str(round(item)) for item in (np.nanmean(infos_all, axis=0))) + "\n")
    else:
        fout.write("No nuclei detected\n")

    rest_mask_count = len(np.unique(masks)[1:]) - (invisible_count + small_count) + big_count
    mask_count = [len(np.unique(masks)[1:]), -invisible_count, -small_count, big_count, rest_mask_count]
    fout.write("\n\n#cellpose\t#invisible\t#small\t#big\t#remain\n")
    fout.write("\t".join(str(item) for item in mask_count))
    fout.close()

    imgOutlined = utils.createOutlinedImgFromMask(imgOutlined, big_masks, utils.Color.GRAY.value)
    imgOutlined = utils.putNumbersOnImage(imgOutlined, big_masks, utils.Color.WHITE.value)
    imgOutlined = utils.createOutlinedImgFromMask(imgOutlined, small_masks, utils.Color.YELLOW.value)
    imgOutlined = utils.putNumbersOnImage(imgOutlined, small_masks, utils.Color.WHITE.value)
    imgOutlined = utils.createOutlinedImgFromMask(imgOutlined, invisible_masks, utils.Color.BLUE.value)
    imgOutlined = utils.putNumbersOnImage(imgOutlined, invisible_masks, utils.Color.WHITE.value)

    imgOutlined = utils.create_bottom_border_add_info(imgOutlined, 'outline')
    cv2.imwrite(out_path + fout_path + "_elm&split_mask.png", imgOutlined, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    return infos_all, mask_count


def elimination_for_all_projections(parent_img_name, img_list, masks_list, files, elim_out, big_area_thresh,
                                    small_area_thresh, intens_thresh):
    global big_areaLimit, small_areaLimit, intensity_thresh
    big_areaLimit = big_area_thresh
    intensity_thresh = intens_thresh
    small_areaLimit = small_area_thresh
    parent_img_name = os.path.splitext(os.path.basename(parent_img_name))[0]
    file_path = elim_out + 'numofcell-elim_split.txt'
    fo = open(file_path, "a")
    if os.path.getsize(file_path) == 0:
        fo.write("Image Name\t#cellpose\t#invisible\t#small\t#big\t#remain\n")

    print(utils.get_formatted_datetime(), '####EL-INFO: Elimination started for file:',  parent_img_name)
    masks_numbers = []
    for masks, img, filename in zip(masks_list, img_list, files):
        infos_all, rest_mask_count = split_masks(masks, img.copy(), elim_out, filename, parent_img_name)
        masks_numbers.append(rest_mask_count[-1])
        fo.write(filename + '\t' + "\t".join(str(item) for item in rest_mask_count) + '\n')
    fo.close()
    print(utils.get_formatted_datetime(), "####EL-INFO: Elimination ended for file:",  parent_img_name)
    return masks_numbers


