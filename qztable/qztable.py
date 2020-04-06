"""
    Table widget for kivy
    Author : Armando de la Torre
    First Beta Release : April-2020 : Year of the Coronavirus
    Version 0.9-beta1 05-04-2020
"""
import numpy as np
import pandas as pd
import csv
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
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
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.splitter import Splitter
from kivy.uix.slider import Slider
from kivy.properties import ListProperty
from kivy.event import EventDispatcher
from kivy.uix.relativelayout import RelativeLayout
from qzutils import Gui
from itertools import chain
import qz_cell_widgets as qzw
from typing import Dict, Sequence , TypeVar, Iterable, Tuple, Union
from qz_scroll_bar import QzScrollBar



class TableModel(object):
    def __init__(self, **kwargs):
        super(TableModel, self).__init__(**kwargs)

    """
        returns the number of data rows
    """
    def get_rows(self):
        return 0

    """ returns the number of columns
    """
    def get_columns(self):
        return 0

    def get_types(self):
        return []
    """ moves the value from the data model into the widget
    """
    def set_widget_value(self,table,widget,row,col):
        pass

    """ moves the value from the widget into the data model
        ... or not if it is an invalid value
    """
    def set_model_value(self,table,widget,row,col):
        pass


"""
    Helper class : represents a cell in the grid
"""

class SizeButton(ToggleButton):
    def __init__(self, **kwargs):
        super(SizeButton,self).__init__(**kwargs)
        self.old_state = self.state
        self._down = False
        self._down_x = 0
        self._down_y = 0
        self._up_x = 0
        self._up_y = 0

        self.horiz = False
        self.vert = True

        self.bind(on_touch_down=self.on_touch_down_evt)
        self.bind(on_touch_move=self.on_touch_move_evt)
        self.bind(on_touch_up=self.on_touch_up_evt)

    def on_touch_down_evt(self,inst, touch):
        if self.collide_point(*touch.pos):
            #@debug
            #print(self,inst)
            if self._down == False:
                self._down = True
                self._down_x = touch.pos[0]
                self._down_y = touch.pos[1]
                Window.set_system_cursor("crosshair")

    def on_touch_move_evt(self,inst,touch):
        pass

    def on_touch_up_evt(self,inst, touch):
        if self._down == True:
            Window.set_system_cursor("arrow")
            self._down = False
            self._up_x = touch.pos[0]
            self._up_y = touch.pos[1]
            dx = self._up_x - self._down_x
            dy = self._down_y - self._up_y
            #This was a resizing operation revert the button state
            if abs(dx) > 2 or abs(dy) > 2:
                self.state = self.old_state
            if self.horiz == True:
                new_w = self.width +dx
                if new_w < 10:
                    new_w = 10
                self.width = new_w
            if self.vert == True:
                new_h = self.height + dy
                if new_h < 10 :
                    new_h = 10
                self.height = new_h

class QzTable(Widget):
    g_min_size_x:int = 25
    g_min_size_y:int = 15

    def __init__(self, **kwargs):
        super(QzTable, self).__init__(**kwargs)
        self._debug = False
        self._first = False
        self.size_hint_min_x = 75
        self.size_hint_min_y = 75
        #------------------------------------------------
        #EVENTS
        #------------------------------------------------
        self.register_event_type('on_init_widget_event')
        self.register_event_type('on_cell_clicked_event')
        self.register_event_type('on_get_value')
        self.register_event_type('on_set_value')
        self.register_event_type('on_value_changed')
        #------------------------------------------------
        #HELPERS
        #------------------------------------------------
        self._dy:int = 0    #height after resizing
        self._dx:int = 0     #width after resizing
        self._top:int = 0       #top row displayed in the grid
        self._left:int = 0      #left col displayed in the grid
        self._bottom:int = 0    #bottom column displayed completely
        self._right:int = 0     #right column displayed completely
        self._col_idx = dict()
        self._row_idx = dict()
        #------------------------------------------------
        #PROPERTIES
        #------------------------------------------------
        self.multiple_col_selection = True
        self.multiple_row_selection = True
        self._slider_width:int     = 35
        self._col_header_height    = 25     #column header height
        self._row_header_width     = 50     #row header width
        self.default_row_height    = 25     #Default row height
        self.default_col_width     = 100    #Default column width
        self.show_row_number       = True   #Show row numbers in the row headers
        self.show_col_number       = True   #show the column number in the column header
        self._focus_col = -1          #selected column+
        self._focus_row = -1          #selected row+
        self._grid_cols:int = 1         #Number of grid columns+
        self._grid_rows:int = 1         #Number of grid rows+
        self._fixed_cols:int = 0        #Number of fixed columns+
        self._fixed_rows:int = 0        #Number of fixed rows
        self._virtual_rows = 0          #rows in which data is accessed from other source

        self._col_widgets = list()  #widgets used for the columns
        self._row_widgets = dict()  #dictionary of list
        self._col_headers = list()  #column text headers
        self._col_widths = list()   #column widths
        self._sel_cols = list()     #selected columns
        self._col_types = list()    #column types

        self._row_heights = list()  #row heights
        self._sel_rows = list()     #selected rows
        self._row_headers = list()  #row headers

        self._data = None           #Data for the table. It may be
        self._virtual = False        #virtual mode
        self._allow_col_sizing  = True # Allow column sizing
        self._allow_row_sizing  = True # Allow row sizing

        self._grid_cols = 1
        self._grid_rows = 1
        self.font_size = 12

        #------------------------------------------------
        #LAYOUT
        #------------------------------------------------
        #set the vertical slider

        self._hslider = QzScrollBar(orientation = "horizontal", low_value = 0, high_value = self.grid_cols,
                                    base_value = 0, range = 1 )
        self._hslider.size_hint_y = None
        self._hslider.height =  self._slider_width

        self._hslider.bind(on_value_changed=self.handle_hscroll_value_changed)

        self._vslider = QzScrollBar(orientation = "vertical", low_value = 0, high_value = self.grid_cols,
                                    base_value = 0,  range = 1)
        self._vslider.size_hint_x = None
        self._vslider.width = self._slider_width

        self._vslider.bind(on_value_changed=self.handle_vscroll_value_changed)


        """
        self._hslider = Slider(min=0, max=self._grid_cols, value=0,step = 1,
                               orientation ="horizontal", size_hint =( None,None) ,height =  self._slider_width,
                               value_track = True )

        self._hslider.bind(on_touch_up = self.handle_hscroll_touch_up)

        #set the horizontal slider
        self._vslider = Slider(min=0, max=self._grid_rows, value=0,step = 1,
                               orientation ="vertical", size_hint = (None,None), width = self._slider_width,
                               value_track = True)
        self._vslider.bind(on_touch_up = self.handle_vscroll_touch_up)
        """

        self._root_gb = GridLayout(cols = 2)                          #contains table and sliders
        self._table_vb = RelativeLayout()          #column header + body

        self._btn_corner = None # the corner button
        #Add the root widget
        self.add_widget(self._root_gb)
        #table and sliders
        self._root_gb.add_widget(self._table_vb)
        self._root_gb.add_widget(self._vslider)
        self._root_gb.add_widget(self._hslider)
        self.resize_widgets(self.width,self.height)

        self.bind(size=self.update_layout)
        self.bind(pos=self.update_position)


    """
    "   Widget layout / rendering 
    """
    def resize_widgets(self,dx,dy):
        if self.parent != None:
            self._root_gb.pos = self.pos
            self._root_gb.size_hint = (None,None)
            self._root_gb.width = dx
            self._root_gb.height = dy

            self._table_vb.size_hint = (None,None)
            self._table_vb.height = dy - self._slider_width
            self._table_vb.width = dx - self._slider_width
            self._hslider.width = self._table_vb.width
            self._vslider.height = self._table_vb.height

    """
    " Internal use only : print debug information in console
    """
    def info(self,*args):
        if self._debug:
            print(args)

    def update_position(self,*args):
        self.resize_widgets(self.width,self.height)
        if self._first == False:
            self._first = True
            self.redraw(self.width,self.height)

    def update_size(self,rows:int,cols:int):
        self.grid_cols = cols
        self.grid_rows = rows
        if self._left >= self.grid_cols:
            self._left = self.grid_cols - 1
        if self.top >= self.grid_rows:
            self._top = self.grid_rows - 1

    def update_layout(self,*args):
        self.redraw(self.width,self.height)

    """
    "
    """
    def calc_col_header_width(self,dx,dy):
        return dx - self._slider_width

    def calc_body_width(self,dx,dy):
        return dx - self._slider_width - self.row_header_width

    def calc_row_header_height(self,dx,dy):
        return dy - self._slider_width - self.col_header_height


    def redraw(self,dx,dy):
        if dx < 0 :
            dx = self.width
        if dy < 0 :
            dy = self.height
        self.resize_widgets(dx,dy)
        if self.parent != None:
            self._dx = dx
            self._dy = dy
            self._table_vb.clear_widgets()
            self.draw_col_header(dx,dy)
            self.draw_row_header(dx,dy)
            self.update_headers_state(self._col_idx,self._row_idx)
            self.draw_cells(dx,dy)
            self._update_hscroll_new()
            self._update_vscroll_new()

    def draw_col_header(self,dx,dy):
        self._col_idx.clear()
        w = self.calc_col_header_width(dx,dy)

        #self._col_header_hb.height = self.col_header_height
        y = self.calc_row_header_height(dx,dy)

        self._btn_corner = Button()
        self._btn_corner.size_hint = (None,None)
        self._btn_corner.height = self.col_header_height
        self._btn_corner.width = self.row_header_width
        self._table_vb.add_widget(self._btn_corner)
        self._btn_corner.pos = (0,y)

        x = self.row_header_width
        l_cols = list(chain(range(0,self._fixed_cols,1), range(self._left,self._grid_cols)))
        for i in l_cols:
            cw = self._col_widths[i]
            self._right = i
            max = w - x
            if max <= self.g_min_size_x :
                self._right = i - 1
                break
            if cw > max:
                cw = max
            btn = self.create_col_header_cell(x,y,cw,i)
            self._table_vb.add_widget(btn)
            self._col_idx[btn.column] = btn
            x = x + cw

    """
        x = x position 
        cw = column width 
        i = data column index 
    """
    def create_col_header_cell(self,x,y,cw,i):
        tbtn = SizeButton(text = "" , font_size = self.font_size )
        if self.show_col_number:
            tbtn.text = str(i) +" : "+ self._col_headers[i]
        else:
            tbtn.text = self._col_headers[i]

        tbtn.pos = (x,y)
        tbtn.size_hint_x = None
        tbtn.size_hint_y = None
        tbtn.height = self._col_header_height
        tbtn.horiz = True
        tbtn.vert = False
        tbtn.width = cw
        tbtn.column = i
        tbtn.row = -1
        tbtn.state = "normal"
        tbtn.bind(on_release=self.handle_col_btn_release)
        tbtn.bind(size=self.handle_col_resize)
        return tbtn

    def get_col_widget(self,col):
        if col >= self._left and col <= self._right:
            for split in self._col_header_hb.children:
                if split.column == col:
                    return split.children[0]
        else:
            return None
        return None

    def get_row_widget(self,row):
        if row >= self._left and row <= self._right:
            for split in self._col_header_hb.children:
                if split.row == row:
                    return split.children[0]
        else:
            return None
        return None

    def draw_row_header(self,dx,dy):
        h = self.calc_row_header_height(dx,dy)
        y = 0          #y top to bottom

        self._row_idx.clear()
        l_rows = list(chain(range(0,self._fixed_rows,1),range(self._top,self._grid_rows,1)))

        for i in l_rows:
            rh = self._row_heights[i]
            self._bottom = i
            max = h - y
            if max <= self.g_min_size_y :
                self._bottom = i -1
                break
            if rh > max:
                rh = max
            btn = self.create_row_header_cell( (h-y) - rh , rh,i)
            self._table_vb.add_widget(btn)
            self._row_idx[btn.column] = btn
            y = y + rh

    """
    "  y = y bottom up position of the cell
    "  rh = row height
    "  i = row number of the data 
    """
    def create_row_header_cell(self,y,rh,i):

        tbtn = SizeButton(text = "" )
        tbtn.font_size = 12
        tbtn.pos = (0,y)
        if self.show_row_number:
            tbtn.text = str(i) +":"+self._row_headers[i]
        else:
            tbtn.text =self._row_headers[i]
        tbtn.size_hint_x = None
        tbtn.size_hint_y = None
        tbtn.width = self.row_header_width
        tbtn.height = rh

        tbtn.column = -1
        tbtn.row = i
        tbtn.bind(on_release=self.handle_row_btn_release)
        tbtn.bind(size=self.handle_row_resize)

        return tbtn

    """
    " Draw the cells in the body of the table 
    """
    def draw_cells(self,dx,dy):

        lh = self.calc_row_header_height(dx,dy)
        lw = self.calc_col_header_width(dx,dy)
        #for each row
        y = 0
        draw_top = self._top
        if draw_top < self.fixed_rows:
            draw_top = self.fixed_rows
        draw_left = self._left
        if draw_left < self._fixed_cols:
            draw_left = self.fixed_rows

        l_rows = list(chain(range(0,self._fixed_rows,1),range(draw_top,self._grid_rows,1)))
        l_cols = list(chain(range(0,self._fixed_cols,1),range(draw_left,self._grid_cols,1)))
        for row in l_rows:
            maxy = lh - y
            #No more space for rows
            if maxy <= self.g_min_size_y :
                break
            cy = self._row_heights[row]
            if cy > maxy:
                cy = maxy
            x = self._row_header_width
            for col in l_cols:
                maxx = lw - x
                cx = self._col_widths[col]
                if cx > 0:
                    #get the widget template
                    ww  = self.get_widget_template(row,col)
                    if maxx <= self.g_min_size_x :
                        break
                    if cx > maxx:
                        cx = maxx
                    wid:Widget =  self.create_cell_widget(ww,x, (lh-y)-cy, cx,cy,col,row)
                    self._table_vb.add_widget(wid)
                x = x + cx
            y = y + cy

    def get_widget_template(self,grid_row,grid_col)->object:
        #No widget found at row level : use the column widget
        if not grid_row in self._row_widgets:
            ww = self._col_widgets[grid_col]
            return ww
        #row found Use the row widget
        else:
            wrow = self._row_widgets[grid_row]
            return wrow[grid_col]

    """""
        wtemplate: the template used to set the widget properties
        x : x relative position
        y : y relative position in widget 
        dx : width 
        dy : height
        cx : column
        cy : row
    """
    def create_cell_widget(self, wtemplate,x,y, dx, dy, cx, cy):
        virtual : bool = False
        model :bool = False
        wclass = qzw.get_widget_class(wtemplate)

        NewWidget = type('NewWidget', (type(wtemplate),), {})
        new_w = NewWidget()
        Gui.clone_widget(wtemplate,new_w)

        new_w.size_hint = (None,None)
        new_w.pos = (x,y)
        new_w.width = dx
        new_w.height = dy
        new_w.grid_x = cx
        new_w.grid_y = cy

        #the event handler has to set the value
        if self._virtual:
            self.trigger_get_value(new_w,cx,cy)
            virtual = True
        else:
            if self.virtual_rows > 0:
                if cy < self.virtual_rows:
                    virtual = True
                    self.trigger_get_value(new_w,cx,cy)
            if not self.data is None:
                if cy >= self.virtual_rows:
                    if isinstance(self.data,pd.DataFrame):
                        value = self.data.iloc[cy-self.virtual_rows,cx]
                    elif isinstance(self.data,list):
                        value = self.data[cy-self.virtual_rows][cx]
                    elif isinstance(self.data,np.ndarray):
                        value = self.data[cy-self.virtual_rows,cx]
                    elif isinstance(self.data,TableModel):
                        value = self.data.set_widget_value(self,new_w,cy,cx)
                        model = True
        #raise the widget initialization event
        #@widget.event
        self.trigger_init_widget_event(new_w,cx,cy)
        #bind the touch event
        if hasattr(new_w,"touch_up"):
            #@widget.event
            new_w.bind(on_touch_up=self.handle_touch_up)

        if virtual == False and model == False:
            #this is not a cell widget
            if wclass == "":
                #if it has a text attribute set the value to the text
                if hasattr(wtemplate,"text"):
                    new_w.text = str(value)
                else:
                    pass
            else:
                if wclass != "":
                    new_w.set_value(str(value))
        #bind value change
        if wclass == "rw":
            #@widget.event
            new_w.on_value_changed=lambda value : self.trigger_value_changed(new_w,value)
        return new_w

    """----------------------------------------------------------------------------
    "   Internal event handlers 
    ----------------------------------------------------------------------------"""
    def handle_touch_up(self,instance,touch):
        #check that the touch event occured in this widget
        if instance.collide_point(*touch.pos):
            self._focus_col = instance.grid_x
            self._focus_row = instance.grid_y
            self.trigger_cell_clicked_event(instance,instance.grid_x,instance.grid_y)
            return True

    """
    " Internal handler for column selection
    """
    def handle_col_btn_release(self,instance,*args):
        col = instance.column
        if instance.state == "down":
            self._sel_cols[col] = 1
        else:
            self._sel_cols[col] = 0
        if self.multiple_col_selection == False:
            self.clear_col_selection(skip=col)
            self._update_col_sel_widgets()
    """
    " Internal handler for column resize
    """
    def handle_col_resize(self,instance,*args):
        if self.parent != None:
            column = instance.column
            if self._col_widths[column] != int(instance.width):
                self._col_widths[column] = int(instance.width)
                self.redraw(self.width,self.height)

    """
    " Internal handler for row resize
    """
    def handle_row_resize(self,instance,*args):
        if self.parent != None:
            row = instance.row
            if self._row_heights[row] != int(instance.height):
                self._row_heights[row] = int(instance.height)
                self.redraw(self.width,self.height)

    """
    " Internal handler for row selection
    """
    def handle_row_btn_release(self,instance,*args):
        row = instance.row
        if instance.state =="down":
            self._sel_rows[row] = 1
        else:
            self._sel_rows[row] = 0
        if self.multiple_row_selection == False:
            self.clear_row_selection(skip=row)
            self._update_row_sel_widgets()

    """
    "  single column selection mode
    """
    def clear_column_selection(self,skip:int=-1):
        if skip >= 0:
            for i in range(0,len(self._sel_cols)):
                if i != skip:
                    self._sel_cols[i] = 0
        else:
            for i in range(0,len(self._sel_cols)):
                self._sel_cols[i] = 0

    """
    " clear row selection 
    " skip : do not de-select this row
    """
    def clear_row_selection(self,skip:int=-1):
        if skip >= 0:
            for i in range(0,len(self._sel_rows)):
                if i!=skip:
                    self._sel_rows[i] = 0
        else:
            for i in range(0,len(self._sel_cols)):
                self._sel_cols[i] = 0

    """
    "  Update the header state after redraw
    """
    def update_headers_state(self,col_idx:dict,row_idx:dict):
        for idx in col_idx:
            btn = col_idx[idx]
            if self._sel_cols[idx] == 1:
                btn.state = "down"
            else:
                btn.state = "normal"
            btn.text = self._col_headers[idx]

        for idx in row_idx:
            btn = row_idx[idx]
            if self._sel_rows[idx] == 1:
                btn.state = "down"
            else:
                btn.state = "normal"


    """
    " Obtain the widget for column i 
    """
    def get_col_widget(self,i):
        if i in self._col_idx:
            return self._col_idx[i]
        else:
            return None

    """
    " Obtain the widget for row i
    """
    def get_row_widget(self,i):
        if i in self._row_idx:
            return self._row_idx[i]
        else:
            return None

    """
    " Updatee the grid view after the horizontal scroll is changed
    """
    def handle_hscroll_touch_up(self,instance,touch):
        if instance.collide_point(*touch.pos):
            v = instance.value
            r  = self._calculate_right()
            if v != self._left or r != self._right:
                self._left = int(v)
                self._right = int(r)
                self.redraw(self.width, self.height)

    """
    " Update the grid view after the vertical scroll is changed
    """
    def handle_vscroll_touch_up(self,instance,touch):
        if instance.collide_point(*touch.pos):
            v = abs(instance.value)
            b = self._calculate_bottom()
            if v != self._top or b != self._bottom:
                self._top = int(v)
                self._bottom = int(b)
                self.redraw(self.width, self.height)

    """
    " Updatee the grid view after the horizontal scroll is changed
    """
    def handle_hscroll_value_changed(self,instance,value):
        v = instance.base_value
        r = self._calculate_right1() #the scroll didn't move, the grid was resized
        instance.range = (r - self._left ) +1
        if v != self._left or r != self._right:
            self._left = int(v)
            self.redraw(self.width, self.height)
            #adjust the slider range
            instance.range = ( self._right - self._left) +1

    def handle_vscroll_value_changed(self,instance,value):
        v = instance.base_value
        b = self._calculate_bottom1() # the scroll didn't move, the grid was resized
        instance.range = (b - self._top ) +1
        if v != self._top or b != self._bottom:
            self._top = int(v)
            self._bottom = int(b)
            self.redraw(self.width, self.height)
            instance.range = ( self._bottom - self._top )+1

    """
    "   Event definition
    """
    def trigger_init_widget_event(self, *args):
        widget = args[0]
        x = args[1]
        y = args[2]
        self.dispatch('on_init_widget_event', widget,x,y)

    def trigger_cell_clicked_event(self,*args):
        widget = args[0]
        column = args[1]
        row = args[2]
        self.dispatch('on_cell_clicked_event',widget,column,row)

    def trigger_get_value(self, widget,column , row):
        self.dispatch('on_get_value',widget,column,row)

    def trigger_set_value(self,*args):
        widget = args[0]
        value = args[1]
        column = args[2]
        row = args[3]
        self.dispatch('on_set_value',widget,value,column,row)

    def trigger_value_changed(self, widget,value):
        wclass = qzw.get_widget_class(widget)
        if wclass != "":
            col = widget.grid_x
            row = widget.grid_y
        else:
            col = self.focus_col
            row = self.focus_row
        self.dispatch('on_value_changed',col,row,value,widget)

    #-----------------------------------------------------------------
    #3 define the signature of the events
    def on_init_widget_event(self,widget,x,y):
        pass

    def on_cell_clicked_event(self,widget,x,y):
        pass

    def on_get_value(self,widget,column,row):
        return ""

    def on_get_data(self,column,row):
        return ""

    def on_set_value(self,widget,value,column,row):
        pass

    def on_value_changed(self,col,row,value,widget):
        self.grid_to_model(col,row,value,widget)

    """ Helper method:
        Pass the grid widget values to the data structure
    """
    def grid_to_model(self,col,row,value,widget):
        if self.virtual:
            pass
        else:
            if row >= self.virtual_rows:

                if isinstance(self.data,pd.DataFrame):
                    tt = self._col_types[col]
                    type_value = qzw.convert_to_type(value,tt)
                    self.data.iloc[row - self.virtual_rows,col] = type_value

                elif isinstance(self.data,list):
                    tt = self._col_types[col]
                    type_value = qzw.convert_to_type(value,tt)
                    row = self.data[row -self.virtual_rows ]
                    #only if it is a list of lists
                    if isinstance(row,list):
                        self.data[row -self.virtual_rows ][col] = type_value
                elif isinstance(self.data,np.ndarray):
                    tt = self._col_types[col]
                    type_value = qzw.convert_to_type(value,tt)
                    self.data[row-self.virtual_rows,col] = type_value
                elif isinstance(self.data,TableModel):
                    self.data.set_model_value(self,row,col,widget)

    """
    "HELPER FUNCTIONS
    """

    """
    " Obtain the right-most column being displayed
    """
    #@clean
    def _calculate_right(self)->int:
        right = 0
        for key in self._col_idx:
            btn = self._col_idx[key]
            if btn.column > right:
                right = btn.column
        return int(right)

    """
    " Obtain the bottom-most row being displayed
    """
    #@clean
    def _calculate_bottom(self):
        bottom = 0
        for key in self._row_idx:
            btn = self._row_idx[key]
            if btn.row > bottom:
                bottom = btn.row
        return int(bottom)

    def _calculate_right1(self)->int:
        right = 0
        w = 0
        maxw = self.calc_col_header_width(self.width,self.height)
        for i in range(self._left , self.grid_cols,1):
            w = w + self._col_widths[i]
            right = i
            if w > maxw:
                right = right -1
                break
        return right

    def _calculate_bottom1(self)->int:
        bottom = 0
        h = 0
        maxh = self.calc_row_header_height(self.width,self.height)
        for i in range(self._top,self.grid_rows,1):
            h = h + self._row_heights[i]
            bottom = i
            if h > maxh:
                bottom = bottom - 1
                break
        return bottom

    def _update_hscroll_new(self):
        #@clean
        if isinstance(self._hslider,QzScrollBar):
            self._hslider.low_value = 0
            self._hslider.high_value = self.grid_cols
            self._hslider.range = int(self._right - self._left)+1
            max = self.grid_rows - self._vslider.range
            if self._hslider.base_value > max:
                self._hslider.base_value = max

    def _update_vscroll_new(self):
        #@clean
        if isinstance(self._vslider,QzScrollBar):
            self._vslider.low_value = 0
            self._vslider.high_value = self.grid_rows
            self._vslider.range = int(self._bottom - self._top ) +1
            max = self.grid_rows - self._vslider.range
            if self._vslider.base_value > max:
                self._vslider.base_value = max


    def _check_list(self,l,axis):
        if axis == "c":
            if len(l) != self.grid_cols:
                raise Exception("list must match the number of columns : " +self.grid_cols)
        elif axis == "r":
            if len(l) != self.grid_rows:
                raise Exception("list must match the number of rows : "+self.grid_rows )

    def set_widgets(self,col_widgets:Union[dict,list]):
        if isinstance(col_widgets,dict):
            for col_idx in col_widgets:
                value = col_widgets[col_idx]
                self._col_widgets[col_idx] = value
        elif isinstance(col_widgets,list):
            self._col_widgets = col_widgets

    def set_row_widgets(self,row,widget_s):
        #the row has not been created
        if not row in self._row_widgets:
            #create the row
            w_list = list()
            for i in range(0,self._grid_cols):
                w_list.append(qzw.CellLabel(background_color = (0.95,0.95,0.95,1)))
            self._row_widgets[row] = w_list
        #this is a widget, set the widget for the whole row
        if isinstance(widget_s,Widget):
            w_list = self._row_widgets[row]
            for i in range(len(w_list)):
                w_list[i] = widget_s
        #this is a dictionary, set the widget in the appropiate column
        elif isinstance(widget_s,dict):
            for col_idx in widget_s:
                value = widget_s[col_idx]
                self._col_widgets[col_idx] = value


    def set_types(self,col_types:Union[dict,list]):
        if isinstance(col_types,dict):
            for col_idx in col_types:
                tt = col_types[col_idx]
                self._col_types[col_idx] = tt
        #list : it assumes all the column types are passed
        elif isinstance(col_types,list):
            self._col_types = col_types

    def set_col_labels(self,col_labels:Union[dict,list]):
        if isinstance(col_labels,dict):
            for i in col_labels:
                value = col_labels[i]
                self._col_headers[i] = value
        elif isinstance(col_labels,list):
            self._col_headers = col_labels

    def set_col_widths(self,col_widths:Union[dict,list]):
        if isinstance(col_widths,dict):
            for i in col_widths:
                value = col_widths[i]
                self._col_widths[i] = value
        elif isinstance(col_widths,list):
            self._col_widths = col_widths

    def set_row_heights(self,row_heights:Union[dict,list]):
        if isinstance(row_heights,dict):
            for i in row_heights:
                value = row_heights[i]
                self._row_heights[i] = value
        elif isinstance(row_heights,list):
            self._row_widgets = row_heights

    def _update_col_sel_widgets(self):
        for idx in range(len(self._sel_cols)):
            val = self._sel_cols[idx]
            tbtn = self._col_idx[idx]
            if tbtn != None:
                if val == 1:
                    tbtn.state = "down"
                else:
                    tbtn.state = "normal"

    def _update_row_sel_widgets(self):
        for idx in range(len(self._sel_rows)):
            val = self._sel_rows[idx]
            tbtn = self._row_idx[idx]
            if tbtn != None:
                if val == 1:
                    tbtn.state = "down"
                else:
                    tbtn.state = "normal"


    def clear_row_selection(self):
        for i in range(len(self._sel_cols)):
            self._sel_cols[i] = 0
            tbtn = self._row_idx[i]
        self._update_row_sel_widgets()

    def select_rows(self,low:int,high:int):
        for i in range(low,high+1):
            self._sel_rows[i] =1
            tbtn = self._row_idx[i]
            tbtn.state = "normal"
        self._update_row_sel_widgets()

    def select_row_list(self,rows:list):
        for idx in rows:
            self._sel_cols[idx] = 1
            tbtn = self._row_idx[idx]
            tbtn.state = "normal"
        self._update_row_sel_widgets()

    def select_columns(self,low:int,high:int):
        for i in range(low,high+1):
            self._sel_cols[i] = 1
            tbtn = self._col_idx[i]
            tbtn.state = "normal"
        self._update_row_sel_widgets()

    def select_col_list(self,cols:list):
        for idx in cols:
            self._sel_rows[idx] = 1
            tbtn = self._col_idx[idx]
            tbtn.state = "normal"
        self._update_col_sel_widgets()

    def clear_col_selection(self):
        for i in range(len(self._sel_rows)):
            self._sel_rows[i] = 0
        self._update_col_sel_widgets()

    def get_selected_rows(self):
        list = [num for num in self._sel_rows if num == 1]
        return list

    def get_selected_cols(self):
        list = [num for num in self._sel_cols if num == 1]
        return list

    """
    "PROPERTIES
    """
    @property
    def virtual(self):
        return self._virtual

    @virtual.setter
    def virtual(self,value):
        self._virtual = value
        if value:
            self._virtual_rows = 0

    @property
    def virtual_rows(self):
        return self._virtual_rows

    @virtual_rows.setter
    def virtual_rows(self,value):
        self._virtual_rows = value
        self.redraw(self.width,self.height)

    @property
    def allow_col_sizing(self):
        return self._allow_col_sizing

    @allow_col_sizing.setter
    def allow_row_sizing(self,value):
        self._allow_col_sizing = value

        for idx in self._col_idx:
            btn = self._col_idx[idx]
            btn.horiz = value

    @property
    def allow_row_sizing(self):
        return self._allow_row_sizing

    @allow_row_sizing.setter
    def allow_row_sizing(self,value):
        self.allow_row_sizing = value

        for idx in self._row_idx:
            btn = self._row_idx[idx]
            btn.vert = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if self.virtual == False:
            if not value is None:
                self._data = value
                if isinstance(value, pd.DataFrame):

                    self.grid_cols = value.shape[1]
                    self.grid_rows = value.shape[0]+ self._virtual_rows
                    self.resize_widgets(self.width,self.height)
                    self.redraw(self.width,self.height)
                    for idx,tt in enumerate(self._data.dtypes):
                        if tt == object:
                            tt = type("")
                        self._col_types[idx] = tt
                    d_cols = dict()
                    for idx, col in enumerate(self._data.columns):
                        d_cols[idx] = col
                    self.set_col_labels(d_cols)

                elif isinstance(value, np.ndarray):
                    self.grid_rows = self._data.shape[0] +self._virtual_rows
                    self.grid_cols = self._data.shape[1]
                    self.redraw(self.width,self.height)
                elif isinstance(value,list):
                    self.grid_rows = len(value) +self._virtual_rows
                    self.grid_cols = len(value[0])
                    self.redraw(self.width,self.height)
                elif isinstance(value,TableModel):
                    self.grid_rows = self.data.get_rows()
                    self.grid_cols = self.data.get_columns()
                    self.set_types(self.data.get_types())
                    self.redraw(self.width,self.height)

            elif value is None:
                self._data = None
                self.fixed_cols = 0
                self._fixed_rows = 0
                self.grid_cols = 1
                self.grid_rows = 1 + self.virtual_rows
                self.redraw(self.width,self.height)

            else:
                raise Exception("Invalid type")
        else:
            self._data = value

    @property
    def fixed_rows(self):
        return self._fixed_rows

    @fixed_rows.setter
    def fixed_rows(self,value):
        self._fixed_rows = value
        self.redraw(-1,-1)

    @property
    def fixed_cols(self):
        return self._fixed_cols

    @fixed_cols.setter
    def fixed_cols(self,value):
        self._fixed_cols = value
        self.redraw(-1,-1)

    @property
    def col_header_height(self):
        return self._col_header_height

    @col_header_height.setter
    def col_header_height(self,value):
        self._col_header_height = value


    @property
    def row_header_width(self):
        return self._row_header_width

    @row_header_width.setter
    def row_header_width(self,value):
        self._row_header_width = value

    @property
    def grid_cols(self):
        return self._grid_cols

    @grid_cols.setter
    def grid_cols(self,value):
        if value > len(self._col_headers):

            while len(self._col_headers) < value:
                self._col_headers.append("")
                #@debug
                lbl = qzw.CellLabel(color = (0.95,0.95,1,1),font_size = 12)
                #lbl = Label(color = (1,1,1,1))
                self._col_widgets.append( lbl )
                self._col_widths.append(self.default_col_width)
                self._sel_cols.append(0)
                self._col_types.append(type(""))

            for y in self._row_widgets:
                w_list = self._row_widgets[y]
                while len(w_list) < value:
                    w_list.append(qzw.CellLabel)

            self._grid_cols = value

        if value < len(self._col_headers):
            self._col_headers = self._col_headers[:value]
            self._col_widgets = self._col_widgets[:value]
            self._col_widths = self._col_widths[:value]
            self._sel_cols = self._sel_cols[:value]
            self._grid_cols = value
            for y in self._row_widgets:
                w_list = self._row_widgets[y]
                w_list = w_list[:value]
                self._row_widgets[y] = w_list
        self._update_hscroll_new()

    @property
    def grid_rows(self):
        return self._grid_rows

    @grid_rows.setter
    def grid_rows(self,value):
        if value > len(self._row_heights):
            while len(self._row_heights) < value:
                self._row_heights.append(self.default_row_height)
                self._row_headers.append("")
                self._sel_rows.append(0)
            self._grid_rows = value
        if value < len(self._row_heights):
            self._row_heights = self._row_heights[:value]
            self._row_headers = self._row_headers[:value]
            self._sel_rows = self._sel_rows[:value]
        self._update_vscroll_new()

    @property
    def focus_col(self):
        return self._focus_col

    @property
    def focus_row(self):
        return self._focus_row

    @property
    def fixed_cols(self):
        return self._focus_col

    @fixed_cols.setter
    def set_fixed_cols(self, value):
        if value != self._fixed_cols:
            self._fixed_cols = value
            self.redraw(self.width,self.height)

