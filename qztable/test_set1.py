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
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from qztable import QzTable
import pandas as pd
import numpy as np


"""
TestSet 1:
    Display a pandas frame
    Display an list
    Display a numpy array
Bug Log
    When there is not enough space to display the last row / column the result is ... weird:
        The cell overlaps with the previous cell - FIXED
        
"""

class TestSet1Window(BoxLayout):
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
        self.qt_list.data = self.l_data
        self.qt_array.data = self.a_data

        #Layout
        self.add_widget(self.tp_main)
        self.tp_main.add_widget(ti_pandas)
        ti_pandas.add_widget(self.qt_pandas)
        self.tp_main.add_widget(ti_list)
        ti_list.add_widget(self.qt_list)
        self.tp_main.add_widget(ti_numpy)
        ti_numpy.add_widget(self.qt_array)


class TestSet1App(App):
    def build(self):

        return TestSet1Window()

if __name__=='__main__':
    TestSet1App().run()
