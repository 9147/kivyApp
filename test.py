from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.app import MDApp

# Load the KivyMD design language string
kv_string = '''
<RootLayout>:
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)  # Adjust the height as needed

                Label:
                    text: "Group 1 Label 1"
                Button:
                    text: "Button 1"
                Button:
                    text: "Button 2"
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)  # Adjust the height as needed

                Label:
                    text: "Group 2 Label 1"
                Button:
                    text: "Button 3"
                Button:
                    text: "Button 4"

            # Add more BoxLayouts for additional groups as needed
'''

class RootLayout(BoxLayout):
    pass

class MyApp(MDApp):
    def build(self):
        return RootLayout()

if __name__ == "__main__":
    MyApp().run()
