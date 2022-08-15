"""All pain comparison as sanity check"""

import os,json,glob,sys
from os.path import join as opj
from nipype.interfaces.spm import Level1Design, EstimateModel, EstimateContrast, OneSampleTTestDesign, Threshold, TwoSampleTTestDesign
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces.fsl import Info
from nipype.algorithms.misc import Gunzip
from nipype import Workflow, Node
import nilearn.plotting
import numpy
import pandas as pd
import nibabel
import matplotlib.pyplot as plt

def first_level(TR, contrast_list, subject_list, 
                experiment_dir, output_dir, subjectinfo_func, working_dir='workingdir'):
    """define first level model"""
    # SpecifyModel - Generates SPM-specific Model
    modelspec = Node(SpecifySPMModel(concatenate_runs=False,
                                    input_units='secs',
                                    output_units='secs',
                                    time_repetition=TR,
                                    high_pass_filter_cutoff=128),
                                    name="modelspec")

    # Level1Design - Generates an SPM design matrix
    level1design = Node(Level1Design(bases={'hrf': {'derivs': [0, 0]}},
                                    timing_units='secs',
                                    interscan_interval=TR,
                                    model_serial_correlations='FAST'),
                                    name="level1design")

    # EstimateModel - estimate the parameters of the model
    level1estimate = Node(EstimateModel(estimation_method={'Classical': 1}),
                                    name="level1estimate")

    # EstimateContrast - estimates contrasts
    level1conest = Node(EstimateContrast(), name="level1conest")

    # Get Subject Info - get subject specific condition information
    getsubjectinfo = Node(Function(input_names=['subject_id'],
                                output_names=['subject_info'],
                                function=subjectinfo_func),
                        name='getsubjectinfo')

    # Infosource - a function free node to iterate over the list of subject names
    infosource = Node(IdentityInterface(fields=['subject_id',
                                                'contrasts'],
                                        contrasts=contrast_list),
                    name="infosource")
    infosource.iterables = [('subject_id', subject_list)]

    # SelectFiles - to grab the data (alternativ to DataGrabber)
    smooth_dir = opj(experiment_dir, 'smooth_nomask', 'preproc')
    templates = {'func': opj(smooth_dir, 'sub-{subject_id}',
                            '*run-*_fwhm-8_bold.nii')}

    selectfiles = Node(SelectFiles(templates,
                                base_directory=experiment_dir,
                                sort_filelist=True),
                    name="selectfiles")

    # Datasink - creates output folder for important outputs
    datasink = Node(DataSink(base_directory=experiment_dir,
                            container=output_dir),
                    name="datasink")

    # Use the following DataSink output substitutions
    substitutions = [('_subject_id_', 'sub-')]
    datasink.inputs.substitutions = substitutions

    # Initiation of the 1st-level analysis workflow
    l1analysis = Workflow(name='l1analysis')
    l1analysis.base_dir = opj(experiment_dir, working_dir)

    # Connect up the 1st-level analysis components
    l1analysis.connect([(infosource, selectfiles, [('subject_id', 'subject_id')]),
                        (infosource, getsubjectinfo, [('subject_id',
                                                    'subject_id')]),
                        (getsubjectinfo, modelspec, [('subject_info',
                                                    'subject_info')]),
                        (infosource, level1conest, [('contrasts', 'contrasts')]),
                        (selectfiles, modelspec, [('func', 'functional_runs')]),
                        (modelspec, level1design, [('session_info',
                                                    'session_info')]),
                        (level1design, level1estimate, [('spm_mat_file',
                                                        'spm_mat_file')]),
                        (level1estimate, level1conest, [('spm_mat_file',
                                                        'spm_mat_file'),
                                                        ('beta_images',
                                                        'beta_images'),
                                                        ('residual_image',
                                                        'residual_image')]),
                        (level1conest, datasink, [('spm_mat_file', '1stLevel.@spm_mat'),
                                                ('spmT_images', '1stLevel.@T'),
                                                ('con_images', '1stLevel.@con'),
                                                ('spmF_images', '1stLevel.@F'),
                                                ('ess_images', '1stLevel.@ess'),
                                                ]),
                        ])
    return l1analysis

def second_level(contrast_list, experiment_dir, first_level_dir, output_dir, mask_path='/data/group_mask.nii.gz', working_dir='workingdir'):
    """define second level model"""
    # Gunzip - unzip the mask image
    gunzip = Node(Gunzip(in_file=mask_path), name="gunzip")

    # OneSampleTTestDesign - creates one sample T-Test Design
    onesamplettestdes = Node(OneSampleTTestDesign(),
                            name="onesampttestdes")

    # EstimateModel - estimates the model
    level2estimate = Node(EstimateModel(estimation_method={'Classical': 1}),name="level2estimate")

    # EstimateContrast - estimates group contrast
    level2conestimate = Node(EstimateContrast(group_contrast=True),
                            name="level2conestimate")
    cont1 = ['Group', 'T', ['mean'], [1]]
    level2conestimate.inputs.contrasts = [cont1]

    # Threshold - thresholds contrasts
    level2thresh = Node(Threshold(contrast_index=1,
                                use_topo_fdr=True,
                                # use_fwe_correction=True,
                                use_fwe_correction=False,
                                extent_threshold=0,
                                height_threshold=0.001,
                                # height_threshold=0.05,
                                height_threshold_type='p-value',
                                extent_fdr_p_threshold=0.05),
                        name="level2thresh")

    # Infosource - a function free node to iterate over the list of subject names
    infosource = Node(IdentityInterface(fields=['contrast_id']),
                    name="infosource")
    infosource.iterables = [('contrast_id', contrast_list)]

    # SelectFiles - to grab the data (alternativ to DataGrabber)
    firstlev_dir = opj(experiment_dir, first_level_dir, '1stLevel')
    templates = {'cons': opj(firstlev_dir, 'sub-*',
                            '{contrast_id}.nii')}
    selectfiles = Node(SelectFiles(templates,
                                base_directory=experiment_dir,
                                sort_filelist=True),
                    name="selectfiles")

    # Datasink - creates output folder for important outputs
    datasink = Node(DataSink(base_directory=experiment_dir,
                            container=output_dir),
                    name="datasink")

    # Use the following DataSink output substitutions
    substitutions = [('_contrast_id_', '')]
    datasink.inputs.substitutions = substitutions

    # Initiation of the 2nd-level analysis workflow
    l2analysis = Workflow(name='l2analysis')
    l2analysis.base_dir = opj(experiment_dir, working_dir)

    # Connect up the 2nd-level analysis components
    l2analysis.connect([(infosource, selectfiles, [('contrast_id', 'contrast_id')]),
                        (selectfiles, onesamplettestdes, [('cons', 'in_files')]),
                        (gunzip, onesamplettestdes, [('out_file',
                                                    'explicit_mask_file')]),
                        (onesamplettestdes, level2estimate, [('spm_mat_file', 'spm_mat_file')]),
                        (level2estimate, level2conestimate, [('spm_mat_file', 'spm_mat_file'),
                        ('beta_images', 'beta_images'),
                        ('residual_image', 'residual_image')]),
                        (level2conestimate, level2thresh, [('spm_mat_file',
                                                            'spm_mat_file'),
                                                        ('spmT_images',
                                                            'stat_image'),
                                                        ]),
                        (level2conestimate, datasink, [('spm_mat_file',
                                                        '2ndLevel.@spm_mat'),
                                                    ('spmT_images',
                                                        '2ndLevel.@T'),
                                                    ('con_images',
                                                        '2ndLevel.@con')]),
                        (level2thresh, datasink, [('thresholded_map',
                                                '2ndLevel.@threshold')]),
                        ])
    return l2analysis

def second_level_2sampleTTest(contrast_list, experiment_dir, first_level_dir_group1, first_level_dir_group2, output_dir, mask_path='/data/group_mask.nii.gz', working_dir='workingdir'):
    """define second level model comparing 2 groups in 2sample TTest"""
    # Gunzip - unzip the mask image
    gunzip = Node(Gunzip(in_file=mask_path), name="gunzip")

    # TwoSampleTTestDesign - creates two sample T-Test Design
    twosamplettestdes = Node(TwoSampleTTestDesign(),
                            name="twosampttestdes")

    # EstimateModel - estimates the model
    level2estimate = Node(EstimateModel(estimation_method={'Classical': 1}),name="level2estimate")

    # EstimateContrast - estimates group contrast
    level2conestimate = Node(EstimateContrast(group_contrast=True),
                            name="level2conestimate")
    # cont1 = ['Group', 'T', ['mean'], [1]]
    cont01 = ['FG_minus_TG', 'T', ['Group_{1}', 'Group_{2}'], [1,-1]]
    # cont02 = ['TG_minus_FG', 'T', ['Group_{1}', 'Group_{2}'], [-1,1]]
    level2conestimate.inputs.contrasts = [cont01]

    # Threshold - thresholds contrasts
    level2thresh = Node(Threshold(contrast_index=1,
                                use_topo_fdr=True,
                                # use_fwe_correction=True,
                                use_fwe_correction=False,
                                extent_threshold=0,
                                height_threshold=0.001,
                                # height_threshold=0.05,
                                height_threshold_type='p-value',
                                extent_fdr_p_threshold=0.05),
                        name="level2thresh")

    # Infosource - a function free node to iterate over the list of subject names
    infosource = Node(IdentityInterface(fields=['contrast_id']),
                    name="infosource")
    infosource.iterables = [('contrast_id', contrast_list)]

    # SelectFiles - to grab the data (alternativ to DataGrabber)
    firstlev_dir_group1 = opj(experiment_dir, first_level_dir_group1, '1stLevel')
    templates_group1 = {'cons': opj(firstlev_dir_group1, 'sub-*',
                            '{contrast_id}.nii')}
    selectfiles_group1 = Node(SelectFiles(templates_group1,
                                base_directory=experiment_dir,
                                sort_filelist=True),
                    name="selectfiles_group1")
    firstlev_dir_group2 = opj(experiment_dir, first_level_dir_group2, '1stLevel')
    templates_group2 = {'cons': opj(firstlev_dir_group2, 'sub-*',
                            '{contrast_id}.nii')}
    selectfiles_group2 = Node(SelectFiles(templates_group2,
                                base_directory=experiment_dir,
                                sort_filelist=True),
                    name="selectfiles_group2")

    # Datasink - creates output folder for important outputs
    datasink = Node(DataSink(base_directory=experiment_dir,
                            container=output_dir),
                    name="datasink")

    # Use the following DataSink output substitutions
    substitutions = [('_contrast_id_', '')]
    datasink.inputs.substitutions = substitutions

    # Initiation of the 2nd-level analysis workflow
    l2analysis = Workflow(name='l2analysis')
    l2analysis.base_dir = opj(experiment_dir, working_dir)

    # Connect up the 2nd-level analysis components
    l2analysis.connect([(infosource, selectfiles_group1, [('contrast_id', 'contrast_id')]),
                        (selectfiles_group1, twosamplettestdes, [('cons', 'group1_files')]),
                        (infosource, selectfiles_group2, [('contrast_id', 'contrast_id')]),
                        (selectfiles_group2, twosamplettestdes, [('cons', 'group2_files')]),
                        (gunzip, twosamplettestdes, [('out_file',
                                                    'explicit_mask_file')]),
                        (twosamplettestdes, level2estimate, [('spm_mat_file', 'spm_mat_file')]),
                        (level2estimate, level2conestimate, [('spm_mat_file', 'spm_mat_file'),
                        ('beta_images', 'beta_images'),
                        ('residual_image', 'residual_image')]),
                        (level2conestimate, level2thresh, [('spm_mat_file',
                                                            'spm_mat_file'),
                                                        ('spmT_images',
                                                            'stat_image'),
                                                        ]),
                        (level2conestimate, datasink, [('spm_mat_file',
                                                        '2ndLevel.@spm_mat'),
                                                    ('spmT_images',
                                                        '2ndLevel.@T'),
                                                    ('con_images',
                                                        '2ndLevel.@con')]),
                        (level2thresh, datasink, [('thresholded_map',
                                                '2ndLevel.@threshold')]),
                        ])
    return l2analysis

def second_level_covariate(contrast_list, experiment_dir, first_level_dir, output_dir, cov_ls, mask_path='/data/group_mask.nii.gz', working_dir='workingdir'):
    """define second level model within between-subject covariate"""
    # Gunzip - unzip the mask image
    gunzip = Node(Gunzip(in_file=mask_path), name="gunzip")

    # covariates (a list of items which are a dictionary with keys which are 'vector' or 'name' or 'interaction' or 'centering' and with values which are any value)
    covariates_ls = [dict(vector=cov_ls, name='model_evidence')]

    # OneSampleTTestDesign - creates one sample T-Test Design
    onesamplettestdes = Node(OneSampleTTestDesign(covariates=covariates_ls),
                            name="onesampttestdes")

    # EstimateModel - estimates the model
    level2estimate = Node(EstimateModel(estimation_method={'Classical': 1}),name="level2estimate")

    # EstimateContrast - estimates group contrast
    level2conestimate = Node(EstimateContrast(group_contrast=True),
                            name="level2conestimate")
    cont1 = ['Group', 'T', ['mean'], [1]]
    level2conestimate.inputs.contrasts = [cont1]

    # Threshold - thresholds contrasts
    level2thresh = Node(Threshold(contrast_index=1,
                                use_topo_fdr=True,
                                # use_fwe_correction=True,
                                use_fwe_correction=False,
                                extent_threshold=0,
                                height_threshold=0.001,
                                # height_threshold=0.05,
                                height_threshold_type='p-value',
                                extent_fdr_p_threshold=0.05),
                        name="level2thresh")

    # Infosource - a function free node to iterate over the list of subject names
    infosource = Node(IdentityInterface(fields=['contrast_id']),
                    name="infosource")
    infosource.iterables = [('contrast_id', contrast_list)]

    # SelectFiles - to grab the data (alternativ to DataGrabber)
    firstlev_dir = opj(experiment_dir, first_level_dir, '1stLevel')
    templates = {'cons': opj(firstlev_dir, 'sub-*',
                            '{contrast_id}.nii')}
    selectfiles = Node(SelectFiles(templates,
                                base_directory=experiment_dir,
                                sort_filelist=True),
                    name="selectfiles")

    # Datasink - creates output folder for important outputs
    datasink = Node(DataSink(base_directory=experiment_dir,
                            container=output_dir),
                    name="datasink")

    # Use the following DataSink output substitutions
    substitutions = [('_contrast_id_', '')]
    datasink.inputs.substitutions = substitutions

    # Initiation of the 2nd-level analysis workflow
    l2analysis = Workflow(name='l2analysis')
    l2analysis.base_dir = opj(experiment_dir, working_dir)

    # Connect up the 2nd-level analysis components
    l2analysis.connect([(infosource, selectfiles, [('contrast_id', 'contrast_id')]),
                        (selectfiles, onesamplettestdes, [('cons', 'in_files')]),
                        (gunzip, onesamplettestdes, [('out_file',
                                                    'explicit_mask_file')]),
                        (onesamplettestdes, level2estimate, [('spm_mat_file', 'spm_mat_file')]),
                        (level2estimate, level2conestimate, [('spm_mat_file', 'spm_mat_file'),
                        ('beta_images', 'beta_images'),
                        ('residual_image', 'residual_image')]),
                        (level2conestimate, level2thresh, [('spm_mat_file',
                                                            'spm_mat_file'),
                                                        ('spmT_images',
                                                            'stat_image'),
                                                        ]),
                        (level2conestimate, datasink, [('spm_mat_file',
                                                        '2ndLevel.@spm_mat'),
                                                    ('spmT_images',
                                                        '2ndLevel.@T'),
                                                    ('con_images',
                                                        '2ndLevel.@con')]),
                        (level2thresh, datasink, [('thresholded_map',
                                                '2ndLevel.@threshold')]),
                        ])
    return l2analysis

def subjectinfo(subject_id):
    """define individual subject info"""
    import pandas as pd
    from nipype.interfaces.base import Bunch
    
    def construct_sj(trialinfo, subject_id, run_num, cond_name):
        """construct df"""
        df_sj = trialinfo[(trialinfo['subject']==int(subject_id)) & (trialinfo['session']==int(run_num))]
        sj_info = pd.DataFrame()
        sj_info['onset'] = df_sj['runtime']
        sj_info['duration'] = 0.
        sj_info['weight'] = 1.
        trial_type = df_sj['seq'].replace({1:'Low', 2:'High'})
        sj_info['trial_type'] = trial_type
        sj_info_cond = sj_info[sj_info['trial_type']==cond_name]
        return sj_info_cond

    def select_confounds(subject_id, run_num):
        """import confounds tsv files"""
        confounds_dir = f'/data/sub-%02d/func/' % int(subject_id)
        confounds_file = confounds_dir+f'sub-%02d_task-tsl_run-%d_desc-confounds_timeseries.tsv' % (int(subject_id), int(run_num))
        conf_df = pd.read_csv(confounds_file, sep='\t')
        return conf_df

    def confounds_regressor(conf_df, conf_names):
        """select confounds for regressors"""
        conf_select = conf_df[conf_names].loc[4:].fillna(0) # ignore first 4 dummy scans
        conf_select_list = [conf_select[col].values.tolist() for col in conf_select] 
        return conf_select_list

    def find_runs(subject_id):
        """find available runs from func"""
        from glob import glob
        func_dir = f'/output/smooth_nomask/preproc/sub-%02d/' % int(subject_id)    
        func_files = glob(func_dir+'*bold.nii')
        runs = []
        for f in func_files:
            tmp = f.split('/')
            run = tmp[5].split('_')[2].split('-')[1]
            runs.append(int(run))
        return sorted(runs)
    
    conf_names = ['csf','white_matter','global_signal',
    'dvars','std_dvars','framewise_displacement', 'rmsd',
    'a_comp_cor_00', 'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03', 'a_comp_cor_04', 'a_comp_cor_05', 'cosine00', 'cosine01', 'cosine02', 'cosine03', 'cosine04', 'cosine05',
    'trans_x', 'trans_y', 'trans_z', 'rot_x','rot_y','rot_z']

    alltrialinfo = pd.read_csv('/code/data/fmri_behavioural_new.csv')
    alltrialinfo.head()
    
    subject_info = []
    onset_list = []
    condition_names = ['High', 'Low']
    runs = find_runs(subject_id)
    print(runs)
    for run in runs:
        for cond in condition_names:
            run_cond = construct_sj(alltrialinfo, subject_id, run, cond)
            onset_run_cond = run_cond['onset'].values
            onset_list.append(sorted(onset_run_cond))

    subject_info = []
    for r in range(len(runs)):
        onsets = [onset_list[r*2], onset_list[r*2+1]]
        regressors_all = select_confounds(subject_id, runs[r])
        regressors = confounds_regressor(regressors_all, conf_names)

        subject_info.insert(r,
                           Bunch(conditions=condition_names,
                                 onsets=onsets,
                                 durations=[[0], [0]],
                                 regressors=regressors,
                                 regressor_names=conf_names,
                                 amplitudes=None,
                                 tmod=None,
                                 pmod=None))

    return subject_info  # this output will later be returned to infosource

def select_confounds(subject_id, run_num):
    """import confounds tsv files"""
    confounds_dir = f'/data/sub-%02d/func/' % int(subject_id)
    confounds_file = confounds_dir+f'sub-%02d_task-tsl_run-%d_desc-confounds_timeseries.tsv' % (int(subject_id), int(run_num))
    conf_df = pd.read_csv(confounds_file, sep='\t')
    return conf_df

def confounds_regressor(conf_df, conf_names):
    """select confounds for regressors"""
    conf_select = conf_df[conf_names].loc[4:].fillna(0) # ignore first 4 dummy scans
    conf_select_list = [conf_select[col].values.tolist() for col in conf_select] 
    return conf_select_list

def list_subject(data_dir='/data'):
    """list all available subjects"""
    sj_ls = []
    for f in os.listdir(data_dir):
        if f.startswith('sub') and (not f.endswith('.html')):
            sj_ls.append(f.split('-')[1])
    return sj_ls

def find_runs(subject_id):
    """find available runs from func"""
    from glob import glob
    func_dir = f'/output/smooth_nomask/preproc/sub-%02d/' % int(subject_id)    
    func_files = glob(func_dir+'*bold.nii')
    runs = []
    for f in func_files:
        tmp = f.split('/')
        run = tmp[5].split('_')[2].split('-')[1]
        runs.append(int(run))
    return sorted(runs)


if __name__ == "__main__":
    code_dir = '/code'
    experiment_dir = '/output'
    output_1st_dir = '1stLevel_nomask'
    # output_2nd_dir = '2ndLevel_masked'
    output_2nd_dir = '2ndLevel_masked_FDR0001'
    working_dir = 'workingdir'
    
    # define experiment info
    TR = 2.
    subject_list = list_subject(data_dir=opj(experiment_dir, 'smooth_nomask', 'preproc'))

    # define contrasts
    # condition names
    condition_names = ['High','Low']
    # contrasts
    cont01 = ['average', 'T', condition_names, [.5, .5]]
    cont02 = ['High',    'T', condition_names, [1, 0]]
    cont03 = ['Low',     'T', condition_names, [0, 1]]
    cont04 = ['High>Low','T', condition_names, [1,-1]]
    cont05 = ['Low>High','T', condition_names, [-1,1]]
    contrast_list = [cont01, cont02, cont03, cont04, cont05]

    # run first level
    l1analysis = first_level(TR, contrast_list, subject_list, 
                experiment_dir, output_1st_dir, subjectinfo)
    l1analysis.run('MultiProc')

    # run second level
    conname_lsit = ['con_0001', 'con_0002', 'con_0003', 'con_0004', 'con_0005']
    l2analysis = second_level(conname_lsit, experiment_dir, output_1st_dir, output_2nd_dir, mask_path='/output/group_mask.nii.gz')
    l2analysis.run('MultiProc')