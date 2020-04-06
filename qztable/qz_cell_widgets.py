"""
    Generic control that triggers event:
        value changed event
        set_value
        get_value

"""
import os

from kivy.properties import ListProperty
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
from kivy.uix.spinner import SpinnerOption
from kivy.uix.widget import Widget
from kivy.event import EventDispatcher
from kivy.uix.colorpicker import ColorPicker
from kivy.graphics import Color
from qzutils import Gui
from kivy.uix.filechooser import FileChooser, FileChooserListView , FileChooserIconView
from kivy.graphics import Rectangle, Color
import builtins

def get_widget_class(w):
    if hasattr(w,"get_value") and hasattr(w,"set_value") and hasattr(w,"on_value_changed"):
        return "rw"
    elif hasattr(w,"get_value") and hasattr(w,"set_value"):
            return "r"
    else:
        return ""



def convert_to_value(source,dest_value):
      str_type = str(type(dest_value))
      start = str_type.find("'")
      str_type = str_type[start+1: -2]
      return getattr(builtins, str_type)(source)

def convert_to_type(source,dest_type:type):
      str_type = str(dest_type)
      start = str_type.find("'")
      str_type = str_type[start+1: -2]
      return getattr(builtins, str_type)(source)

def convert_to_stype(source,dest_type:str):
      return getattr(builtins, dest_type)(source)



class CellTextInputButton(BoxLayout,EventDispatcher):
    def __init__(self,**kwargs):

        BoxLayout.__init__(self,**kwargs)
        EventDispatcher.__init__(self,**kwargs)

        self.size_hint_y = None
        self.orientation = "horizontal"

        self.textInput = TextInput()
        self.textInput.size_hint_x = 0.9
        self.textInput.multiline = False
        self.button = Button()
        self.button.text = "..."
        self.button.size_hint_min_x = 20
        self.button.size_hint_x = None
        self.button.height = 25
        self.button.width = 25
        self.button.bind(width=self.set_button_width)

        self.add_widget(self.textInput)
        self.add_widget(self.button)

        self.register_event_type('on_value_changed')
        self.textInput.bind(on_text_validate=self.trigger_on_value_changed)
        self.height = 25


    def set_button_width(self):
        self.button.width = self.height

    def trigger_on_value_changed(self, *args):
        self.dispatch('on_value_changed',args[0].text)

    def get_value(self):
        return self.textInput.text

    def set_value(self,value):
        self.textInput = value

    def on_value_changed(self,instance,value):
        pass


class CellTxtInput(TextInput):
    def __init__(self,**kwargs):
        super(CellTxtInput,self).__init__(**kwargs)

        self.register_event_type('on_value_changed')
        self.bind(on_text_validate=self.trigger_on_value_changed)
        self.bind(focus=self.trigger_on_value_changed)

    def trigger_on_value_changed(self, *args):
        self.dispatch('on_value_changed',args[0].text)

    def get_value(self):
        return self.text

    def set_value(self,value):
        self.text = value

    def on_value_changed(self,instance,value):
        pass


class CellCheckbox(CheckBox):
    def __init__(self,**kwargs):
        CheckBox.__init__(self,**kwargs)

        self.register_event_type('on_value_changed')
        self.bind(active=self.trigger_on_value_changed)

    def trigger_on_value_changed(self, *args):
        self.dispatch('on_value_changed',args[1])

    def get_value(self):
        return self.active

    def set_value(self,value):
        if self.widget.active != value:
            self.widget.active = value

    def on_value_changed(self,instance,value):
        pass

class CellSpinnerOptions(SpinnerOption):
    Height = 25
    BackgroundColor = [0,0,1,1]

    def __init__(self, **kwargs):
        super(CellSpinnerOptions, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = self.BackgroundColor    # blue colour
        self.height = self.Height


class CellSpinner(Spinner):
    def __init__(self,**kwargs):
        super(CellSpinner, self).__init__(**kwargs)

        self.register_event_type('on_value_changed')
        self.bind(is_open=self.trigger_on_value_changed)
        self.option_cls = CellSpinnerOptions

    def get_value(self):
        return self.text

    def set_value(self,value):
        self.text = value

    def trigger_on_value_changed(self, *args):
        self.dispatch('on_value_changed',self.text)

    def on_value_changed(self,value):
        pass


class CellLabel(Label):
    background_color = ListProperty([0.2, 0.2, 0.2, 1])

    def __init__(self,**kwargs):
        super(CellLabel, self).__init__(**kwargs)
        self.register_event_type('on_value_changed')
        if "background_color" in kwargs:
            self.background_color = kwargs["background_color"]
        c = self.background_color
        with self.canvas.before:
            #Color(self.background_color)
            Color(c[0],c[1],c[2],c[3])
            self.rect = Rectangle(pos=(self.pos[0]+1,self.pos[1]+1),
                                          size=(self.size[0]-2,self.size[1]-2))

        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self,*args):
        self.rect.pos = (self.pos[0]+1,self.pos[1]+1)
        self.rect.size = (self.size[0]-2,self.size[1]-2)

    def get_value(self):
        return self.text

    def set_value(self,value):
        self.text = value

    #def trigger_on_value_changed(self, *args):
    #    self.dispatch('on_value_changed',args[1])

    def on_value_changed(self,instance,value):
        pass

class ColorDialog(Widget):
    def __init__(self,**kwargs):
        self._rgba = [1.0,1.0,1.0,1.0]
        self._tmp_rgba = [1.0,1.0,1.0,1.0]

        self.widget_props:set = {"rgba"}
    @property
    def accept(self):
        return self._accept

    @property
    def rgba(self):
        return self._rgba

    @rgba.setter
    def rgba(self,value):
        self._rgba = value

    def show(self, rgba, title="", width=400, height=430):

        self._accept = False
        self._rgba = rgba
        vbox_main = BoxLayout(orientation = "vertical")
        hbox_buttons = BoxLayout(orientation = "horizontal")
        hbox_buttons.size_hint_y = None
        hbox_buttons.height = 35
        btn_ok = Button(text="Ok", size_hint_y = None, height = 30)
        btn_cancel = Button(text="Cancel", size_hint_y = None, height = 30)
        self.cp = ColorPicker()
        self.cp.color = self._rgba

        #bind
        self.cp.bind(color=self.on_color)
        btn_ok.on_release = lambda: self.handle_color_picked(self._rgba)
        btn_cancel.on_release = lambda : self.popup.dismiss()

        #layout
        hbox_buttons.add_widget(btn_ok)
        hbox_buttons.add_widget(btn_cancel)
        vbox_main.add_widget(self.cp)
        vbox_main.add_widget(hbox_buttons)


        self.popup = Popup(title='',
            content=vbox_main,
            size_hint=(None, None), size=(width,height))
        self.popup.open()
        print("size:", btn_ok.on_release)

    @property
    def rgba(self):
        return self._rgba

    @rgba.setter
    def rgba(self, value):
        self._rgba = value

    def on_color(self,instance,rgba):
        self._tmp_rgba = rgba

    def handle_color_picked(self,*args):
        self.rgba = self._tmp_rgba
        self.trigger_color_picked(*args)
        self.popup.dismiss()
        return True

    def handle_cancel(self,*args):
        self.popup.dismiss()

class FileDialog(Widget):
    def __init__(self,**kwargs):
        super(FileDialog,self).__init__(**kwargs)
        self._pick_mode = "file"
        self._single_file = True
        self._view_type = "list"
        self._sel_files = list()
        self._sel_path = ""

    def show(self, path, title="", width=400, height=430):
        self._path = os.path.split(path)
        self._old_path = ""

        self.vbox_main = BoxLayout( orientation = "vertical")
        self.txt_path = TextInput( size_hint_y = None, height = 30)
        self.txt_path.multiline = False
        self.txt_path.text = self._path
        self.txt_path.bind(focus=self.on_focus)
        self.txt_path.bind(on_text_validate= self.validate_path )

        self.fclv = FileChooserIconView()
        self.fclv.path = self._path

        self.fclv.bind(path=self.set_path)
        self.fclv.multiselect = True

        vb_buttons = BoxLayout(orientation = "horizontal")
        vb_buttons.size_hint_y = None
        vb_buttons.height = 30
        self.btn_ok = Button(text= "Ok")
        self.btn_cancel = Button(text ="Cancel")
        vb_buttons.add_widget(self.btn_ok)
        vb_buttons.add_widget(self.btn_cancel)

        self.vbox_main.add_widget(self.txt_path)
        self.vbox_main.add_widget(self.fclv)
        self.vbox_main.add_widget(vb_buttons)


        self.btn_ok.on_release = lambda: self.handle_ok(self.txt_path.text,self.fclv)
        self.btn_cancel.on_release = lambda : self.popup.dismiss()

        self.popup = Popup(title=title,
            content=self.vbox_main,
            size_hint=(None, None), size=(width,height))
        self.popup.open()

    def handle_ok(self,path,selection):
        if self.pick_mode == "file":
            if len(selection) == 0:
                Gui.message(self,"Select a file")
            else:
                self._sel_files.extend(selection)
                self.popup.dismiss()
        else:
            self._sel_path = path
            self.popup.dismiss()

    @property
    def pick_mode(self):
        return self._pick_mode

    @pick_mode.setter
    def pick_mode(self, value):
        valid_values = ["file","path"]
        if value in valid_values:
            self._pick_mode = value
        else:
            raise  Exception("invalid pick_mode. Valid values:"+valid_values)

    @property
    def view_type(self):
        return self._pick_mode

    @view_type.setter
    def view_type(self, value):
        valid_values = ["list","icon"]
        if value in valid_values:
            self._view_type = value
        else:
            raise  Exception("invalid view type. Valid values:"+valid_values)


    @property
    def single_file(self):
        return self._single_file

    @single_file.setter
    def single_file(self, value):
        self._single_file = value

    @property
    def selected_files(self):
        return self._sel_files

    @property
    def selected_path(self):
        return self._sel_path


class CellButton(Button):
    def __init__(self,**kwargs):
        super(CellButton,self).__init__(**kwargs)
        self._rgba = [0.3,0.3,0.3,1.0]
        self.background_color = self._rgba
        self.background_normal = ''
#        self.register_event_type('on_value_changed')

    def get_value(self):
        return self.text

    def set_value(self,value):
        self.text = value


    #def on_value_changed(self,instance,value):
    #    pass


class CellColorButton(Button):
    def __init__(self,**kwargs):
        super(CellColorButton,self).__init__()
        self.register_event_type('on_value_changed')
        self.bind(on_release=self.handle_on_release)
        self._rgba = [1.0,1.0,1.0,1.0]
        self.background_color = self._rgba
        self.background_normal = ''
        self.dialog=True

        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
#            if k =="dialog":
#                self.dialog = v


    def handle_on_release(self,*args):
        dlg = ColorDialog()
        dlg.bind(on_color_picked=self.on_color_picked)
        dlg.show(self._rgba,'',400,450)

    def on_color_picked(self, instance,rgba):
        self._rgba = rgba
        self.background_color = rgba
        self.dispatch('on_value_changed',instance, self.color)

    def get_value(self):
        return Gui.frgba_to_int(self.color)

    def set_value(self,value:int):
        self._rgba = Gui.int_to_frgba(value)

    def on_value_changed(self,instance,value):
        pass

class TestWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        spn = CellSpinner(text="45", values = ["45","90","135","180","225","270","315"],
                       size_hint=(0.1,None),height=30)
        self.bind_widget(spn)
        self.add_widget(spn)

        chb = CellCheckbox()
        #chb.bind(on_value_changed=self.handle_value_changed )
        self.bind_widget(chb)
        self.add_widget(chb)

        txt = CellTxtInput()
        txt.size_hint = (None,None)
        txt.height = 25
        txt.width = 200
        txt.multiline = False
        self.bind_widget(txt)
        self.add_widget(txt)

        tb = CellTextInputButton()
        self.bind_widget(tb)
        self.add_widget(tb)

        ccb = CellColorButton()
        self.add_widget(ccb)

    def handle_value_changed(self,instance,value):
        if hasattr(instance,"get_value"):
            print("protocol",instance,"=", instance.get_value())
        else:
            print(instance,"=",value)
        return True

    def bind_widget(self,widget):
        if hasattr(widget,"trigger_on_value_changed") and hasattr(widget,"on_value_changed"):
           widget.bind(on_value_changed=self.handle_value_changed)



class TestApp(App):
    def build(self):

        return TestWindow()

if __name__=='__main__':
    TestApp().run()

