def add_save_button(self):
        button = MDRaisedButton(text='Save PDF', on_release=self.open_file_manager, pos_hint={"center_x": 0.5})
        self.ids.container.add_widget(Widget())
        self.ids.container.add_widget(button)
        self.ids.container.add_widget(Widget())

    def open_file_manager(self, instance):
        # Open the default system file manager
        os.startfile(os.getcwd())

    def save_pdf(self, file_manager, path):
        # Save the generated PDF to the selected path
        file_name = self.workbook_active.split('.')[0]
        pdf_path = os.path.join(path, file_name + '.pdf')
        shutil.copyfile("resources/" + file_name + ".pdf", pdf_path)
        file_manager.close()

    def cancel_save(self, file_manager):
        # Handle cancel event of file manager
        file_manager.close()
