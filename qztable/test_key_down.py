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



class Test_keyWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kt = KeyTracker()
        self.kt.bind()

        btn = Button(text="click me")
        btn.bind(on_touch_down= self.on_touch_down)
        self.add_widget(btn)

    def on_touch_down(self, touch):
        print(self.kt.keys)

class Test_keyApp(App):
    def build(self):

        return Test_keyWindow()

if __name__=='__main__':
    Test_keyApp().run()
