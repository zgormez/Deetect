import os

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from PyQt5 import uic, QtGui, QtCore

import analysis.stats as st
import pandas as pd
import numpy as np


class StatsWindow(QMainWindow):
    """
    This "window" is a QMainWindow. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    analysis_file = ''
    df = None

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        uic.loadUi('stats_window_qt.ui', self)
        # self.parent.statusbar.showMessage("MESSAGE from child") #it works

        self.group_byname_rb.toggled.connect(lambda: self.grouping_checked(1))
        self.group_byselect_rb.toggled.connect(lambda: self.grouping_checked(0))
        # self.pushButton_selection.clicked.connect(self.move_selected_to_group2)
        self.pushButton_apply_grouping.clicked.connect(self.apply_grouping_pattern)
        self.pushButton_apply_grouping_folder.clicked.connect(self.apply_grouping_folder)
        self.pushButton_apply_stats.clicked.connect(self.apply_stats)
        self.pushButton_sum.clicked.connect(self.perform_sum_df)

    def apply_stats(self):
        base_path = os.path.dirname(self.analysis_file)
        test = 0
        if self.rbtest_mann.isChecked():
            test = 'Mann-Whitney'
        elif self.rbtest_rank.isChecked():
            test = 'Wilcoxon'
        elif self.rbtest_unpaired_ttest.isChecked():
            test = 't-test_paired'
        elif self.rbtest_paired_ttest.isChecked():
            test = 't-test_ind'

        graph_type = 'box'
        if self.rbtype_box.isChecked():
            graph_type = 'box'
        elif self.rbtype_violin.isChecked():
            graph_type = 'violin'

        try:
            # st.apply_stats_df(self.df, base_path, test, graph_type)
            st.seaborn_grouped_plot(self.df,base_path,  test, graph_type, hue='Group', sort=['Group'])
            self.statusbar.showMessage(f'{test} applied and written in {base_path}/stats.txt,'
                                       f' plot saved under {base_path}')
        except ValueError as ve:
            QMessageBox.warning(self, "Grouping", f' {str(ve)}')
        except Exception as e:
            print(e)

    def grouping_checked(self, i):
        self.stackedWidget.setCurrentIndex(i)

    def move_selected_to_group2(self):
        # sort rows in descending order in order to compensate shifting due to takeItem
        rows = sorted([index.row() for index in self.listWidget.selectedIndexes()], reverse=True)
        for row in rows:
            self.listWidget_2.addItem(self.listWidget.takeItem(row))
        self.listWidget_2.sortItems()

    def run(self):
        # read images and load them into list
        base_path = os.path.dirname(self.analysis_file)
        self.df = pd.read_csv(self.analysis_file, sep='\t')
        if 'Folder' not in self.df.columns:
            self.df.insert(loc=0, column='Folder', value='F1')
        self.df.insert(loc=0, column='Group', value='G1')
        self.populate_QlistWidget_with_folder()
        self.populate_QTableView()
        self.show()

    def populate_QTableView(self):
        model = PandasModel(self.df)
        self.tableView.setModel(model)
        size_df = self.df.groupby(['Group']).size().reset_index(name='counts')
        text = []
        for row in size_df.itertuples():
            text.append(f'{row[1]}: {row[2]}')

        self.label_grouping_info.setText(f'Number of images to be processed: {len(self.df)} ( {", ".join(text)} )')

    def apply_grouping_folder(self):
        if self.listWidget.currentItem() is not None:
            self.df['Group'] = np.where(self.df['Folder'].str.contains(self.listWidget.currentItem().text()),
                                        self.line_group_name_2.text(), self.df['Group'])
            self.populate_QTableView()
        else:
            QMessageBox.warning(self, 'Warning', "Select one folder then press apply!")

    def apply_grouping_pattern(self):
        self.df['Group'] = np.where(self.df['Image_name'].str.contains(self.line_pattern.text()),
                                    self.line_group_name.text(), self.df['Group'])
        self.populate_QTableView()

    def populate_QlistWidget_with_folder(self):

        image_list = self.df.iloc[:, 0].tolist()
        folder_list = self.df["Folder"].unique()
        for i in folder_list:
            QtWidgets.QListWidgetItem(i, self.listWidget)

    def perform_sum_df(self):
        if 'Parent_Image' in self.df.columns:
            df_sum = self.df.copy()
            params = {
                'Group': lambda x: ','.join(sorted(pd.Series.unique(x))),
                'Folder': lambda x: ','.join(sorted(pd.Series.unique(x)))
            }
            method_index = len(df_sum.columns) - 3
            for method in df_sum.columns[method_index:]:
                params.update({method: 'sum'})

            df_sum = df_sum.groupby('Parent_Image').agg(params).reset_index()
            df_sum.rename(columns={'Parent_Image': 'Image_name'}, inplace=True)
            df_sum.insert(2, 'Image_name', df_sum.pop('Image_name'))

            self.df = df_sum
            self.populate_QTableView()
        else:
            QMessageBox.warning(self, 'Warning', "Summing is already performed!")


class PandasModel(QtGui.QStandardItemModel):
    def __init__(self, data, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._data = data
        for row in data.values.tolist():
            data_row = [QtGui.QStandardItem("{}".format(x)) for x in row]
            self.appendRow(data_row)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[x]
        return None


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    w = StatsWindow()
    w.analysis_file = r"sample_data\stats_in_paper\number_of_cell_ALL_sets_folder_parent.txt"
    w.run()

    try:
        app.exec_()
    except Exception as e:
        print(e)
    except:
        print("Unexpected error:", sys.exc_info()[0])
