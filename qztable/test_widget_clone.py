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
from kivy.properties import ObservableList

"""
    This is a test script to see how a kivy widget cloning could be done
    Several approaches were tried: 
        __dict__ = it didn't return all the properties
        dir = returns a lot of "artifacts" which are not properties , so more filtering has to be done
            This was the best method so far.
        I couldn't find a way to make the event binding dynamically
        
"""

"""
widget_props = [
"background_color","background_disabled_down","background_down","background_normal","border",
"allow_stretch","anim_delay","anim_loop","image_ratio","keep_ratio","keep_data","mip"
"anchors", "base_direction", "bold", "center", "center_x", "center_y",
"collide_point", "collide_widget", "color",
"disabled", "disabled_color","disabled_outline_color","ellipsis_options","font_blended",
"font_context","font_family","font_features","font_hinting", "font_kerning",
"font_name","font_size","halign","height","inc_disabled",
"is_event_type","is_shortened","italic","line_height","markup","max_lines",
"on_kv_post","on_opacity","on_ref_press","on_touch_down","on_touch_move","on_touch_up",
"opacity","outline_color","outline_width","padding","padding_x","padding_y","parent","pos","pos_hint",
"properties","property","right","size","size_hint","size_hint_max","size_hint_max_x",
"size_hint_max_y","size_hint_min","size_hint_min_x","size_hint_min_y","size_hint_x",
"size_hint_y","split_str","strikethrough","strip","text","text_language",
"text_size","texture","texture_size","underline","valign","width",
"x","y"]
"""

def clone_widget(source,dest,include:set={},exclude:set={"pos","x","y"}):
    props = dir(source)
    for p in props:
        #skip events
        if p[:3] == "on_":
            pass
        #skip the id and the private properties
        elif p in ["id","uid"] or p[0] == "_":
            pass
        else:
            value = getattr(source,p)
            tt = type(value)
            #skip if it is in the exclude list
            if p in exclude:
                pass
            #add the include list
            elif isinstance(value, (float, int, str, list, dict, tuple,bool, ObservableList)) or p in include:
                try:
                    setattr(dest,p,value)
                except Exception as e:
                    print("set failed:",p)
            else:
                pass

class Widget_test_window(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        lab1 = Label(text = "Hello World" )
        lab1.size_hint = (None,None)
        lab1.halign = "right"
        lab1.height = 30
        lab1.width = 200
        lab1.color = ( 1,0,0,1)
        txt1 = TextInput(text = "hi there!")
        txt1.multiline = False
        txt1.hint_text = "greeting"
        txt2 = TextInput()
        txt1.bind(on_text_validate=self.on_text_validate)
        clone_widget(txt1,txt2)
        lab2 = Label(text ="hello")
        clone_widget(lab1,lab2)

        self.add_widget(lab1)
        self.add_widget(lab2)
        self.add_widget(txt1)
        self.add_widget(txt2)

    def on_text_validate(self,instance,*args):
        print("validate",instance,args)

class widget_test_App(App):
    def build(self):

        return Widget_test_window()



if __name__=='__main__':
    widget_test_App().run()
