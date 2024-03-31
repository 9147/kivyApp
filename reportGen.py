import os
import shutil
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarActionButton
from kivymd.uix.menu import MDDropdownMenu
import glob
import requests
import sqlite3
import json
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from fpdf import FPDF
from kivy.uix.filechooser import FileChooser

url = "http://127.0.0.1:8000/"

Builder.load_string('''
#:import toast kivymd.toast.toast

<LoginScreen>:
    orientation: "vertical"
    padding: "10dp"
    spacing: "10dp"

    MDTopAppBar:
        title: "ReportGen"
        pos_hint: {"top": 1}

    Widget:

    BoxLayout:
        size_hint: (None, None)
        size: ("300dp", "200dp")
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        orientation: "vertical"
        spacing: "10dp"

        MDTextField:
            id: username
            hint_text: "username"
            helper_text: "Enter your esername"
            helper_text_mode: "on_focus"
            icon_right: "account"
            size_hint: (.8,None)
            icon_right_color: app.theme_cls.primary_color
            pos_hint: {"center_x": 0.5, "center_y": 1}

        MDTextField:
            id: password
            hint_text: "Password"
            helper_text: "Enter your password"
            helper_text_mode: "on_focus"
            password: True
            size_hint: (.8,None)
            icon_right: "eye-off"
            icon_right_color: app.theme_cls.primary_color
            pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            on_release: app.on_login(username.text, password.text)

    Widget:

<HomeScreen>:
    name: 'home'
    MDTopAppBar:
        title: "ReportGen"
        pos_hint: {"top": 1}
        right_action_items: [["logout", lambda x: app.logout()]]


    BoxLayout:
        size_hint: (None, None)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        orientation: "vertical"
        spacing: "30dp"

        Widget:

        MDRaisedButton:
            text: "Edit Report"
            size_hint: (None, None)
            size: ("400dp", "150dp")
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'edit'

        MDRaisedButton:
            text: "Print Report"
            size_hint: (None, None)
            size: ("400dp", "150dp")
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'print'

        MDRaisedButton:
            text: "Add Report"
            size_hint: (None, None)
            size: ("400dp", "150dp")
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'add'

        Widget:

<EditScreen>:
    name: 'edit'
    MDTopAppBar:
        title: "ReportGen"
        pos_hint: {"top": 1}
        right_action_items: [["home", lambda x: app.go_home()], ["logout", lambda x: app.logout()]]

    BoxLayout:
        id: container
        orientation: 'vertical'
        size_hint: (1, 1)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}


<PrintScreen>:
    name: 'print'
    MDTopAppBar:
        title: "ReportGen"
        pos_hint: {"top": 1}
        right_action_items: [["home", lambda x: app.go_home()], ["logout", lambda x: app.logout()]]

    BoxLayout:
        id: container
        orientation: 'vertical'
        size_hint: (1, 1)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

<AddScreen>:
    name: 'add'
    MDTopAppBar:
        title: "ReportGen"
        pos_hint: {"top": 1}
        right_action_items: [["home", lambda x: app.go_home()], ["logout", lambda x: app.logout()]]

    BoxLayout:
        id: container
        orientation: 'vertical'
        size_hint: (1, 1)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        

''')


class LoginScreen(Screen, MDBoxLayout):
    pass


class HomeScreen(Screen):

    def on_enter(self, *args):
        get_data_scheme()


class EditScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.selected_row = None
        self.workbook_active = None
        self.workbook = None
        self.sheets = None
        self.current_sheet_index = 0
        self.values = []

    def on_enter(self, *args):
        self.values = []
        self.ids.container.clear_widgets()
        self.get_xlsx_files()

    def get_xlsx_files(self):
        files = glob.glob('resources/*.xlsx')
        dropdown_items = [os.path.basename(f) for f in files]
        self.add_buttons(dropdown_items)

    def add_buttons(self, files):
        widge = Widget()
        self.ids.container.add_widget(widge)
        for file in files:
            button = MDRaisedButton(text=file, on_release=self.on_button_click, pos_hint={"center_x": 0.5})
            self.ids.container.add_widget(button)
        widge = Widget()
        self.ids.container.add_widget(widge)

    def on_button_click(self, instance):
        self.workbook_active = instance.text
        workbook = load_workbook(filename=f'resources/{instance.text}')
        # get the first sheet
        sheets = [sheet.title for sheet in workbook.worksheets]

        # Create a list to hold the sheets
        self.sheets = sheets
        self.workbook = workbook
        self.current_sheet_index = 0
        self.ids.container.clear_widgets()
        self.ids.container.add_widget(Widget())
        # add a text field for the admission number
        text_field = MDTextField(hint_text='Admission Number', pos_hint={"center_x": 0.5}, id='admissionNo')
        self.ids.container.add_widget(text_field)
        self.ids.container.add_widget(
            MDRaisedButton(text='Match', on_release=self.match_admissionNo, pos_hint={"center_x": 0.5}))
        self.ids.container.add_widget(Widget())

    def match_admissionNo(self, instance):
        match=False
        for widget in self.ids.container.children:
            if isinstance(widget, MDTextField) and widget.id == 'admissionNo':
                text_field = widget
                break
        admissionNo = text_field.text
        if admissionNo:
            sheet = self.workbook['cover_page']
    #         in first row find the cell with value admission number
            for cell in sheet[1]:
                if cell.value == 'Admission Number':
                    row:int=2
                    while row <= sheet.max_row:
                        if str(sheet.cell(row=row, column=cell.column).value).strip() == str(admissionNo).strip():
                            self.on_admissionNo_match()
                            match=True
                            self.selected_row = row
                        row += 1
        if not match:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Admission Number does not match",
                ),
                MDSnackbarActionButton(
                    text="DISMISS",
                    on_release=lambda *args: snackbar.dismiss(),
                    theme_text_color="Custom",
                    text_color="#8E353C",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                md_bg_color="#E8D8D7",
            )
            snackbar.open()


    def on_admissionNo_match(self):
        # remover everything inside the container
        self.ids.container.clear_widgets()
        # Create a ScrollView
        scroll_view = ScrollView(do_scroll_x=False, size_hint=(None, None), size=(400, 450), pos_hint={"center_x": 0.5})
        # Create a BoxLayout inside the ScrollView
        box_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))
        scroll_view.add_widget(box_layout)

        # Create MDTextField for each cell in the first row of the first sheet
        self.create_text_fields(box_layout, self.current_sheet_index)

        # Add the ScrollView to the container
        self.ids.container.add_widget(Widget())
        self.ids.container.add_widget(scroll_view)
        self.ids.container.add_widget(Widget())


    def create_button_fields(self, box_layout, sheet_index):
        # Clear the BoxLayout
        box_layout.clear_widgets()
        self.ids.container.clear_widgets()
        # Get the current sheet
        sheet = self.sheets[sheet_index]
        worksheet = self.workbook[sheet]

        # Get the first row
        row = worksheet[1]
        val = []


        # Create a button for each cell in the row
        for i in range(0, len(row), 2):
            cell1 = row[i]
            cell2 = row[i+1]
            if cell1.value and cell2.value:
                common_text = get_common_text(cell1.value, cell2.value)
                component = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                label = MDLabel(text=common_text)
                button1 = MDRaisedButton(text='Term 1')
                button2 = MDRaisedButton(text='Term 2')
                component.add_widget(label)
                component.add_widget(button1)
                component.add_widget(button2)
                box_layout.add_widget(component)


        # # Create a MDTextField for each cell in the row
        # for cell in row:
        #     if cell.value:
        #         text_field = MDTextField(hint_text=str(cell.value), text=str(worksheet.cell(row=self.selected_row, column=cell.column).value) if worksheet.cell(row=self.selected_row, column=cell.column).value else "")
        #         box_layout.add_widget(text_field)

        next_button = MDRaisedButton(text='Next', on_release=self.on_next_button_click, pos_hint={"center_x": 0.5})
        box_layout.add_widget(next_button)

    def create_text_fields(self, box_layout, sheet_index):
        # Clear the BoxLayout
        box_layout.clear_widgets()
        self.ids.container.clear_widgets()
        # Get the current sheet
        sheet = self.sheets[sheet_index]
        worksheet = self.workbook[sheet]

        # Get the first row
        row = worksheet[1]
        val = []

        # Create a MDTextField for each cell in the row
        for cell in row:
            if cell.value:
                text_field = MDTextField(hint_text=str(cell.value), text=str(worksheet.cell(row=self.selected_row, column=cell.column).value) if worksheet.cell(row=self.selected_row, column=cell.column).value else "")
                box_layout.add_widget(text_field)

        next_button = MDRaisedButton(text='Next', on_release=self.on_next_button_click, pos_hint={"center_x": 0.5})
        box_layout.add_widget(next_button)

    def on_next_button_click(self, instance):
        # Increment the current sheet index
        self.current_sheet_index += 1
        # iterate throught the text fields and get the values
        value_li = []
        for child in self.ids.container.children:
            if isinstance(child, ScrollView):
                for widget in child.children:
                    if isinstance(widget, BoxLayout):
                        for text_field in widget.children:
                            if isinstance(text_field, MDTextField):
                                print(text_field.text)
                                value_li.append(text_field.text)
        self.values.append(value_li[::-1])

        # Clear the container
        self.ids.container.clear_widgets()
        # Create a ScrollView
        scroll_view = ScrollView(do_scroll_x=False, size_hint=(None, None), size=(400, 450), pos_hint={"center_x": 0.5})
        # Create a BoxLayout inside the ScrollView
        box_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))
        scroll_view.add_widget(box_layout)

        # If there are more sheets, create text fields for the next sheet
        if self.current_sheet_index < len(self.sheets):
            if self.sheets[self.current_sheet_index] in ['cover_page','first_page']:
                self.create_text_fields(box_layout, self.current_sheet_index)
            else:
                self.create_button_fields(box_layout, self.current_sheet_index)
            self.ids.container.add_widget(Widget())
            self.ids.container.add_widget(scroll_view)
            self.ids.container.add_widget(Widget())
        else:
            #             display its done and add a home button
            self.ids.container.clear_widgets()
            self.ids.container.add_widget(Widget())
            self.ids.container.add_widget(MDLabel(text='Done', halign='center', theme_text_color='Primary'))
            self.ids.container.add_widget(Widget())
            print(self.values)
            for sheet, value in zip(self.sheets, self.values):
                worksheet = self.workbook[sheet]
            #      add values to the selected rows
                for val,a in zip(worksheet[self.selected_row],value):
                    val.value=a
            #     col=0
            #     for a in value:
            #         worksheet.cell(row=self.selected_row, column=col + 1, value=a)
            self.workbook.save(f'resources/{self.workbook_active}')


class PrintScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.selected_row = None
        self.workbook_active = None
        self.workbook = None
        self.sheets = None
        self.current_sheet_index = 0
        self.values = []

    def on_enter(self, *args):
        self.values = []
        self.ids.container.clear_widgets()
        self.get_xlsx_files()

    def get_xlsx_files(self):
        files = glob.glob('resources/*.xlsx')
        dropdown_items = [os.path.basename(f) for f in files]
        self.add_buttons(dropdown_items)

    def add_buttons(self, files):
        widge = Widget()
        self.ids.container.add_widget(widge)
        for file in files:
            button = MDRaisedButton(text=file, on_release=self.on_button_click, pos_hint={"center_x": 0.5})
            self.ids.container.add_widget(button)
        widge = Widget()
        self.ids.container.add_widget(widge)

    def on_button_click(self, instance):
        self.workbook_active = instance.text
        workbook = load_workbook(filename=f'resources/{instance.text}')
        # get the first sheet
        sheets = [sheet.title for sheet in workbook.worksheets]

        # Create a list to hold the sheets
        self.sheets = sheets
        self.workbook = workbook
        self.current_sheet_index = 0
        self.ids.container.clear_widgets()
        self.ids.container.add_widget(Widget())
        # add a text field for the admission number
        text_field = MDTextField(hint_text='Admission Number', pos_hint={"center_x": 0.5}, id='admissionNo')
        self.ids.container.add_widget(text_field)
        self.ids.container.add_widget(
            MDRaisedButton(text='Match', on_release=self.match_admissionNo, pos_hint={"center_x": 0.5}))
        self.ids.container.add_widget(Widget())

    def match_admissionNo(self, instance):
        match=False
        for widget in self.ids.container.children:
            if isinstance(widget, MDTextField) and widget.id == 'admissionNo':
                text_field = widget
                break
        admissionNo = text_field.text
        if admissionNo:
            sheet = self.workbook['cover_page']
    #         in first row find the cell with value admission number
            for cell in sheet[1]:
                if cell.value == 'Admission Number':
                    row:int=2
                    while row <= sheet.max_row:
                        if str(sheet.cell(row=row, column=cell.column).value).strip() == str(admissionNo).strip():
                            match=True
                            self.selected_row = row
                        row += 1
        if not match:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Admission Number does not match",
                ),
                MDSnackbarActionButton(
                    text="DISMISS",
                    on_release=lambda *args: snackbar.dismiss(),
                    theme_text_color="Custom",
                    text_color="#8E353C",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                md_bg_color="#E8D8D7",
            )
            snackbar.open()
        else:
            self.get_images()
            self.on_admissionNo_match()


    def on_admissionNo_match(self):
        # remover everything inside the container
        self.ids.container.clear_widgets()
        print('admission number matched')
        self.add_save_button()

    def add_save_button(self):
        button = MDRaisedButton(text='Save PDF', on_release=self.save_pdf, pos_hint={"center_x": 0.5})
        self.ids.container.add_widget(Widget())
        self.ids.container.add_widget(MDTextField(hint_text='Save name', id='save_location', pos_hint={"center_x": 0.5}))
        self.ids.container.add_widget(button)
        self.ids.container.add_widget(Widget())

    def save_pdf(self,instance):
    #    save the file to the location
        for widget in self.ids.container.children:
            if isinstance(widget, MDTextField) and widget.id == 'save_location':
                text_field = widget
                break
        try:
            save_location = "D:/Reports/"+self.workbook_active.split('.')[0]+"/"+text_field.text
            os.makedirs(os.path.dirname(save_location), exist_ok=True)  # Create directories if not present
            if not save_location.endswith('.pdf'):
                save_location+='.pdf'
            if save_location:
                shutil.move(f'resources/{self.workbook_active.split(".")[0]}.pdf', save_location)
                toast('PDF saved successfully')
                # display it is done
                self.ids.container.clear_widgets()
                self.ids.container.add_widget(Widget())
                self.ids.container.add_widget(MDLabel(text='PDF saved successfully', halign='center', theme_text_color='Primary'))
                self.ids.container.add_widget(Widget())
            else:
                toast('Please enter a save location')
        except FileNotFoundError:
            self.ids.container.clear_widgets()
            self.ids.container.add_widget(Widget())
            self.ids.container.add_widget(MDLabel(text='An unknown error occured please contact!', halign='center', theme_text_color='Primary'))
            self.ids.container.add_widget(Widget())
            toast('File not found')


    def get_images(self):
        # extract the file name from the workbook
        file_name= self.workbook_active.split('.')[0]
        # get data from scheme.json and stored it as dictionary
        dic = {}
        with open('scheme.json') as f:
            data = json.load(f)['classes']
            for d in data:
                if d['name'] == file_name:
                    dic = d
                    break
        development_pages = [d["development_goal"] for d in dic['development_page']]
        # get the sheets in the workbook
        # start editing a pdf
        pdf = FPDF()
        sheets = [sheet.title for sheet in self.workbook.worksheets]
        for sheet_name in sheets:
            if sheet_name in dic:
                sheet = self.workbook[sheet_name]
                fields = dic[sheet_name]
                attr = fields['report_fields']
                data = {'request': 'image'}
                headers = {'Authorization': f'Token {get_stored_token()}'}
                image_url = fields['page_background']
                new_url = url + image_url
                response = requests.get(new_url, data=data, headers=headers)

                values = self.get_values_from_sheet(sheet, self.selected_row)
                print(values)
                # get image from the response
                image = response.content
                with open('resources/' + sheet_name + '.jpg', 'wb') as f:
                    # save the image
                    f.write(image)
                # set image as pdf background
                pdf.add_page()
                # set the image to fit exactly the page
                pdf.image('resources/' + sheet_name + '.jpg', x=0, y=0, w=210, h=297)
                # set the font
                pdf.set_font("helvetica", size=17)
                # set the position of the text
                for field in attr:
                    if field['type_of_field'] != 'image':
                        # set the position of the text
                        pdf.set_xy(field['position_x'], field['position_y'])
                        # add the text to the pdf from values if its not none else add empty string
                        if field['multi_field']:
                            pdf.multi_cell(field['width'] if field['width'] else 200, field['height'] if field['height'] else 10,
                                           values[field['name']] if values[field['name']] is not None else "")
                        else:
                            pdf.cell(field['width'] if field['width'] else 200, field['height'] if field['height'] else 10,
                                 values[field['name']] if values[field['name']] is not None else "")
                    else:
                        # set the position of the image
                        pdf.set_xy(field['position_x'], field['position_y'])
                        # add the image to the pdf
                        pdf.image('resources/' + sheet_name + '.jpg', x=field['position_x'], y=field['position_y'],
                                  w=field['width'], h=field['height'])
            elif sheet_name in development_pages:
                new_url = url+dic["default_background"]
                headers = {'Authorization': f'Token {get_stored_token()}'}
                response = requests.get(new_url,  headers=headers)
                image = response.content
                with open('resources/default_background.jpg', 'wb') as f:
                    f.write(image)
                pdf.add_page()
                pdf.image('resources/default_background.jpg', x=0, y=0, w=210, h=297)
                pdf.set_font("helvetica", size=17)
                pdf.set_xy(0,0)
                print('development page')


        pdf.output("resources/" + file_name + ".pdf")
        

    def get_values_from_sheet(self,sheet, selected_row):
        values = {}
        col = 1
        while col <= sheet.max_column:
            values[sheet.cell(1, col).value] = sheet.cell(selected_row, col).value
            col += 1
        return values


class AddScreen(Screen):
    def on_enter(self, *args):
        self.values = []
        self.ids.container.clear_widgets()
        self.get_xlsx_files()

    def get_xlsx_files(self):
        files = glob.glob('resources/*.xlsx')
        dropdown_items = [os.path.basename(f) for f in files]
        self.add_buttons(dropdown_items)

    def add_buttons(self, files):
        widge = Widget()
        self.ids.container.add_widget(widge)
        for file in files:
            button = MDRaisedButton(text=file, on_release=self.on_button_click, pos_hint={"center_x": 0.5})
            self.ids.container.add_widget(button)
        widge = Widget()
        self.ids.container.add_widget(widge)

    def on_button_click(self, instance):
        # remover everything inside the container
        self.ids.container.clear_widgets()
        # Create a ScrollView
        scroll_view = ScrollView(do_scroll_x=False, size_hint=(None, None), size=(400, 450), pos_hint={"center_x": 0.5})
        # Create a BoxLayout inside the ScrollView
        box_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))
        scroll_view.add_widget(box_layout)

        # open the file name instance.text
        self.workbook_active = instance.text
        workbook = load_workbook(filename=f'resources/{instance.text}')
        # get the first sheet
        sheets = [sheet.title for sheet in workbook.worksheets]

        # Create a list to hold the sheets
        self.sheets = sheets
        self.workbook = workbook
        self.current_sheet_index = 0

        # Create MDTextField for each cell in the first row of the first sheet
        self.create_text_fields(box_layout, self.current_sheet_index)

        # Add the ScrollView to the container
        self.ids.container.add_widget(Widget())
        self.ids.container.add_widget(scroll_view)
        self.ids.container.add_widget(Widget())

    def create_button_fields(self, box_layout, sheet_index):
        # Clear the BoxLayout
        box_layout.clear_widgets()
        self.ids.container.clear_widgets()
        # Get the current sheet
        sheet = self.sheets[sheet_index]
        worksheet = self.workbook[sheet]

        # Get the first row
        row = worksheet[1]
        val = []

        # Create a button for each cell in the row
        for i in range(0, len(row), 2):
            cell1 = row[i]
            cell2 = row[i+1]
            if cell1.value and cell2.value:
                common_text = get_common_text(cell1.value, cell2.value)
                component = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                label = MDLabel(text=common_text)
                button1 = MDRaisedButton(text='Term 1')
                button2 = MDRaisedButton(text='Term 2')
                component.add_widget(label)
                component.add_widget(button1)
                component.add_widget(button2)
                box_layout.add_widget(component)

        next_button = MDRaisedButton(text='Next', on_release=self.on_next_button_click, pos_hint={"center_x": 0.5})
        box_layout.add_widget(next_button)

    def create_text_fields(self, box_layout, sheet_index):
        # Clear the BoxLayout
        box_layout.clear_widgets()
        self.ids.container.clear_widgets()
        # Get the current sheet
        sheet = self.sheets[sheet_index]
        worksheet = self.workbook[sheet]

        # Get the first row
        row = worksheet[1]
        val = []

        # Create a MDTextField for each cell in the row
        for cell in row:
            if cell.value:
                text_field = MDTextField(hint_text=str(cell.value))
                box_layout.add_widget(text_field)

        next_button = MDRaisedButton(text='Next', on_release=self.on_next_button_click, pos_hint={"center_x": 0.5})
        box_layout.add_widget(next_button)

    def on_next_button_click(self, instance):
        # Increment the current sheet index
        self.current_sheet_index += 1
        # iterate throught the text fields and get the values
        value_li = []
        for child in self.ids.container.children:
            if isinstance(child, ScrollView):
                for widget in child.children:
                    if isinstance(widget, BoxLayout):
                        for text_field in widget.children:
                            if isinstance(text_field, MDTextField):
                                value_li.append(text_field.text)
        self.values.append(value_li[::-1])

        # Clear the container
        self.ids.container.clear_widgets()
        # Create a ScrollView
        scroll_view = ScrollView(do_scroll_x=False, size_hint=(None, None), size=(400, 450), pos_hint={"center_x": 0.5})
        # Create a BoxLayout inside the ScrollView
        box_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))
        scroll_view.add_widget(box_layout)

        # If there are more sheets, create text fields for the next sheet
        if self.current_sheet_index < len(self.sheets):
            if self.sheets[self.current_sheet_index] in ['cover_page','first_page']:
                self.create_text_fields(box_layout, self.current_sheet_index)
            else:
                self.create_button_fields(box_layout, self.current_sheet_index)
            self.ids.container.add_widget(Widget())
            self.ids.container.add_widget(scroll_view)
            self.ids.container.add_widget(Widget())
        else:
            #display its done and add a home button
            self.ids.container.clear_widgets()
            self.ids.container.add_widget(Widget())
            self.ids.container.add_widget(MDLabel(text='Done', halign='center', theme_text_color='Primary'))
            self.ids.container.add_widget(Widget())
            for sheet, value in zip(self.sheets, self.values):
                worksheet = self.workbook[sheet]
                worksheet.append(value)
            self.workbook.save(f'resources/{self.workbook_active}')


#             open the file and write the values


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__()

    def build(self):
        global url
        self.url = url
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(EditScreen(name='edit'))
        self.sm.add_widget(PrintScreen(name='print'))
        self.sm.add_widget(AddScreen(name='add'))

        # Create or connect to the SQLite database
        # self.conn = sqlite3.connect('mydatabase.db')
        # self.cursor = self.conn.cursor()

        # # Create a table if it doesn't exist
        # self.cursor.execute('''CREATE TABLE IF NOT EXISTS Person (
        #                                id INTEGER PRIMARY KEY,
        #                                name TEXT,
        #                                age INTEGER)''')
        # self.cursor.execute('''CREATE TABLE IF NOT EXISTS Cookies (
        #                         Name TEXT PRIMARY KEY,
        #                         Value TEXT
        #     )''')
        # self.conn.commit()
        data = {"request": "access"}
        # cookies = {"sessionid": get_sessionid(self.cursor)}
        headers = {'Authorization': f'Token {get_stored_token()}'}
        response = requests.post(url + "data/", headers=headers, data=data)
        # response = requests.post(url, data=data, cookies=cookies)
        if response.status_code == 200:
            self.sm.current = 'home'
        return self.sm

    def on_login(self, username, password):
        # API endpoint
        url = self.url + "login/"

        # Data to be sent to the API
        data = {"username": username, "password": password}
        # Send a post request to the API
        response = requests.post(url, data=data)
        if response.status_code == 200:
            # Assuming the token is returned in the response JSON
            response_json = response.json()
            new_token = response_json.get('token')
            if new_token:
                store_token(new_token)
            else:
                print("Token not found in the response.")
        else:
            print("Login failed. Status code:", response.status_code)

        # if 'sessionid' in response.cookies:
        #     sessionid = response.cookies['sessionid']
        #     self.cursor.execute("INSERT OR REPLACE INTO Cookies (Name, Value) VALUES (?, ?)", ("sessionid", sessionid))

        # If the response status code is 200 (HTTP OK), switch to the home screen
        if response.status_code == 200:
            # url = "http://127.0.0.1:8000/data/"
            # cookies = {"sessionid": get_sessionid(self.cursor)}
            # data = {"request":"schema"}
            self.sm.current = 'home'
        else:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Invalid Username or Password",
                ),
                MDSnackbarActionButton(
                    text="DISMISS",
                    on_release=lambda *args: snackbar.dismiss(),
                    theme_text_color="Custom",
                    text_color="#8E353C",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                md_bg_color="#E8D8D7",
            )
            snackbar.open()

    def logout(self):
        self.sm.current = 'login'
        #     clear the username and password fields
        url = self.url + "data/"
        data = {"request": "logout"}
        # cookies = {"sessionid": get_sessionid(self.cursor)}
        headers = {'Authorization': f"Token {get_stored_token()}"}
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            store_token("")
        self.sm.get_screen('login').ids['username'].text = ''
        self.sm.get_screen('login').ids['password'].text = ''

    def go_home(self):
        self.sm.current = 'home'


def store_token(token):
    with open('token.json', 'w') as f:
        json.dump({'token': token}, f)


def get_stored_token():
    try:
        with open('token.json', 'r') as f:
            data = json.load(f)
            return data.get('token')
    except FileNotFoundError:
        return ""

def get_common_text(text1, text2):
    text1 = text1.split(' ')
    text2 = text2.split(' ')
    common_text = []
    for t1, t2 in zip(text1, text2):
        if t1 == t2:
            common_text.append(t1)
        else:
            break
    return ' '.join(common_text).strip('term').strip()

# get the scheme from the server and store it if its updated
def get_data_scheme():
    global url
    data = {"request": "scheme"}
    headers = {'Authorization': f'Token {get_stored_token()}'}
    response = requests.post(url + "data/", headers=headers, data=data)
    if response.status_code == 200:
        response_json = response.json()
        new_scheme = {"classes": response_json.get("classes")}
        if os.path.exists('scheme.json'):
            with open('scheme.json', 'r') as f:
                old_scheme = json.load(f)
            if old_scheme != new_scheme:
                print("Database scheme has changed.")
                update_database(new_scheme)
            else:
                print("Database scheme is up-to-date.")
        else:
            with open('scheme.json', 'w') as f:
                json.dump(new_scheme, f)
            create_database()
    else:
        print("Failed to get the scheme")



def update_database(new_scheme):
    print("Updating the database")
    with open('scheme.json', 'w') as f:
        json.dump(new_scheme, f)


def create_database():
    print("Creating the database")
    with open('scheme.json', 'r') as f:
        scheme = json.load(f)
        classes = scheme['classes']
        for cls in classes:
            key = cls['name']
            # check if file exists
            file_path = f'resources' + '/' + key + '.xlsx'
            if os.path.exists(file_path):
                workbook = load_workbook(filename=file_path)
            else:
                workbook = Workbook()
                workbook.save(file_path)
            values = ['cover_page', 'first_page','development_page']
            for value in values:
                if value in ['cover_page','first_page']:
                    worksheet = workbook[value] if value in workbook else None
                    # If the worksheet does not exist, create a new one
                    if worksheet is None:
                        worksheet = workbook.create_sheet(value)
                    sub = cls[value]['report_fields']
                    i = 0
                    for s in sub:
                        worksheet.cell(row=1, column=i + 1, value=s['name'])
                        i += 1
                elif value=='development_page':
                    sub = cls[value]
                    for s in sub:
                        worksheet = workbook[s['development_goal']] if s['development_goal'] in workbook else None
                        # If the worksheet does not exist, create a new one
                        if worksheet is None:
                            worksheet = workbook.create_sheet(s['development_goal'])
                        sub_li=s['sections']
                        i = 0
                        for sub in sub_li:
                            li=sub['learning_outcome']
                            for l in li:
                                worksheet.cell(row=1, column=i + 1, value=l['code']+" term 1")
                                worksheet.cell(row=1, column=i+2, value=l['code']+" term 2")
                                i += 2
            workbook.save(file_path)


MainApp().run()
