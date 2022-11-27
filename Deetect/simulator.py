import time
from os.path import basename
import numpy as np
from PyQt5.QtWidgets import QApplication, QMessageBox
import utils
from analysis import nuclei_detection as pnd
from analysis import elimination_splitting as pes
from analysis import double_counting as pdc
import pandas as pd
from pathlib import Path


def run_file_by_file_for_all_analysis(params, progress_bar, info_lbl):
    # sys.stdout = open(self.outputFile + self.condition + '_console_out.txt', 'w')
    tic_total = time.time()
    print('\n', utils.get_formatted_datetime(), '&&SIM-INFO: Analysis STARTED for all selected images')
    df_stats = create_df(params)
    diameters = []
    try:
        utils.check_and_mkdir(params.cp_orj_out)
        utils.check_and_mkdir(params.cp_png_out)
        if params.elim_out != "":
            utils.check_and_mkdir(params.elim_out)
        if params.double_out != "":
            utils.check_and_mkdir(params.double_out)

        processed_file = 0
        for parent_img_name in params.filelist:
            masks_numbers = []
            print(utils.get_formatted_datetime(), '##SIM-INFO: Analysis STARTED for file:', parent_img_name)
            try:
                stacked_imgs, files = utils.read_tif_apply_stacking(parent_img_name, params.stack_size,
                                                                    params.outputFile, params.rotation, params.projection_type)

                masks_numbers_cp = []
                diameter = []

                masks_list = []
                img_list = []
                for img, filename in zip(stacked_imgs, files):
                    info_lbl.setText("TIME: " + utils.get_formatted_datetime() + "\nPROCESS: Nuclei detection" +
                                     "\nProcessed File: " + filename + '\nOriginal File: ' + parent_img_name)
                    QApplication.processEvents()

                    masks, flows, styles, diams, img_outlined = pnd.cellpose_eval(img, params.channels,
                                                                                  params.cp_model,
                                                                                  params.flow_thresh,
                                                                                  params.mask_thresh, filename,
                                                                                  params.cp_png_out,
                                                                                  params.cp_orj_out)

                    img_list.append(img_outlined)
                    masks_list.append(masks)
                    masks_numbers_cp.append(len(np.unique(masks)[1:]))
                    diameter.append(diams)

                    processed_file += 1
                    progress_bar.setValue(int(processed_file * 100 / (params.filenumber * len(files))))
                    QApplication.processEvents()
                masks_numbers.append(masks_numbers_cp)
                if params.double_out != "":
                    # double counting
                    info_lbl.setText("TIME: " + utils.get_formatted_datetime() + "\nPROCESS: Double counting" +
                                     '\nOriginal File: ' + parent_img_name)
                    QApplication.processEvents()

                    count = len(masks_list)

                    masks_list, img_list, masks_numbers_double = pdc.double_counting_for_all_projections \
                        (parent_img_name, img_list, masks_list, files, params.double_out, params.intersect_thresh)

                    masks_numbers.append(masks_numbers_double)
                if params.elim_out != "":
                    # elimination
                    info_lbl.setText(
                        "TIME: " + utils.get_formatted_datetime() + "\nPROCESS: Elimination and Splitting" +
                        '\nOriginal File: ' + parent_img_name)
                    QApplication.processEvents()
                    masks_numbers_elim = pes.elimination_for_all_projections(parent_img_name, img_list, masks_list,
                                                                             files,
                                                                             params.elim_out,
                                                                             params.big_area_thresh,
                                                                             params.small_area_thresh,
                                                                             params.intensity_thresh)
                    masks_numbers.append(masks_numbers_elim)

                masks_numbers = np.transpose(masks_numbers).tolist()
                add_stats_df(df_stats, masks_numbers, files, parent_img_name)
                diameters.append(diameter)

            except ValueError as err:
                print(utils.get_formatted_datetime(), '##SIM-ERROR:', err, parent_img_name)
        df_to_file(df_stats, params.outputFile)
        QApplication.processEvents()

    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
    finally:
        print('&&SIM-Total Process Times: %0.3f sec' % (time.time() - tic_total))
        print(utils.get_formatted_datetime(), '&&SIM-INFO: Analysis ENDED for all selected images')
        QMessageBox.information(None, "DONE",
                                "All analysis were complete. Please group the images to perform statistics ")


def create_df(params):
    col = ['Folder', 'Parent_Image', 'Image_name', 'Nuclei Detection']
    if params.double_out != "":
        col.append('Double Counting Analysis')
    if params.elim_out != "":
        col.append('Elimination Processes')
    df = pd.DataFrame(columns=col)
    return df


def df_to_file(df, outputFile):
    file = f'{outputFile}/number_of_cell_df.txt'
    df.to_csv(file, sep="\t", index=False)


def add_stats_df(df, masks_numbers, files, parent_img_path):
    folder = basename(Path(parent_img_path).parent.name)
    parent_name = basename(parent_img_path)
    for counts, filename in zip(masks_numbers, files):
        a_list = [folder, parent_name, filename]
        a_list.extend(counts)
        df.loc[len(df.index)] = a_list