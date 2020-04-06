"""
Set 3
    Virtual Rows and Row Widgets
    virtual mode with a list of objects
    Table Model : heat map
    zero column width
"""
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
from qztable import QzTable , TableModel
import qz_cell_widgets as qzw
from qzutils import KeyTracker
import pandas as pd
import numpy as np
import csv
from datetime import datetime

class Person(TableModel):
    columns =['first_name','last_name','birth_date']
    types=[str,str,datetime]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_name = ""
        self.last_name = ""
        self.birth_date = None
        for k,v in kwargs.items():
            setattr(self,k,v)


#Implement the table model
class Heatmap(TableModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = None
        self.low =  0
        self.high = 0

    def get_types(self):
        return[float] * self.get_columns()

    def get_rows(self):
        return self.grid.shape[0]

    def get_columns(self):
        return self.grid.shape[1]

    #Create a grid with a binomial gausian distribution
    #it look cool when colored
    def create_grid(self,rows,cols)->np.ndarray:
        x, y = np.meshgrid(np.linspace(-1,1,rows), np.linspace(-1,1,cols))
        d = np.sqrt(x*x+y*y)
        sigma, mu = 1.0, 0.0
        g = np.exp(-( (d-mu)**2 / ( 2.0 * sigma**2 ) ) )
        self.grid =g
        self.low = self.grid.min()
        self.high = self.grid.max()

    def set_widget_color(self,widget):
        v = widget.value
        g = ((v- self.low) / ( self.high - self.low))
        widget.background_color = (0,g,0.2,1)

    #Fill the widget with the values from the model
    def set_widget_value(self,table,widget,row,col):
        if isinstance(widget,qzw.CellTxtInput):
            value = self.grid[row,col]
            widget.text = "{:.3f}".format(value)
            widget.value = value
            self.set_widget_color(widget)

    """ moves the value from the widget into the data model
        ... or not if it is an invalid value
    """
    def set_model_value(self,table,row,col,widget):
        if isinstance(widget,qzw.CellTxtInput):
            widget.value = float(widget.text)
            self.grid[row,col] = widget.value
            self.set_widget_color(widget)

class TestSet3Window(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kt = KeyTracker()

        self.tp_main = TabbedPanel()
        ti_vrow = TabbedPanelItem(id="ti_pandas", text = "pandas" )
        ti_virtual = TabbedPanelItem(id="ti_list", text = "list")
        ti_hmap = TabbedPanelItem(id="ti_hmap", text = "heatmap")

        #
        self.qt_vrow = QzTable(id="qt_pandas")
        self.qt_virtual = QzTable(id="qt_list")
        self.qt_hmap = QzTable(id="qt_hmap")

        #---------------------------------------------------------------------------
        #virtua row demo
        self.df_data = pd.read_csv("height_weight.csv")
        self.qt_vrow.data = self.df_data
        self.qt_vrow.virtual_rows = 2
        self.sort_cols = list()
        self.sort_mode = list()
        self.sort_count = 0

        #create the spin button for sorting in ascending or descending ordr
        spn_sort  = qzw.CellSpinner(values=('','asc', 'desc'), background_color = (0.5,0.5,0.55,1), font_size = 12 )
        #create the button that indicates the column sort order
        btn_order = qzw.CellButton(text = "" )
        qzw.CellSpinnerOptions.BackgroundColor = (0.6,0.6,0.65,1)

        self.qt_vrow.set_row_widgets(0,spn_sort)
        self.qt_vrow.set_row_widgets(1,btn_order)
        self.qt_vrow.bind(on_value_changed=self.on_value_changed)
        self.qt_vrow.bind(on_get_value=self.on_get_value)
        self.qt_vrow.fixed_rows = 2

        #---------------------------------------------------------------------------
        #virtual mode demo
        self.l_person = self.read_persons()
        self.qt_virtual.virtual = True
        self.qt_virtual.data = self.l_person
        self.qt_virtual.set_types(Person.types)
        self.qt_virtual.bind(on_value_changed=self.qt_virtual_on_value_changed)
        self.qt_virtual.bind(on_get_value=self.qt_virtual_on_get_value)
        self.qt_virtual.grid_cols = 3
        self.qt_virtual.grid_rows = len(self.l_person)

        #---------------------------------------------------------------------------
        #Table model demo
        self.grid_data = Heatmap()
        self.grid_data.create_grid(20,20)
        self.qt_hmap.data = self.grid_data
        c = self.grid_data.get_columns()
        self.qt_hmap.set_col_widths( [50]* c)
        txt = qzw.CellTxtInput()
        txt.multiline = False
        #allow only numbers in the text input
        txt.input_type = "number"
        txt.background_color = (1,1,1,1)
        txt.foreground_color = (1,1,1,1)
        self.qt_hmap.set_widgets([txt]*c )
        btn_refresh = Button(text="Refresh")

        #Layout
        self.add_widget(self.tp_main)
        self.tp_main.add_widget(ti_vrow)
        ti_vrow.add_widget(self.qt_vrow)
        self.tp_main.add_widget(ti_virtual)
        ti_virtual.add_widget(self.qt_virtual)
        self.tp_main.add_widget(ti_hmap)
        ti_hmap.add_widget(self.qt_hmap)


    #-------------------------------------------------------------------------
    #Methods for virual rows
    #-------------------------------------------------------------------------
    def clear_sort(self):
        cols = len(self.df_data.columns)
        self.sort_cols.clear()
        self.sort_mode.clear()


    def on_get_value(self,instance,widget,col,row):
        if row in [0,1]:
            if col in self.sort_cols:
                idx = self.sort_cols.index(col)
                mode = self.sort_mode[idx]
                if row == 0:
                    widget.set_value(mode)
                if row == 1:
                    widget.set_value(str(idx))

    def on_value_changed(self,instance,col,row,value):
        self.qt_virtual.grid_to_model(col,row,value)
        #the combo box
        if row == 0:
            #Clear the list if it is not pressed
            if not KeyTracker.SHIFT in self.kt.keys:
                self.clear_sort()

            if value == "":
                if col in self.sort_cols:
                    idx = self.sort_cols.index(col)
                    self.sort_cols.remove(col)
                    del self.sort_mode[idx]
            else:
                if col in self.sort_cols:
                    idx = self.sort_cols.index(col)
                    self.sort_mode[idx] = value
                else:
                    self.sort_mode.append(value)
                    self.sort_cols.append(col)
                self.sort_count = self.sort_count + 1
            #prepare for sorting
            l_names = list()
            l_asc = list()
            for idx,mode in zip(self.sort_cols,self.sort_mode):
                name = self.df_data.columns[idx]
                l_names.append(name)
                if mode == "asc":
                    l_asc.append(True)
                else:
                    l_asc.append(False)
            #sort dataframe
            if len(l_names) > 0:
                self.df_data.sort_values(l_names,axis=0,ascending = l_asc, inplace = True)
                self.qt_vrow.redraw(-1,-1)

    #-------------------------------------------------------------------------
    #Methods for virual mode
    #-------------------------------------------------------------------------
    def read_persons(self)->list:
        l = list()
        f = open("persons.csv","r")
        while True:
            line = f.readline()
            if not line:
                break
            reader = csv.reader([line], delimiter=',')
            items = list(reader)[0]
            p = Person()
            p.first_name = items[0]
            p.last_name = items[1]
            p.birth_date = datetime.strptime(items[2], "%d/%m/%Y")
            l.append(p)
        return l

    #update the model
    def qt_virtual_on_value_changed(self,instance,col,row,value):
        # get the person object
        p = self.l_person[row]
        field = Person.columns[col]
        value = instance.get_value()
        setattr(p,field,value)

    #update the widget value
    def qt_virtual_on_get_value(self,instance,widget,col,row):
        obj = self.l_person[row]
        field = Person.columns[col]
        value = getattr(obj,field)
        widget.set_value(str(value))

class TestSet3App(App):
    def build(self):

        return TestSet3Window()

if __name__=='__main__':
    TestSet3App().run()
