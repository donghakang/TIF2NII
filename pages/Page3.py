
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import SimpleITK as sitk
import os
import numpy as np

import logic.converter as nifti_converter


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


class Page3(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup()

    def setup(self):
        '''
        setup GUI
        '''
        self.tif_images = []
        self.image_format_list = [
            'nia', 'nii', 'nii.gz', 'hdr', 'img', 'img.gz'
        ]  # etc

        self.heading = Label(self, text="Export", font=('Arial', 20))

        # information frame
        self.info_frame = Frame(self)

        # file name
        self.filename = ''
        self.filename_label = Label(self.info_frame, text='Filename')
        self.filename_entry = Entry(self.info_frame)

        self.file_type_variable = StringVar(self)
        self.file_type_variable.set(self.image_format_list[1])
        self.file_type_menu = OptionMenu(
            self.info_frame, self.file_type_variable, *self.image_format_list, command=self.callback)
        self.file_type_menu.config(width=5)
        self.file_type_variable.set('nii')
        self.file_type = 'nii'

        self.savepath_entry = Entry(self.info_frame, state=DISABLED)
        self.savepath_button = Button(
            self.info_frame, width=10, text="Save path", command=self.get_save_path)

        # image size
        self.img_x1_label = Label(
            self.info_frame, text='Image Position start x')
        self.img_y1_label = Label(
            self.info_frame, text='Image Position start y')
        self.img_x2_label = Label(self.info_frame, text='Image Position end x')
        self.img_y2_label = Label(self.info_frame, text='Image Position end y')
        self.img_x1_entry = Entry(self.info_frame)
        self.img_y1_entry = Entry(self.info_frame)
        self.img_x2_entry = Entry(self.info_frame)
        self.img_y2_entry = Entry(self.info_frame)

        self.resize_label = Label(self.info_frame, text='Resize image factor')
        self.resize_entry = Entry(self.info_frame, text='1')

        # buttons
        sep = ttk.Separator(self, orient='horizontal')
        self.next_button = Button(
            self, width=10, text="Start", command=self.next_button_handler)
        self.progrees_label = Label(self, text='')
        # back button
        self.back_button = Button(
            self, width=10, text="Back", command=self.back_button_handler)

        # position setup
        self.savepath_entry.grid(row=0, column=0, columnspan=2, sticky='we')
        self.savepath_button.grid(row=0, column=2)
        self.filename_label.grid(row=1, column=0)
        self.filename_entry.grid(row=1, column=1, sticky='we')
        self.file_type_menu.grid(row=1, column=2)
        self.img_x1_label.grid(row=2, column=0, pady=(20, 0))
        self.img_y1_label.grid(row=3, column=0)
        self.img_x2_label.grid(row=4, column=0)
        self.img_y2_label.grid(row=5, column=0)
        self.img_x1_entry.grid(row=2, column=1, pady=(20, 0))
        self.img_y1_entry.grid(row=3, column=1)
        self.img_x2_entry.grid(row=4, column=1)
        self.img_y2_entry.grid(row=5, column=1)
        self.resize_label.grid(row=6, column=0, pady=(20, 0))
        self.resize_entry.grid(row=6, column=1, pady=(20, 0))

        self.heading.grid(row=0, column=0, pady=10, sticky='w')
        self.info_frame.grid(row=1, column=0, columnspan=3)

        sep.grid(row=2, column=0, columnspan=3, sticky='swe')
        self.back_button.grid(row=3, column=0, padx=10, pady=10, sticky='sw')
        self.progrees_label.grid(
            row=3, column=1, padx=10, pady=10, sticky='se')
        self.next_button.grid(row=3, column=2, padx=10, pady=10, sticky='se')

    def get_save_path(self):
        self.savepath_entry.config(state='normal')
        filepath = filedialog.askdirectory(
            initialdir=".", title="Select file")
        self.savepath_entry.delete(0, END)
        self.savepath_entry.insert(0, filepath)
        self.savepath_entry.config(state='disabled')
        return

    def callback(self, selection):
        self.file_type = selection
        pass

    def set_page_3(self):

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

    def error_check(self):
        # missing file name
        if not self.filename_entry.get():
            return "Filename missing"
        if not self.savepath_entry.get():
            return "Savepath missing"
        if not self.img_x1_entry.get():
            return "Image Position start x missing"
        if not self.img_y1_entry.get():
            return "Image Position start y missing"
        if not self.img_x2_entry.get():
            return "Image Position end x missing"
        if not self.img_y2_entry.get():
            return "Image Position end y missing"
        if not self.resize_entry.get():
            return "Resize image factor missing"

        # not integer
        if not self.img_x1_entry.get().isdigit():
            return "Image Position start x not a number"
        if not self.img_y1_entry.get().isdigit():
            return "Image Position start y not a number"
        if not self.img_x2_entry.get().isdigit():
            return "Image Position end x not a number"
        if not self.img_y2_entry.get().isdigit():
            return "Image Position end y not a number"

        try: 
            _resize = float(self.resize_entry.get())
        except:
            return "Resize image factor not a number (float)"            

        return ''


    def back_button_handler(self):
        self.controller.show_frame("Page2")

    def next_button_handler(self):
        # start the process.
        print('check error', self.error_check())
        if not self.error_check():

            filename = self.filename_entry.get() + "." + self.file_type
            loadpath = self.controller.tif_images
            savepath = self.savepath_entry.get()
            position = (int(self.img_x1_entry.get()), int(self.img_y1_entry.get()), int(
                self.img_x2_entry.get()), int(self.img_y2_entry.get()))
            refactor = float(self.resize_entry.get())

            num_files = len(loadpath)

            _images = []

            print('[+] 💻 Resizing the images ...')
            for idx, tif in enumerate(loadpath):
                im = sitk.ReadImage(tif, imageIO="TIFFImageIO")

                # crop image
                crop_im = nifti_converter.crop_roi(im, position)

                # resampling
                downsample_im = nifti_converter.downsample_patient(
                    crop_im, refactor)

                spacing = downsample_im.GetSpacing()[0]

                im_arr = sitk.GetArrayFromImage(downsample_im)
                new_im = sitk.GetImageFromArray(np.vectorize(
                    nifti_converter.tif_hu_threshold)(im_arr))
                _images.append(new_im)

                self.progrees_label['text'] = str(
                    idx) + '/' + str(num_files) + ' Completed ..'

            # print('[+] 🔗 Joining Images ...')
            join_series = sitk.JoinSeries(_images)
            join_series.SetOrigin((0.0, 0.0, 0.0))
            join_series.SetSpacing((spacing, spacing, 1))

            print('[+] 🔥 Creating joined series')
            sitk.WriteImage(join_series, savepath + '/' + filename)

            print('[+] 🎉 Creating Nifti successful ...')
            self.progrees_label['text'] = 'Complete!'

        else:
            self.progrees_label['text'] = self.error_check()
