import os

from kivy.core.window import Window
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast


KV = '''
MDBoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "MDFileManager"
        left_action_items: [["menu", lambda x: None]]
        elevation: 3

    MDFloatLayout:

        MDRoundFlatIconButton:
            text: "Open manager"
            icon: "folder"
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: app.file_manager.file_manager_open()
'''

class CustomFileManager(MDFileManager):
    def show(self, path):
        '''Forms the body of a directory. Called when opening a directory.'''

        self.current_path = path
        super().show(path)
        self.selection_button.opacity = 0  # hide the selection_button
        self.selection_button.disabled = True 

class ImageManager():
    def __init__(self):
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = CustomFileManager(
            exit_manager=self.exit_manager, 
            select_path=self.select_path,
            ext=['.jpg', '.png', '.jpeg'],# only show these types of files
            preview=True, # allow preview of images
            icon_selection_button="none",
        )

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''
        self.exit_manager()
        toast(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

class Example(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = ImageManager()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Builder.load_string(KV)



Example().run()

