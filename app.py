from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import glob
import cv2

import SimpleITK as sitk
import sys
import os
import glob
import sys
import numpy as np
import cv2


class SampleApp(Tk):
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
        self.save_directory = ''
        self.crop_size = (0, 0, 0, 0)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)

            self.frames[page_name] = frame  # frames["StartPage"] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # file buttons
        self.loaded_directory = StringVar()
        self.loaded_directory.trace_add('write', self.callback)
        self.loadpath_entry = Entry(self, textvariable=self.loaded_directory)
        self.loadpath_button = Button(
            self, width=10, text="Load Path", command=self.getLoadPath)

        self.saved_directory = StringVar()
        self.saved_directory.trace_add('write', self.callback)
        self.savepath_entry = Entry(self, textvariable=self.saved_directory)
        self.savepath_button = Button(
            self, width=10, text="Save path", command=self.getSavePath)

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
            self, width=10, text="Next", state=DISABLED, command=self.nextButtonHandler)

        self.loadpath_entry.grid(row=0, column=0, sticky='we')
        self.loadpath_button.grid(row=0, column=1, sticky='e')
        self.savepath_entry.grid(row=1, column=0, sticky='we')
        self.savepath_button.grid(row=1, column=1, sticky='e')
        self.file_frame.grid(row=2, column=0, columnspan=2,
                             padx=(10, 0), pady=10, sticky='nwse')
        sep.grid(row=3, column=0, columnspan=2, sticky='we')
        self.total_label.grid(row=4, column=0, padx=10, sticky='w')
        self.next_button.grid(row=4, column=1, pady=10, sticky='e')
        # file_list.grid(row=2,column=0, columnspan=2, sticky='we')

    def getLoadPath(self):
        self.loadpath_entry.config(state='normal')
        filepath = filedialog.askdirectory(
            initialdir='../', title="Select file"
        )
        self.loadpath_entry.delete(0, END)
        self.loadpath_entry.insert(0, filepath)
        self.loadpath_entry.config(state='disabled')
        return

    def getSavePath(self):
        self.savepath_entry.config(state='normal')
        filepath = filedialog.askdirectory(
            initialdir=".", title="Select file")
        self.savepath_entry.delete(0, END)
        self.savepath_entry.insert(0, filepath)
        self.savepath_entry.config(state='disabled')
        return

    def callback(self, var, idx, mode):
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

        if self.loaded_directory.get() and self.saved_directory.get():
            self.next_button["state"] = "active"

    def nextButtonHandler(self):
        self.controller.tif_images = self.tif_files
        # self.controller.frames["PageOne"].label["text"] = self.tif_files[0]

        # change data in page one.
        if self.tif_files:
            PAGE_ONE = self.controller.frames["PageOne"]   # class PageOne
            PAGE_ONE.visual_image_path = self.tif_files[int(
                len(self.tif_files)/2)]
            PAGE_ONE.setPageOne()
        else:
            self.total_label['text'] = "No tif files in current directory"

        self.controller.show_frame("PageOne")


class PageOne(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.controller = controller

        self.visual_image_path = ''
        self.RESIZE_FACTOR = 0.3

        # canvas
        self.canvas = Canvas(self, bg='gray', cursor='cross')

        # seperator
        sep = ttk.Separator(self, orient='horizontal')

        # next button
        self.next_button = Button(
            self, width=10, text="Next", command=self.nextButtonHandler)
        # box size validator
        self.box_size_label = Label(self, text='')
        # back button
        self.back_button = Button(
            self, width=10, text="Back", command=self.backButtonHandler)

        # position setup
        self.canvas.grid(row=0, column=0, columnspan=3, sticky='nsew')
        sep.grid(row=1, column=0, columnspan=3, sticky='we')
        self.back_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.box_size_label.grid(row=2, column=1, padx=10, sticky='e')
        self.next_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')

    def backButtonHandler(self):
        self.controller.show_frame("StartPage")

    def nextButtonHandler(self):
        # update controller data
        self.controller.show_frame("PageTwo")
        crop_size = [self.start_x, self.start_y, self.end_x, self.end_y]
        self.controller.crop_size = tuple(map(lambda x : int(x / self.RESIZE_FACTOR), crop_size))
        self.controller.resize_factor = self.RESIZE_FACTOR
        
        PAGE_TWO = self.controller.frames["PageTwo"]
        PAGE_TWO.setPageTwo()

    def resizeImage(self, img):
        img_w, img_h = img.size
        print(460 / img_h)

        self.RESIZE_FACTOR = 460 / img_h
        img = cv2.imread(self.visual_image_path)
        img = cv2.resize(img, (0, 0), fx=self.RESIZE_FACTOR,
                         fy=self.RESIZE_FACTOR)
        b, g, r = cv2.split(img)
        img = cv2.merge((r, g, b))
        im = Image.fromarray(img)
        return im

    def setPageOne(self):
        # self.canvas["text"] = self.visual_image_path
        print(self.visual_image_path)
        img = Image.open(self.visual_image_path)
        img = self.resizeImage(img)
        img_w, img_h = img.size

        my_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(320, 230, image=my_image, anchor='center')
        self.canvas.width = img_w
        self.canvas.height = img_h
        self.canvas.image = my_image

        # drawing rectangle
        self.x = self.y = 0
        self.rect = ''
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_press)
        self.canvas.bind('<B1-Motion>', self.on_press_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_leave)

    def on_mouse_press(self, e):
        if self.rect:
            self.canvas.delete(self.rect)
        self.start_x = e.x
        self.start_y = e.y

        self.rect = self.canvas.create_rectangle(
            self.x, self.y, 1, 1, width=2, outline='yellow', fill="")

    def on_press_move(self, e):
        self.end_x, self.end_y = (e.x, e.y)
        self.canvas.coords(self.rect, self.start_x,
                           self.start_y, self.end_x, self.end_y)

    def on_mouse_leave(self, e):
        self.box_size_label['text'] = str(int((self.end_x - self.start_x) / self.RESIZE_FACTOR)) + \
            " X " + \
            str(int(
                (self.end_y - self.start_y) / self.RESIZE_FACTOR))


def fetch_filename(filepath):
    # only opt out filename
    fp = [os.path.basename(x).replace('.tiff', '').replace('.tiff', '').replace(
        '.tif', '').replace('.TIFF', '').replace('.TIF', '') for x in filepath]

    filelist = []
    for f in fp:
        filelist.append(''.join([s for s in f if not s.isdigit()]))

    fileset = list(set(filelist))

    if len(fileset) > 1:
        print('Error: All file names have to match')
        exit(0)
    else:
        return fileset[0]


class PageTwo(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.tif_images = []
        self.image_format_list = [
            'nia', 'nii', 'nii.gz', 'hdr', 'img', 'img.gz'
        ]  # etc

        self.heading = Label(self, text=" Export 🚀 ", font=('Arial', 20))

        # file name
        self.filename = ''
        self.filename_label = Label(self, text='Filename')
        self.filename_entry = Entry(self)
        variable = StringVar(self)
        variable.set(self.image_format_list[1])
        self.filename_type = OptionMenu(
            self, variable, *self.image_format_list)
        # self.filename_type.config(width=20)

        # image size
        self.img_x1_label = Label(self, text='Image Position start x')
        self.img_y1_label = Label(self, text='Image Position start y')
        self.img_x2_label = Label(self, text='Image Position end x')
        self.img_y2_label = Label(self, text='Image Position end y')
        self.img_x1_entry = Entry(self)
        self.img_y1_entry = Entry(self)
        self.img_x2_entry = Entry(self)
        self.img_y2_entry = Entry(self)

        # buttons
        sep = ttk.Separator(self, orient='horizontal')
        self.next_button = Button(self, width=10, text="Start", command=self.nextButtonHandler)
        self.box_size_label = Label(self, text='')
        # back button
        self.back_button = Button(self, width=10, text="Back", command=self.backButtonHandler)

        # position setup
        self.heading.grid(row=0, column=0, pady=10)
        self.filename_label.grid(row=1, column=0)
        self.filename_entry.grid(row=1, column=1)
        self.filename_type.grid(row=1, column=2)

        self.img_x1_label.grid(row=2, column=0)
        self.img_y1_label.grid(row=3, column=0)
        self.img_x2_label.grid(row=4, column=0)
        self.img_y2_label.grid(row=5, column=0)
        self.img_x1_entry.grid(row=2, column=1)
        self.img_y1_entry.grid(row=3, column=1)
        self.img_x2_entry.grid(row=4, column=1)
        self.img_y2_entry.grid(row=5, column=1)

        sep.grid(row=6, column=0, columnspan=2, sticky='swe')
        self.back_button.grid(row=7, column=0, padx=10, pady=10, sticky='sw')
        self.box_size_label.grid(row=7, column=1, padx=10, sticky='se')
        self.next_button.grid(row=7, column=2, padx=10, pady=10, sticky='se')

    def setPageTwo(self):

        self.tif_images = self.controller.tif_images
        text = str(len(self.tif_images))

        self.filename_entry.delete(0, END)
        self.img_y1_entry.delete(0, END)
        self.img_x1_entry.delete(0, END)
        self.img_x2_entry.delete(0, END)
        self.img_y2_entry.delete(0, END)

        self.filename_entry.insert(0, fetch_filename(self.tif_images))
        self.img_x1_entry.insert(0, self.controller.crop_size[0])
        self.img_y1_entry.insert(0, self.controller.crop_size[1])
        self.img_x2_entry.insert(0, self.controller.crop_size[2])
        self.img_y2_entry.insert(0, self.controller.crop_size[3])

        # self.label['text'] = "Transform " + text + "images"
        pass

    def backButtonHandler(self):
        self.controller.show_frame("PageOne")

    def nextButtonHandler(self):
        # start the process.
        pass

if __name__ == "__main__":
    app = SampleApp()
    app.title("tk")
    app.geometry("640x460+100+100")
    app.mainloop()
