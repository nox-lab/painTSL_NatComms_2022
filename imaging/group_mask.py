"""create group mask"""
import os,json,glob,sys
from glob import glob
import nilearn

brainmasks = glob('/data/sub-*/func/*brain_mask.nii.gz')

# mean of all masks
mean_mask = nilearn.image.mean_img(brainmasks)

# binarised mask
group_mask = nilearn.image.math_img("a>=0.1", a=mean_mask)

# saving group mask
group_mask.to_filename('/data/group_mask.nii.gz')