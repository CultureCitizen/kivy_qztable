import kivy
from kivy.uix.widget import Widget
import kivy.modules.screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.button import Label
from kivy.properties import ObservableList
from kivy.core.window import Window


class KeyTracker(object):
    SHIFT = 304
    ALT = 308
    CTRL = 305
    ALT_GR = 308
    CAPS = 301

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keys = set()
        self.track_set = set([self.CTRL,self.ALT,self.SHIFT,self.ALT_GR,self.CAPS])

    def bind(self):
        Window.bind(on_key_down= self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

    def on_key_down(self,*args):
        key = args[1]
        if key in self.track_set:
            if not key in self.keys:
                self.keys.add(key)

    def on_key_up(self,*args):
        key = args[1]
        if key in self.track_set:
            if key in self.keys:
                self.keys.remove(key)


class Gui(object):

    date_format_in = ""
    date_format_out = ""
    int_format_out = "{:.2f}"

    def value_to_string(self,value)->str:
        tt = type(value)
        if tt=='str':
            return value
        elif tt=='int':
            return self.int_format_out.format(value)
        elif tt=='float':
            return self.float_format_out.format(value)
        elif tt=='':
            pass

    @staticmethod
    def clone_widget(source,dest,include:set={},exclude:set={"pos","x","y"}):
        props = dir(source)
        if hasattr(source,"widget_props"):
            new_props = source.widget_props
        else:
            new_props = set()
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
                if p in exclude or p in {"cursor_col","cursor_pos","cursor_row","minimum_height","minimum_width"}:
                    pass
                #add the include list or the declared list of widget properties
                elif isinstance(value, (float, int, str, list, dict, tuple,bool, ObservableList)) or p in include\
                        or p in new_props:
                    try:
                        setattr(dest,p,value)
                    except Exception as e:
                        print("set failed:",p)
                else:
                     pass

    @staticmethod
    def init_widget(source,dest):
        if hasattr(source,"init_props"):
            for prop in source.init_props:
                value = source.init_props[prop]
                setattr(dest,prop,value)

    @staticmethod
    def message(parent,message,title="message",width = 400,height = 200):
        vbox = BoxLayout(orientation = "vertical")
        btn_ok = Button(text = "Ok" , size_hint_y = None, height = 30)
        lab_message = Label(text = message)
        vbox.add_widget(lab_message)
        vbox.add_widget(btn_ok)
        popup = Popup(title=title,
            content=vbox,
            size_hint=(None, None), size=(width,height))
        btn_ok.bind(on_release=popup.dismiss)

        popup.open()


    @staticmethod
    def frgba_to_int(rgb:list):
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        if len(rgb) >= 4:
            alpha = rgb[3]
        else:
            alpha = 1
        value = (int(alpha*255) << 24) + (int(red*255) <<16) + (int(green*255) <<8) + int(blue *255)
        return value

    @staticmethod
    def int_to_frgba(value:int):
        blue =  float(value & 255) / 255
        green = float((value >> 8) & 255) / 255
        red =   float((value >> 16) & 255) / 255
        alpha = float((value >> 24) & 255) /255
        return [ red, green, blue,alpha ]


    @staticmethod
    def int_to_rgba(value:int):
        blue =  value & 255
        green = (value >> 8) & 255
        red =   (value >> 16) & 255
        alpha = (value >> 24) & 255
        return [ red, green, blue,alpha ]

    @staticmethod
    def rgba_to_int(rgb:list):
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        if len(rgb) >= 4:
            alpha = rgb[3]
        else:
            alpha = 255
        value = (alpha << 24) + (red<<16) + (green<<8) + blue
        return value


    @staticmethod
    def int_to_rgb(value:int):
        blue =  value & 255
        green = (value >> 8) & 255
        red =   (value >> 16) & 255
        return [ red, green, blue ]

    @staticmethod
    def rgb_to_int(rgb:list):
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        value = (red<<16) + (green<<8) + blue
        return value

    @staticmethod
    def set_widget_size(w:Widget,x:int,y:int):
        if x <= 1 and x > 0 :
            w.size_hint_x = x
        elif x> 1:
            w.size_hint_x = None
            w.width = x
        else:
            pass

        if y <= 1 and y > 0 :
            w.size_hint_x = x
        elif y > 1:
            w.size_hint_y = None
            w.height = y
        else:
            pass
