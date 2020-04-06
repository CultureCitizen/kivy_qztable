
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
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.uix.gridlayout import GridLayout

class QzScrollBar(Widget):

    def __init__(self,**kwargs):
        super(QzScrollBar, self).__init__()
        self.btn_low = Button()
        self.btn_high = Button()
        self.btn_slide = Button()
        self.btn_slide.size_hint = (None,None)
        self.btn_slide.size_hint_min = (None,None)
        self.btn_slide.font_size = 10
        self.small_increment = 1
        self._button_size = 30
        self._low_value = 0
        self._high_value = 100
        self._value = 0
        self._range = 20
        self._orientation = "horizontal"
        self._drag = False
        self.height = 30
        self._show_value = "down"

        for key, value in kwargs.items():
            if hasattr(self,key):
                setattr(self,key,value)
            else:
                raise Exception("Invalid attribute:",key)

        self.add_widget(self.btn_low)
        self.add_widget(self.btn_high)
        self.add_widget(self.btn_slide)
        self.bind(on_touch_down=self.on_touch_down_evt)
        self.bind(on_touch_move=self.on_touch_move_evt)
        self.bind(on_touch_up=self.on_touch_up_evt)
        self.bind(size=self.update_layout)
        self.bind(pos=self.update_layout)

        self.register_event_type('on_value_changed')

    def trigger_on_value_changed(self,value):
        self.dispatch('on_value_changed',self)

    def on_value_changed(self,instance):
        pass

    def get_max_value(self):
        return self._high_value - self._range

    def on_touch_down_evt(self,instance,touch):
        #click on the slide button
        if self.btn_slide.collide_point(*touch.pos):
            self._drag = True
            self._down_x = touch.pos[0] - self.btn_slide.pos[0]
            self._down_y = touch.pos[1] - self.btn_slide.pos[1]
            Window.set_system_cursor("crosshair")
            self.show_value()
        #click on the low button
        elif self.btn_low.collide_point(*touch.pos):
            self._value = self._value - self.small_increment
            self._value = self.get_adjusted_value(self._value)
            if self._orientation == "horizontal":
                self.btn_slide.pos[0] = self.value_to_button()
            else:
                self.btn_slide.pos[1] = self.value_to_button()
            self.trigger_on_value_changed(self._value)
            self.show_value()
        #click on the high button
        elif self.btn_high.collide_point(*touch.pos):
            self._value = self._value + self.small_increment
            self._value = self.get_adjusted_value(self._value)
            if self._orientation == "horizontal":
                self.btn_slide.pos[0] = self.value_to_button()
            else:
                self.btn_slide.pos[1] = self.value_to_button()
            self.trigger_on_value_changed(self._value)
            self.show_value()
        else:
            #click in the slider bar,outside the button, perform a pagination
            if self.collide_point(*touch.pos):
                if self._orientation == "horizontal":
                    if touch.pos[0] < self.btn_slide.pos[0]:
                        delta = -1
                    elif touch.pos[0] > self.btn_slide.pos[0] +self.btn_slide.width:
                        delta = 1
                else:
                    if touch.pos[1] > self.btn_slide.pos[1]:
                        delta = -1
                    elif touch.pos[1] < self.btn_slide.pos[1] + self.btn_slide.height:
                        delta = 1

                self._value = self._value + self._range * delta
                self._value = self.get_adjusted_value(self._value)
                if self._orientation == "horizontal":
                    self.btn_slide.pos[0] = self.value_to_button()
                else:
                    self.btn_slide.pos[1] = self.value_to_button()
                self.trigger_on_value_changed(self._value)
                self.show_value()

    def show_value(self):
        if self._show_value in ["always","down"]:
            self.btn_slide.text = str(int(self._value))

    def get_prop_value(self):
        deltal = ( self._high_value - self._low_value ) - self._range
        deltah = ( self._high_value - self._low_value)
        return int((self._value * deltah / deltal)  + self._low_value)

    def get_adjusted_value(self,v):
        max = self.get_max_value()
        r = v
        if self._value < self._low_value:
            r = self._low_value
        if self._value > max:
            r = max
        return int(r)


    def get_max_drag(self):
        if self._orientation == "horizontal":
            #the available size for sliding - the right corner of the button
            max_x = (self.width - (self._button_size) * 2)
            return max_x
        else:
            max_y = (self.height - self._button_size * 2)
            return max_y

    #terminar
    def value_to_button(self):
        delta = self._value - self._low_value
        base = self._high_value - self._low_value

        value_ratio = ( self._value - self._low_value ) / base

        if self._orientation == "horizontal":
            p = self.pos[0] + self._button_size + (self.get_max_drag() * value_ratio)
            return int(p)
        else:
            p = self.pos[1] + self.height - self._button_size - self.get_slider_size()  - (self.get_max_drag() * value_ratio)
            return int(p)

    def button_to_value(self):
        if self._orientation == "horizontal":
            w_base = self.button_slide_space()
            w_ratio = (self.btn_slide.pos[0] - self.pos[0] - self._button_size) / w_base
            v_delta = ( self._high_value - self._low_value )
            self._value = self._low_value + ( v_delta * w_ratio)
        else:
            w_base = self.button_slide_space()
            w_ratio = (self.pos[1] + self.height - self._button_size - ( self.btn_slide.pos[1]  + self.btn_slide.height)   ) / w_base
            v_delta = (self._high_value - self._low_value)
            self._value = self._low_value + ( v_delta * w_ratio)

    def on_touch_move_evt(self,inst,touch):
        if self._drag:
            x = touch.pos[0]
            y = touch.pos[1]
            if self._orientation == "horizontal":
                maxx = self.pos[0] + self.width - self._button_size - self.get_slider_size()
                minx = self.pos[0] +self._button_size
                px = x - self._down_x
                if px < minx:
                    px = minx
                if px > maxx:
                    px = maxx
                self.btn_slide.pos[0] = px
                self.button_to_value()
            elif self._orientation == "vertical":
                maxy = self.pos[1] + self.height - self._button_size - self.get_slider_size()
                miny = self.pos[1] + self._button_size
                self.btn_slide.pos[1] = -(y - self._down_y)
                py = y - self._down_y

                if py < miny:
                    py= miny
                if py > maxy:
                    py = maxy
                self.btn_slide.pos[1] = py
                self.button_to_value()
            self.trigger_on_value_changed(self._value)
            self.show_value()


    def on_touch_up_evt(self,inst, touch):
        if self._drag == True:
            Window.set_system_cursor("arrow")
            self._drag = False
            self.button_to_value()
        if self._show_value in ["","down"]:
            self.btn_slide.text = ""

    """
      Obtain the sliding space for the slide button
    """
    def button_slide_space(self):
        if self._orientation == "horizontal":
            return self.width - (self._button_size * 2)
        else:
            return self.height - (self._button_size * 2)

    def update_layout(self,*args):
        if self.parent != None:
            if self._orientation == "horizontal":
                self.btn_low.pos = self.pos
                self.btn_low.width = self._button_size
                self.btn_low.height = self.height

                self.btn_high.pos =  (self.right - self._button_size, self.pos[1])

                self.btn_high.width = self._button_size
                self.btn_high.height = self.height

                self.btn_slide.pos = ( self.value_to_button(), self.pos[1])
                self.btn_slide.height = self.height

                self.btn_slide.width = self.get_slider_size()

            if self._orientation == "vertical":
                self.btn_high.pos = (self.pos[0], self.pos[1])
                self.btn_high.width = self.width
                self.btn_high.height = self._button_size

                self.btn_low.pos = (self.pos[0], self.pos[1] + self.height - self._button_size)
                self.btn_low.width = self.width
                self.btn_low.height = self._button_size

                self.btn_slide.pos = (self.pos[0], self.value_to_button())
                self.btn_slide.width = self.width
                self.btn_slide.height =  self.get_slider_size()

    def get_slider_size(self):
        if self._orientation == "horizontal":
            v=  int((self._range / ( self._high_value - self._low_value )) *  self.button_slide_space())
        elif self.orientation == "vertical":
            v=  int((self._range / (self._high_value - self._low_value)) * self.button_slide_space())
        #the minimum size is 10 pixels. A smaller size makes it hard to drag
        if v < 17 :
            v = 17
        return v
    @property
    def low_value(self):
        return self._low_value

    @low_value.setter
    def low_value(self,value):
        if value > self._high_value:
            self._high_value = value

        self._low_value = value
        self._value = self.get_adjusted_value(self._value)
        delta = self._high_value - self.low_value
        if self._range > delta:
            self._range = delta
        self.update_layout()

    @property
    def high_value(self):
        return self._high_value

    @high_value.setter
    def high_value(self,value):
        if value < self._low_value:
            self._low_value = value

        self._high_value = value
        self._value = self.get_adjusted_value(self._value)
        delta = self._high_value - self.low_value
        if self._range > delta:
            self._range = delta
        self.update_layout()

    @property
    def base_value(self):
        return self._value

    @base_value.setter
    def base_value(self,value):
        self._value = self.get_adjusted_value(value)
        self.update_layout()

    @property
    def value(self):
        return self.get_prop_value()

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self,value):
        maxv = self.high_value - self.base_value
        if value > maxv:
            self._range = maxv
        else:
            self._range = value

        self.update_layout()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self,value):
        if not value in ["horizontal","vertical"]:
            raise Exception("invalid value:"+value)
        self._orientation = value
        self.update_layout()

    @property
    def button_size(self):
        return self._button_size

    @button_size.setter
    def button_size(self,value):
        self._button_size = value


class TestWindow(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        btn = Button(text = "button 1")
        self.add_widget(btn)

        self.bar =  QzScrollBar()
        self.bar.size_hint_x = None
        self.bar.orientation = "vertical"
        self.bar.width = 30
        self.add_widget(self.bar)

        btn = Button(text = "button 2")
        self.add_widget(btn)

        btn = Button(text = "button 3")
        btn.size_hint_y = None
        btn.height = 10
        self.add_widget(btn)

class TestApp(App):
    def build(self):

        return TestWindow()

if __name__=='__main__':
    TestApp().run()

