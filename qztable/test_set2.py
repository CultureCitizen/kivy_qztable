from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.anchorlayout import AnchorLayout #allows you to set the widgets at a fixed point
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from qztable import QzTable
import qz_cell_widgets as qzw
import pandas as pd
import numpy as np


"""
TestSet 1:
    Display a pandas0 frame
      Test spinner ( combo box)  - TESTED - OK
    Edit  a list
    Edit  a numpy array
    Test : setting the size of a ( column / row ) to 0 ( hide ) 
Bug Log

"""
class TestSet2Window(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tp_main = TabbedPanel()
        ti_pandas = TabbedPanelItem(id="ti_pandas", text = "pandas" )
        ti_list = TabbedPanelItem(id="ti_list", text = "list")
        ti_numpy = TabbedPanelItem(id="ti_numpy", text = "numpy array")

        self.qt_pandas = QzTable(id="qt_pandas")
        self.qt_list = QzTable(id="qt_list")
        self.qt_array = QzTable(id="qt_array")

        self.df_data = pd.read_csv("height_weight.csv")
        self.l_data = list()

        v = 10.0
        for y in range(1,1000,1):
            row = list()
            for x in range(0,50,1):
                v= v+ 10
                row.append(v)
            self.l_data.append(row)

        self.a_data = np.array(self.l_data)
        self.qt_pandas.data = self.df_data
        self.qt_pandas.row_header_width = 300
        self.qt_list.data = self.l_data
        self.qt_array.data = self.a_data

        #setup the pandas widgets
        spinner = qzw.CellSpinner(values=('1', '2') )
        spinner.background_color = (0.3,0.3,0.3,1)
        spinner.font_size = 12
        qzw.CellSpinnerOptions.BackgroundColor = (0.6,0.6,0.65,1)

        text = qzw.CellTxtInput( background_color = (0.3,0.3,0.3,1), font_size = 12 )
        text.halign = "right"
        self.qt_pandas.set_widgets({0:spinner,1:text})

        #Layout
        self.add_widget(self.tp_main)
        self.tp_main.add_widget(ti_pandas)
        ti_pandas.add_widget(self.qt_pandas)
        self.tp_main.add_widget(ti_list)
        ti_list.add_widget(self.qt_list)
        self.tp_main.add_widget(ti_numpy)
        ti_numpy.add_widget(self.qt_array)


class TestSet2App(App):
    def build(self):

        return TestSet2Window()

if __name__=='__main__':
    TestSet2App().run()
