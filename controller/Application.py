from tkinter import *

from pages.Page1 import Page1
from pages.Page2 import Page2
from pages.Page3 import Page3


class Application(Tk):
    '''
    Main container that contains all the pages.
    '''

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tif_images = []

        self.frames = {}

        for page in (Page1, Page2, Page3):
            page_name = page.__name__
            frame = page(parent=container, controller=self)

            self.frames[page_name] = frame  # frames["Page1"] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Page1")

    def show_frame(self, page_name):
        '''
        Show a frame for the given page name
        '''
        frame = self.frames[page_name]
        frame.tkraise()
