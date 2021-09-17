from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import glob


class Page1(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.setup()

    def setup(self):
        # file buttons
        self.loaded_directory = StringVar()
        self.loaded_directory.trace_add('write', self.callback)
        self.loadpath_entry = Entry(self, textvariable=self.loaded_directory)
        self.loadpath_button = Button(
            self, width=10, text="Load Path", command=self.get_load_path)

    
        # file lists
        self.file_frame = Frame(self)
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_rowconfigure(0, weight=1)

        scrollbar = Scrollbar(self.file_frame)
        scrollbar.grid(row=0, column=1, sticky='nse')

        self.listbox = Listbox(self.file_frame, borderwidth=0,
                               highlightthickness=0, yscrollcommand=scrollbar.set)
        # for line in range(1,1001):
        #    listbox.insert(line, str(line) + "/1000")
        self.listbox.grid(row=0, column=0, sticky='nwse')

        scrollbar["command"] = self.listbox.yview

        # next button
        sep = ttk.Separator(self, orient='horizontal')
        self.total_count = StringVar()
        self.total_label = Label(self, text="")
        self.next_button = Button(
            self, width=10, text="Next", state=DISABLED, command=self.next_button_handler)

        self.loadpath_entry.grid(row=0, column=0, sticky='we')
        self.loadpath_button.grid(row=0, column=1, sticky='e')
        
        self.file_frame.grid(row=2, column=0, columnspan=2,
                             padx=(10, 0), pady=10, sticky='nwse')
        sep.grid(row=3, column=0, columnspan=2, sticky='we')
        self.total_label.grid(row=4, column=0, padx=10, sticky='w')
        self.next_button.grid(row=4, column=1, pady=10, sticky='e')


    def get_load_path(self):
        '''
        Get absolute path of TIF images from filedialog.
        '''
        self.loadpath_entry.config(state='normal')
        filepath = filedialog.askdirectory(
            initialdir='../', title="Select file"
        )
        self.loadpath_entry.delete(0, END)
        self.loadpath_entry.insert(0, filepath)
        self.loadpath_entry.config(state='disabled')
        return

    

    def callback(self, var, idx, mode):
        '''
        Callback when file dialog is closed or file path is selected from filedialog
        '''
        if self.loaded_directory.get():
            self.tif_files = []
            self.tif_files += glob.glob(self.loaded_directory.get() + '/*.tif')
            self.tif_files += glob.glob(self.loaded_directory.get() + '/*.TIF')
            self.tif_files += glob.glob(self.loaded_directory.get() + '/*.tiff')
            self.tif_files += glob.glob(self.loaded_directory.get() + '/*.TIFF')

            self.tif_files.sort()
            self.controller.tif_images = self.tif_files

            for idx, file in enumerate(self.tif_files):
                self.listbox.insert(idx, file)

            self.total_label["text"] = "Total: " + \
                str(len(self.tif_files)) + " images"

            self.controller.tif_images = self.tif_files

        if self.loaded_directory.get():
            self.next_button["state"] = "active"

    def next_button_handler(self):
        '''
        - Change frame to Page 2.
        - Send visual path to Page 2.
        - Update initialized Page 2 with new variables.
        '''
        self.controller.tif_images = self.tif_files
        # self.controller.frames["Page2"].label["text"] = self.tif_files[0]

        # change data in page one.
        if self.tif_files:
            PAGE_TWO = self.controller.frames["Page2"]   # class Page2
            PAGE_TWO.visual_image_path = self.tif_files[int(
                len(self.tif_files)/2)]
            PAGE_TWO.set_page_2()
        else:
            self.total_label['text'] = "No tif files in current directory"

        self.controller.show_frame("Page2")

