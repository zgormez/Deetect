import os
import sys
from os import listdir
from pathlib import Path
import torch
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox
import utils
import simulator
from StatsWindow import StatsWindow


class Parameters:
    def __init__(self):
        super().__init__()

        self.filelist = []
        self.filenumber = 0

        # z projection
        self.stack_size = 1

        # preprocessing
        self.rotation = None

        # cellpose
        self.cp_model = 'cyto'
        self.flow_thresh = 0.6
        self.mask_thresh = 0
        self.channels = [0, 3]  # TODO put option in gui and, check if the file has more channel, actually has RGB

        # post-processing
        self.intersect_thresh = 60
        self.intensity_thresh = 16
        self.big_area_thresh = 400
        self.small_area_thresh = 100

        # output
        self.condition = ''
        self.outputFile = ''
        self.outputDir = os.path.abspath(os.path.expanduser("~"))

        torch.cuda.empty_cache()

    def dump_vars(self):
        print("PARAMETERS:")
        attrs = vars(self)
        print('\n'.join("%s: %s" % item for item in attrs.items()))


class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window_qt.ui', self)

        # set defaults
        self.param = None
        self.set_defaults()

        # events
        self.run_btn.clicked.connect(self.run_analyses)
        self.doublecount_cb.stateChanged.connect(
            lambda: self.doublecount_gbox.setEnabled(self.doublecount_cb.isChecked()))
        self.elimination_cb.stateChanged.connect(
            lambda: self.elimination_gbox.setEnabled(self.elimination_cb.isChecked()))
        self.doublecount_gbox.setEnabled(self.doublecount_cb.isChecked())

        # to get input images

        self.fileopen_btn.clicked.connect(lambda: self.get_selected_images(isdir=False))
        self.opendir_btn.clicked.connect(lambda: self.get_selected_images(isdir=True))

        # no double counting if complete projection is selected
        self.stackallscans_rb.toggled.connect(self.set_double_counting_status)

        # to set output folder
        self.outputDir_btn.clicked.connect(self.set_output_directory)

        # open stats window
        self.actionOpen_Analysis_File.triggered.connect(self.open_analysis_file)

    def open_analysis_file(self):
        full_name = QFileDialog.getOpenFileName(self, "select analysis file", "*.txt")[0]
        if full_name:
            self.w = StatsWindow(parent=self)
            self.w.analysis_file = full_name  # it works
            self.w.run()

    def set_defaults(self):
        self.param = Parameters()
        self.output_lineEdit.setText(self.param.outputDir)

    def run_analyses(self):
        self.progressBar.setValue(0)
        if self.check_files():
            self.set_parameters()
            self.statusbar.showMessage("RUNNING")
            self.gui_enable_on_off()
            simulator.run_file_by_file_for_all_analysis(self.param, self.progressBar, self.status_infolbl)
            self.statusbar.showMessage("DONE")
            self.gui_enable_on_off()

    def set_parameters(self):
        # stacking
        if self.stack2by2.isChecked():
            self.param.stack_size = 2
        elif self.stack5by5.isChecked():
            self.param.stack_size = 5
        elif self.noprojection_rb.isChecked():
            self.param.stack_size = 1
        elif self.stackallscans_rb.isChecked():
            self.param.stack_size = 0

        # cellpose
        self.param.channels = [0, 3]  # TODO put option in gui and get
        if self.cyto_rb.isChecked():
            self.param.cp_model = 'cyto'
        elif self.cyto2_rb.isChecked():
            self.param.cp_model = 'cyto2'
        elif self.nuclei_rb.isChecked():
            self.param.cp_model = 'nuclei'
            self.param.channels = [0, 0]  # channels = [3,0] if you want to segment blue nuclei.

        self.param.flow_thresh = float(self.flow_tbox.text())
        self.param.mask_thresh = float(self.cellprob_tbox.text())

        # elimination and splitting
        self.param.intersect_thresh = float(self.intersect_tbox.text())

        # elimination and splitting
        self.param.intensity_thresh = float(self.intens_tbox.text())
        self.param.big_area_thresh = float(self.area_tbox.text())
        self.param.small_area_thresh = float(self.small_area_tbox.text())

        # rotation
        # degree 0: cv2.ROTATE_90_CLOCKWISE, 1: cv2.ROTATE_180, 2: 270, cv2.ROTATE_90_COUNTERCLOCKWISE
        # todo maybe add option for rotation on GUI
        # self.param.rotation = 0

        # output file and condition
        chn_text = "".join(str(p) for p in self.param.channels)
        self.param.condition = f"chan{chn_text}_flwThr{self.param.flow_thresh}_cllThr{self.param.mask_thresh}" \
                               f"_stck{self.param.stack_size}_model{self.param.cp_model}_rot{self.param.rotation}"
        self.param.outputFile = f"results_{self.param.condition}/"
        os.chdir(self.param.outputDir)
        utils.check_and_mkdir(self.param.outputFile)

        self.param.cp_orj_out = self.param.outputFile + "cp_orj_out/"
        self.param.cp_png_out = self.param.outputFile + "cp_png_out/"
        self.param.elim_out = self.param.outputFile + "e&s_out/" if self.elimination_cb.isChecked() else ""
        self.param.double_out = self.param.outputFile + "double_out/" if self.doublecount_cb.isChecked() else ""

        # print all parameters before starting analysis
        self.param.dump_vars()

    def set_double_counting_status(self):
        if self.sender().isChecked():  # it means self.stackallscans_rb.isChecked()
            self.doublecount_cb.setChecked(False)
            self.doublecount_cb.setEnabled(False)
        else:
            self.doublecount_cb.setEnabled(True)

    def update_info_on_gui(self, message, progress_value):
        self.status_infolbl.setText("INFO: %s \nProcessed File:\n%s" % (
            utils.get_formatted_datetime(), message))
        self.progressBar.setValue(progress_value)

        QApplication.processEvents()

    def update_status_bar(self, message):
        self.statusbar.showMessage(message)

    def parameters_enable_on_off(self):
        self.elimination_gbox.setEnabled(self.elimination_cb.isChecked())
        self.doublecount_gbox.setEnabled(self.doublecount_cb.isChecked())

    def get_selected_images(self, isdir):

        default_dir = os.getcwd()
        files = []
        if isdir is False:
            full_names = QFileDialog.getOpenFileNames(self, "select images", default_dir,
                                                      filter="Images (*,*.tiff *.tif)")[0]
            if full_names:
                files = sorted(full_names)
        else:

            dir_path = QFileDialog.getExistingDirectory(self, "select directory", default_dir,
                                                        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            # TODO include subdirectories according to checkbox on GUI
            if dir_path:
                files = [dir_path + '/' + f for f in sorted(listdir(dir_path)) if
                         (f.lower().endswith('.tif') or f.lower().endswith('.tiff')) is True]
        if len(files) > 0:
            # TODO add new files into existing list: what about for the images have ths same name
            self.param.filelist = files
            savedir = Path(files[0]).parent.absolute()  # go up a level to save in its own folder
            self.output_lineEdit.setText(savedir.as_posix())
            self.param.outputDir = self.output_lineEdit.text()

        self.show_file_number()

    def set_output_directory(self):
        new_output_file = QFileDialog.getExistingDirectory(self, "select directory", self.param.outputFile,
                                                           QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.output_lineEdit.setText(f'{new_output_file}')
        self.param.outputDir = self.output_lineEdit.text()

    def show_file_number(self):
        self.param.filenumber = len(self.param.filelist)
        self.filenr_infolabel.setText(f'Number of images to be processed: {self.param.filenumber}')

    def gui_enable_on_off(self):
        self.setEnabled(not self.isEnabled())

    def check_files(self):
        if self.param.filenumber == 0:
            QMessageBox.warning(self, "Select File", "Select at least one image")
            return False
        else:
            return True


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = main_window()
    window.show()
    try:
        app.exec_()
    except Exception as e:
        print(str(e))

