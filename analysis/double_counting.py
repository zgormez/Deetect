import os
import cv2
import numpy as np
import utils
import cellpose as cp

user_interaction = False


def applyElimination(is_perc1, is_perc2):
    if is_perc1 < intersect_percent and is_perc2 < intersect_percent:
        return False
    else:
        return True


def classify_and_draw_intersect(intersect, area1, area2, img1, img2, label1, label2):
    is_perc1 = intersect.area / area1
    is_perc2 = intersect.area / area2
    areaOfsect = [intersect.area, "{:.1%}".format(is_perc1), "{:.1%}".format(is_perc2)]
    doubleCountedPair = ""
    removeInfo = ""
    if applyElimination(is_perc1, is_perc2):
        doubleCountedPair = (label1, label2)
        intersec_color = utils.Color.GREEN.value
        removeInfo = [1, label1] if is_perc1 >= is_perc2 else [2, label2]
        areaOfsect.append("DOUBLE COUNTING: REMOVE from img{}, mNr:{}".format(removeInfo[0], removeInfo[1]))
    else:
        intersec_color = utils.Color.RED.value

    nparr = np.asarray(intersect.exterior.coords, dtype=int)
    cv2.fillPoly(img1, pts=[nparr], color=intersec_color)
    cv2.fillPoly(img2, pts=[nparr], color=intersec_color)

    if user_interaction:
        cv2.imshow("poly intersection", np.hstack((img1, img2)))
        cv2.waitKey(0)
    return areaOfsect, doubleCountedPair, removeInfo


def masks_intersection(masks1, masks2, img1, img2, is_img_path):
    fo = open(is_img_path + '_intersections.txt', "w")
    fo.write("mNr1\tmNr2\tarea1\tarea2\tarea_is\tper1\tper2\tcomment\n")
    # polygon intersection analysis
    img_is1 = img1.copy()
    img_is2 = img2.copy()
    intersectLabels = []
    doublecountedAllPairs = []
    doubleInfos = []

    # get the overlapped values between masks1 and masks2
    cp_overlap = cp.metrics._label_overlap(masks1, masks2)
    # loop over the masks1 which have an intersection with  masks2
    masks_have_is = np.where(np.sum(cp_overlap[:, 1:], axis=1, keepdims=True) > 0)[0]
    for label1 in masks_have_is:
        if label1 == 0:
            continue
        p1 = utils.get_biggest_polygon(masks1, label1)
        is_masks = np.where(cp_overlap[label1] > 0)[0]
        for label2 in is_masks:
            if label2 == 0:
                continue
            p2 = utils.get_biggest_polygon(masks2, label2)
            intersect = p1.intersection(p2)
            if intersect:
                is_info = []
                doubleCountedPairs = []
                if intersect.geom_type == 'Polygon':
                    # print(intersect.geom_type)
                    is_info, doubleCountedPairs, removeInfo = classify_and_draw_intersect(intersect, p1.area, p2.area,
                                                                                          img_is1, img_is2, label1, label2)
                elif intersect.geom_type == 'GeometryCollection':
                    for sect in intersect:
                        # print(sect.geom_type)
                        if sect.geom_type == 'Polygon':
                            is_info, doubleCountedPairs, removeInfo = classify_and_draw_intersect(sect, p1.area,
                                                                                                  p2.area, img_is1,
                                                                                                  img_is2, label1,
                                                                                                  label2)
                if is_info:
                    intersectLabels.append(is_info)
                    fo.write("\t".join(str(item) for item in [label1, label2, p1.area, p2.area]) + "\t")
                    fo.write("\t".join(str(item) for item in is_info) + "\n")
                if doubleCountedPairs:
                    doublecountedAllPairs.append(doubleCountedPairs)
                    doubleInfos.append(removeInfo)

    img1p = utils.createOutlinedImgFromMask(img_is1, masks1)
    img2p = utils.createOutlinedImgFromMask(img_is2, masks2)
    img_is = np.hstack(
        (cv2.copyMakeBorder(img1p, 0, 0, 0, 5, cv2.BORDER_CONSTANT, value=utils.Color.YELLOW.value), img2p))

    fo.write("# of total intersect {}\n".format(len(intersectLabels)))
    fo.write("# of double counted intersect {}: ".format(len(doublecountedAllPairs)))
    fo.write(str(doublecountedAllPairs) + "\n")
    fo.write("# of cells to be deleted {}: ".format(len(doubleInfos)))
    fo.write(str(doubleInfos) + "\n")
    fo.close()

    # removing operation for double counted cells
    numberofMask = [len(np.unique(masks1)[1:]), len(np.unique(masks2)[1:])]

    removedMask1 = np.zeros(masks1.shape, masks1.dtype)
    removedMask2 = np.zeros(masks2.shape, masks2.dtype)
    for imgNr, maskNr in doubleInfos:
        if imgNr == 1:
            removedMask1[masks1 == maskNr] = maskNr
            masks1[masks1 == maskNr] = 0
        if imgNr == 2:
            removedMask2[masks2 == maskNr] = maskNr
            masks2[masks2 == maskNr] = 0

    numberofMask.append(len(np.unique(masks1)[1:]))
    numberofMask.append(len(np.unique(masks2)[1:]))
    numberofMask.append(len(np.unique(removedMask1)[1:]))
    numberofMask.append(len(np.unique(removedMask2)[1:]))
    numberofMask.append(len(doubleInfos))

    img1o = img1.copy()
    img2o = img2.copy()
    img1o = utils.createOutlinedImgFromMask(img1o, removedMask1, utils.Color.RED.value)
    img1o = utils.putNumbersOnImage(img1o, removedMask1, utils.Color.WHITE.value)
    img2o = utils.createOutlinedImgFromMask(img2o, removedMask2, utils.Color.RED.value)
    img2o = utils.putNumbersOnImage(img2o, removedMask2, utils.Color.WHITE.value)
    img_rem = np.hstack(
        (cv2.copyMakeBorder(img1o, 0, 0, 0, 5, cv2.BORDER_CONSTANT, value=utils.Color.YELLOW.value), img2o))

    if user_interaction:
        cv2.imshow("mask intersection", img_is)
        cv2.waitKey(0)

    img_is = utils.create_bottom_border_add_info(img_is, 'intersect')
    cv2.imwrite(is_img_path + "_intersection.png", img_is, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    img_rem = utils.create_bottom_border_add_info(img_rem, 'outline')
    cv2.imwrite(is_img_path + "_removedMask.png", img_rem, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    return masks1, masks2, img1o, img2o, numberofMask


def double_counting_for_all_projections(parent_img_name, img_list, masks_list, files, double_out, intersect_thresh ):
    global intersect_percent
    intersect_percent = intersect_thresh / 100
    parent_img_name = os.path.splitext(os.path.basename(parent_img_name))[0]
    print(utils.get_formatted_datetime(), '####DC-INFO:Double Counting started for file:',  parent_img_name)
    file_path = double_out + 'numofcell_doublecount.txt'
    fout = open(file_path, "a")
    if os.path.getsize(file_path) == 0:
        fout.write('cell numbers before & after double counting analysis\n')
        fout.write("compared_projections\tbefore-P1\tbefore-P2\tafter-P1\tafter-P2\tdiff-P1\tdiff-P2\tdiff-all\n")

    masks_numbers = [0] * len(masks_list)
    for ind in range(len(masks_list) - 1):
        p1_postfix = os.path.splitext(files[ind])[0].split("_")[-1]
        p2_postfix = os.path.splitext(files[ind + 1])[0].split("_")[-1]
        is_img_name = parent_img_name + p1_postfix + '-' + p2_postfix
        mask1_npy = masks_list[ind]
        mask2_npy = masks_list[ind + 1]
        img1 = img_list[ind]
        img2 = img_list[ind + 1]
        mask1, mask2, img1o, img2o, numberofMask = masks_intersection(mask1_npy, mask2_npy, img1, img2,
                                                                      double_out + is_img_name)
        masks_list[ind] = mask1
        masks_list[ind + 1] = mask2
        img_list[ind] = img1o
        img_list[ind + 1] = img2o
        masks_numbers[ind] = numberofMask[2]
        masks_numbers[ind + 1] = numberofMask[3]

        fout.write("%s\t" % is_img_name + "\t".join(str(item) for item in numberofMask))
        fout.write("\n")
        print('----DC-INFO cell numbers before & after double counting analysis', numberofMask)
        print(utils.get_formatted_datetime(), "####DC-INFO: Double Counting ended for file:",  is_img_name)
    return masks_list, img_list, masks_numbers
