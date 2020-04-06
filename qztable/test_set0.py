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
from kivy.uix.gridlayout import GridLayout

from qztable import QzTable
from qzutils import Gui

import pandas as pd
import qz_cell_widgets as qzw

class Window(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.button = Button( size_hint_y = None, height = 30 , text= "button 1")
        self.add_widget(self.button)

        self.button = Button( size_hint_y = None, height = 30 , text= "button 2")
        self.add_widget(self.button)

        self.button3 = Button( size_hint_y = None, height = 17 , text = "button 3")
        self.button3.size_hint_min= (None, None)
        self.add_widget(self.button3)

        df = pd.read_csv("data.csv")
        self.table = QzTable(size_hint = (None,None), height = 500,width = 500)
        self.table.data = df
        self.table.set_widgets({1: qzw.CellTxtInput(background_color = (0.5,0.5,1,1) ,font_size = 12 ) })

        print("data assigned")
        self.add_widget(self.table)
        self.button = Button( size_hint_y = None, height = 5 , text= "button 4")
        self.add_widget(self.button)

        self.button = Button( size_hint_y = None, height = 30 , text= "button 5")
        self.add_widget(self.button)


class App(App):
    def build(self):
        return Window()

if __name__=='__main__':
    App().run()
