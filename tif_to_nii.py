
import SimpleITK as sitk
from PIL import Image
import sys
import os
import glob
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
from progress.bar import IncrementalBar

filepath = r'../chunk_old/Dry(Frozen)/'
savepath = r'./Dry(Frozen)_out/'
tifpath = r'./out_tif/'


'''
Image Reconstruction
'''


def crop_roi(img):
    #image = cv2.imread(img)
    y = 1900  # y축 시작지점
    x = 1600  # x축 시작지점
    h = 1200  # 최종 - y축. 즉 이동거리
    w = 1000  # 최종 - x축, 즉 이동거리
    cropped = img.crop((1300, 1500, 2800, 3100))
    return cropped


def tif_hu_threshold(val):
    hu = val * 0.0335627 - 1024
    return np.int32(hu)


def Rescale(img):
    data = img
    data = crop_roi(data)
    data = np.vectorize(tif_hu_threshold)(data)

    return img


def downsamplePatient(original_CT, resize_factor):

    dimension = original_CT.GetDimension()
    reference_physical_size = np.zeros(original_CT.GetDimension())
    reference_physical_size[:] = [(sz-1)*spc if sz*spc > mx else mx for sz, spc, mx in zip(
        original_CT.GetSize(), original_CT.GetSpacing(), reference_physical_size)]

    reference_origin = original_CT.GetOrigin()
    reference_direction = original_CT.GetDirection()

    reference_size = [round(sz/resize_factor) for sz in original_CT.GetSize()]
    reference_spacing = [
        phys_sz/(sz-1) for sz, phys_sz in zip(reference_size, reference_physical_size)]

    reference_image = sitk.Image(reference_size, original_CT.GetPixelIDValue())
    reference_image.SetOrigin(reference_origin)
    reference_image.SetSpacing(reference_spacing)
    reference_image.SetDirection(reference_direction)

    reference_center = np.array(reference_image.TransformContinuousIndexToPhysicalPoint(
        np.array(reference_image.GetSize())/2.0))

    transform = sitk.AffineTransform(dimension)
    transform.SetMatrix(original_CT.GetDirection())

    transform.SetTranslation(
        np.array(original_CT.GetOrigin()) - reference_origin)

    centering_transform = sitk.TranslationTransform(dimension)
    img_center = np.array(original_CT.TransformContinuousIndexToPhysicalPoint(
        np.array(original_CT.GetSize())/2.0))
    centering_transform.SetOffset(
        np.array(transform.GetInverse().TransformPoint(img_center) - reference_center))
    centered_transform = sitk.CompositeTransform([centering_transform])
    # centered_transform.AddTransform(centering_transform)

    # sitk.Show(sitk.Resample(original_CT, reference_image, centered_transform, sitk.sitkLinear, 0.0))

    return sitk.Resample(original_CT, reference_image, centered_transform, sitk.sitkLinear, 0.0)


def main():
    _images = []
    total_count = 0
    refactor_val = 2.0

    sample = sitk.ReadImage(
        filepath + 'Dry(Frozen)_rec00001054.tif', imageIO="TIFFImageIO")
    spacing = sample.GetSpacing()[0]

    for root, dirs, files in os.walk(filepath):
        total_count = len(files)

    # bar = IncrementalBar(
    #     f'[+] 🏗 {total_count} Generating new Tif...', max=total_count)
    # for counter, file in enumerate(sorted(glob.glob(filepath + '*.tif'))):
    #     img = Image.open(file)
    #     r = crop_roi(img)
    #     r.save(tifpath + '/' + f'{counter:07}' + '.tif')
    #     bar.next()
    # bar.finish()

    bar = IncrementalBar(
        f'[+] 📐 {total_count} Changing threshold ...', max=total_count)
    for counter, file in enumerate(sorted(glob.glob(tifpath + '*.tif'))):
        im = sitk.ReadImage(file, imageIO="TIFFImageIO")

        # Resampling goes here
        downsample_im = downsamplePatient(im, refactor_val)
        # print(downsample_im.GetSpacing())
        spacing = downsample_im.GetSpacing()[0]

        im_arr = sitk.GetArrayFromImage(downsample_im)
        new_im = sitk.GetImageFromArray(np.vectorize(tif_hu_threshold)(im_arr))
        _images.append(new_im)

        # print(spacing)

        bar.next()
    bar.finish()

    print('[+] 🔗 Joining Images ...')
    join_series = sitk.JoinSeries(_images)
    join_series.SetOrigin((0.0, 0.0, 0.0))

    join_series.SetSpacing((spacing, spacing, 1))
    print(f"🚀🚀🚀🚀🚀{join_series.GetSpacing()}")

    print('[+] 💻 Creating joined series')
    sitk.WriteImage(join_series, f'./output_refactor{int(refactor_val)}.nii')

    print('[+] ✨ Creating Nifti successful')


if __name__ == '__main__':
    main()
