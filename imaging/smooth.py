"""smoothing script"""

from os.path import join as opj
import os
import json
from nipype.interfaces.fsl import (BET, ExtractROI, FAST, FLIRT, ImageMaths,ApplyMask, MCFLIRT, SliceTimer, Threshold, IsotropicSmooth)
from nipype.interfaces.spm import Smooth, SliceTiming
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.algorithms.rapidart import ArtifactDetect
from nipype import Workflow, Node

# Set the way matlab should be called
# import nipype.interfaces.matlab as mlab      # how to run matlab
# mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")

# In case a different path is required
# mlab.MatlabCommand.set_default_paths('/software/matlab/spm12b/spm12b_r5918')

# without slicetime, without mask
def define_workflow(subject_list, run_list, experiment_dir, output_dir):
    """run the smooth workflow given subject and runs"""
    # ExtractROI - skip dummy scans
    extract = Node(ExtractROI(t_min=4, t_size=-1, output_type='NIFTI'),
               name="extract")
    
    # Smooth - image smoothing
    smooth = Node(Smooth(fwhm=[8,8,8]), name="smooth")
    
    # Mask - applying mask to smoothed
    # mask_func = Node(ApplyMask(output_type='NIFTI'),
                    # name="mask_func")
    
    # Infosource - a function free node to iterate over the list of subject names
    infosource = Node(IdentityInterface(fields=['subject_id','run_num']),
                      name="infosource")
    infosource.iterables = [('subject_id', subject_list),
                           ('run_num', run_list)]

    # SelectFiles - to grab the data (alternativ to DataGrabber)
    func_file = opj('sub-{subject_id}', 'func',
                    'sub-{subject_id}_task-tsl_run-{run_num}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
    templates = {'func': func_file}
    selectfiles = Node(SelectFiles(templates,
                        base_directory=data_dir),
                       name="selectfiles")

    # Datasink - creates output folder for important outputs
    datasink = Node(DataSink(base_directory=experiment_dir,
                             container=output_dir),
                    name="datasink")

    ## Use the following DataSink output substitutions
    substitutions = [('_subject_id_', 'sub-'),
                     ('ssub', 'sub'),
                     ('_space-MNI152NLin2009cAsym_desc-preproc_', '_fwhm-8_'),
                     ('_fwhm_', ''),
                     ('_roi', '')
                    ]
    substitutions += [('_run_num_%s' % r, '') for r in run_list]
    datasink.inputs.substitutions = substitutions
    
    # Create a preprocessing workflow
    preproc = Workflow(name='preproc')
    preproc.base_dir = opj(experiment_dir, working_dir)
    
    # Connect all components of the preprocessing workflow (spm smooth)
    preproc.connect([(infosource, selectfiles, [('subject_id', 'subject_id'),('run_num', 'run_num')]),
                 (selectfiles, extract, [('func', 'in_file')]),
                 (extract, smooth, [('roi_file', 'in_files')]),
                 (smooth, datasink, [('smoothed_files', 'preproc.@smooth')])
                ])
    return preproc

def list_subject(data_dir='/data'):
    """list all available subjects"""
    sj_ls = []
    for f in os.listdir(data_dir):
        if f.startswith('sub') and (not f.endswith('.html')):
            sj_ls.append(f.split('-')[1])
    return sj_ls

if __name__ == '__main__':
    experiment_dir = '/output'
    output_dir = 'smooth_nomask'
    working_dir = 'workingdir'
    data_dir = '/data'

    for sj in list_subject(data_dir=data_dir):
        fl = []
        for f in os.listdir('/data/sub-'+sj+'/func'):
            if f.endswith('bold.nii.gz'):
                fl.append(f[20])
        print(f'subject %s has %s sessions.' % (sj, fl))
        # run
        preproc = define_workflow([sj], fl, experiment_dir, output_dir)
        preproc.run('MultiProc')#, plugin_args={'n_procs': 4})