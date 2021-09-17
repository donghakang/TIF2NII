

import SimpleITK as sitk
from PIL import Image
import sys
import os
import glob
import sys
from SimpleITK.SimpleITK import JoinSeries
import numpy as np
import cv2
import matplotlib.pyplot as plt

def crop_roi(img, position):
    '''
    img is sitk format
    '''
    img_w, img_h = img.GetSize()
    crop_filter = sitk.CropImageFilter()
    crop_filter.SetLowerBoundaryCropSize([position[0], position[1], 0])
    crop_filter.SetUpperBoundaryCropSize([img_w - position[2], img_h - position[3], 1])
    cropped_img = crop_filter.Execute(img)
    cropped_img.SetSpacing([1, 1])
    cropped_img.SetOrigin([0, 0])
    return cropped_img


def tif_hu_threshold(val):
    hu = val * 0.0335627 - 1024
    return np.int32(hu)


def rescale(img, position):
    data = img
    data = crop_roi(data, position)
    data = np.vectorize(tif_hu_threshold)(data)

    return img


def downsample_patient(original_CT, resize_factor):

    dimension = original_CT.GetDimension()
    reference_physical_size = np.zeros(original_CT.GetDimension())
    reference_physical_size[:] = [(sz-1)*spc if sz*spc > mx else mx for sz, spc, mx in zip(
        original_CT.GetSize(), original_CT.GetSpacing(), reference_physical_size)]

    reference_origin = original_CT.GetOrigin()
    reference_direction = original_CT.GetDirection()

    reference_size = [round(sz * resize_factor) for sz in original_CT.GetSize()]
    reference_spacing = [
        phys_sz/(sz-1) for sz, phys_sz in zip(reference_size, reference_physical_size)]

    reference_image = sitk.Image(reference_size, original_CT.GetPixelIDValue())
    reference_image.SetOrigin(reference_origin)
    reference_image.SetSpacing(reference_spacing)
    reference_image.SetDirection(reference_direction)

    reference_center = np.array(reference_image.TransformContinuousIndexToPhysicalPoint(
        np.array(reference_image.GetSize()) * resize_factor))

    transform = sitk.AffineTransform(dimension)
    transform.SetMatrix(original_CT.GetDirection())

    transform.SetTranslation(
        np.array(original_CT.GetOrigin()) - reference_origin)

    centering_transform = sitk.TranslationTransform(dimension)
    img_center = np.array(original_CT.TransformContinuousIndexToPhysicalPoint(
        np.array(original_CT.GetSize()) * resize_factor))
    centering_transform.SetOffset(
        np.array(transform.GetInverse().TransformPoint(img_center) - reference_center))
    centered_transform = sitk.CompositeTransform([centering_transform])
    # centered_transform.AddTransform(centering_transform)

    # sitk.Show(sitk.Resample(original_CT, reference_image, centered_transform, sitk.sitkLinear, 0.0))

    return sitk.Resample(original_CT, reference_image, centered_transform, sitk.sitkLinear, 0.0)


def main(filename, loadpath, savepath, position, refactor):
    _images = []

    for file in loadpath:
        im = sitk.ReadImage(file, imageIO="TIFFImageIO")
        
        # Resampling goes here
        downsample_im = downsample_patient(im, refactor)
        # print(downsample_im.GetSpacing())
        spacing = downsample_im.GetSpacing()[0]

        im_arr = sitk.GetArrayFromImage(downsample_im)
        new_im = sitk.GetImageFromArray(np.vectorize(tif_hu_threshold)(im_arr))
        _images.append(new_im)

    join_series = sitk.JoinSeries(_images)
    join_series.SetOrigin((0.0, 0.0, 0.0))

    join_series.SetSpacing((spacing, spacing, 1))
    print(f"🚀🚀🚀🚀🚀{join_series.GetSpacing()}")

    print('[+] 💻 Creating joined series')
    sitk.WriteImage(join_series, savepath + '/' + filename)
    print('[+] ✨ Creating Nifti successful')


def run(filename, loadpath, savepath, position, refactor):
    main(filename, loadpath, savepath, position, refactor)
