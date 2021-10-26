"""IO jump freq model pmod with both posterior and kl divergence as pe, with high/low pain confounds"""

import os,json,glob,sys
from os.path import join as opj
from nipype.interfaces.spm import Level1Design, EstimateModel, EstimateContrast, OneSampleTTestDesign, Threshold
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces.fsl import Info
from nipype.algorithms.misc import Gunzip
from nipype import Workflow, Node
import nilearn.plotting
import numpy as np
import pandas as pd
import nibabel
import matplotlib.pyplot as plt

from pain_compare import first_level, second_level, list_subject

def subjectinfo(subject_id):
    """define individual subject info"""
    import pandas as pd
    import numpy as np
    from nipype.interfaces.base import Bunch
    
    def construct_sj(trialinfo, subject_id, run_num, cond_name):
        """construct df"""
        df_sj = trialinfo[(trialinfo['subject']==int(subject_id)) & (trialinfo['session']==int(run_num))]
        sj_info = pd.DataFrame()
        sj_info['onset'] = df_sj['runtime']
        sj_info['duration'] = 0.
        sj_info['weight'] = 1.
        if cond_name=='High' or cond_name=='Low':
            trial_type = df_sj['seq'].replace({1:'Low', 2:'High'})
            sj_info['trial_type'] = trial_type
            sj_info_cond = sj_info[sj_info['trial_type']==cond_name]
            return sj_info_cond
        else:
            return sj_info

    def select_confounds(subject_id, run_num):
        """import confounds tsv files"""
        # works on cam hpc only
        # confounds_dir = f'/data/sub-%02d/func/' % int(subject_id)
        # confounds_file = confounds_dir+f'sub-%02d_task-tsl_run-%d_desc-confounds_timeseries.tsv' % (int(subject_id), int(run_num))
        # works on jal
        confounds_file = f'/confounds/sub-{int(subject_id):02d}_task-tsl_run-{int(run_num):d}_desc-confounds_timeseries.tsv'
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

    alltrialinfo = pd.read_csv('/code/model_gen/local_output_mean/fmri_io_jump_freq.csv')
    alltrialinfo.head()
    
    subject_info = []
    onset_list = []
    condition_names = ['Stim_pp', 'Stim_pe', 'High', 'Low']
    runs = find_runs(subject_id)
    print(runs)
    for run in runs:
        for cond in condition_names:
            run_cond = construct_sj(alltrialinfo, subject_id, run, cond)
            onset_run_cond = run_cond['onset'].values
            onset_list.append(sorted(onset_run_cond))

    subject_info = []
    conds_num = len(condition_names)
    for r in range(len(runs)):
        onsets = [onset_list[r*conds_num],onset_list[r*conds_num+1],
                  onset_list[r*conds_num+2],onset_list[r*conds_num+3]]
        regressors_all = select_confounds(subject_id, runs[r])
        regressors = confounds_regressor(regressors_all, conf_names)

        df_sj = alltrialinfo[(alltrialinfo['subject']==int(subject_id)) & (alltrialinfo['session']==int(runs[r]))]
        # demean pmod
        param_list_pp = list(df_sj['pmod_mean'].values - np.mean(df_sj['pmod_mean'].values))
        param_list_pe = list(df_sj['pmod_pe'].values - np.mean(df_sj['pmod_pe'].values))
        pmod_bunch = [Bunch(name=['pmod_mean'], poly=[1], param=[param_list_pp]), Bunch(name=['pmod_pe'], poly=[1], param=[param_list_pe]),None]
#         pmod_bunch = None
        subject_info.insert(r,
                           Bunch(conditions=condition_names,
                                 onsets=onsets,
                                 durations=[[0], [0], [0], [0]],
                                 regressors=regressors,
                                 regressor_names=conf_names,
                                 pmod=pmod_bunch,
                                 amplitudes=None,
                                 tmod=None
                                 ))

    return subject_info  # this output will later be returned to infosource


if __name__ == "__main__":
    code_dir = '/code'
    experiment_dir = '/output'
    
    # define experiment info
    TR = 2.
    subject_list = [f'{int(sys.argv[1]):02d}']
    
    # define model name
    model_name = sys.argv[2]
    output_1st_dir = '1stLevel_' + model_name
    print(f'current subject: {subject_list}, model: {model_name}')

    # define contrasts
    con_names = ['Stim_ppxpmod_mean^1','Stim_pexpmod_pe^1', 'High','Low']
    # pmod contrasts
    cont01 = ['pmod_mean', 'T', con_names, [1,0,0,0]]
    cont02 = ['pmod_mean_neg', 'T', con_names, [-1,0,0,0]]
    cont03 = ['pmod_pe', 'T', con_names, [0,1,0,0]]
    cont04 = ['pmod_pe_neg', 'T', con_names, [0,-1,0,0]]
    # cont05 = ['average', 'T', con_names, [0,0,.5,.5]]
    # cont06 = ['High',    'T', con_names, [0,0,1,0]]
    # cont07 = ['Low',     'T', con_names, [0,0,0,1]]
    cont05 = ['High>Low','T', con_names, [0,0,1,-1]]
    cont06 = ['Low>High','T', con_names, [0,0,-1,1]]
    # contrast_list = [cont01, cont02, cont03, cont04, cont05, cont06, cont07, cont08, cont09]
    contrast_list = [cont01, cont02, cont03, cont04, cont05, cont06]

    # run first level
    l1analysis = first_level(TR, contrast_list, subject_list, 
                experiment_dir, output_1st_dir, subjectinfo)
    l1analysis.run('MultiProc')