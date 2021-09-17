from tkinter import *
from tkinter import ttk

from PIL import ImageTk, Image

import cv2


class Page2(Frame):

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
            self, width=10, text="Next", command=self.next_button_handler)
        # box size validator
        self.box_size_label = Label(self, text='')
        # back button
        self.back_button = Button(
            self, width=10, text="Back", command=self.back_button_handler)

        # position setup
        self.canvas.grid(row=0, column=0, columnspan=3, sticky='nsew')
        sep.grid(row=1, column=0, columnspan=3, sticky='we')
        self.back_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.box_size_label.grid(row=2, column=1, padx=10, sticky='e')
        self.next_button.grid(row=2, column=2, padx=10, pady=10, sticky='e')

    def back_button_handler(self):
        '''
        Change frame to Page 1
        '''
        self.controller.show_frame("Page1")

    def next_button_handler(self):
        '''
        - Change frame to Page 2.
        - Pass data to parent
        - Update initialized Page 3 with new variables.
        '''
        # update controller data
        self.controller.show_frame("Page3")
        try:
            crop_size = [self.start_x, self.start_y, self.end_x, self.end_y]
        except:
            print("No image crop")
            crop_size = [0, 0, self.img.size[0], self.img.size[1]]

        self.controller.crop_size = tuple(
            map(lambda x: int(x / self.RESIZE_FACTOR), crop_size))
        self.controller.resize_factor = self.RESIZE_FACTOR

        PAGE_THREE = self.controller.frames["Page3"]
        PAGE_THREE.set_page_3()

    def resize_image(self, img):
        '''
        Resize image to fit canvas
        '''
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

    def set_page_2(self):
        '''
        Re-initialize the frame with data obtained from Page 1
        '''
        # self.canvas["text"] = self.visual_image_path
        print(self.visual_image_path)
        self.img = Image.open(self.visual_image_path)
        self.img = self.resize_image(self.img)
        img_w, img_h = self.img.size

        my_image = ImageTk.PhotoImage(self.img)
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

    # Mouse controller

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
