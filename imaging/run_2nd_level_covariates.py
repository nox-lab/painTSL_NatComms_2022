"""
running 2nd level analysis with covariates
"""
import os,json,glob,sys
import pandas as pd
from os.path import join as opj
from pain_compare import second_level_covariate

if __name__ == "__main__":
    code_dir = '/code'
    experiment_dir = '/output'
    
    model_name = sys.argv[1]
    print(f'Running 2nd level on model: {model_name}')
    output_1st_dir = '1stLevel_' + model_name
    output_2nd_dir = '2ndLevel_' + model_name + '_covariate_FDR0001'

    # gather connames
    conname_list = ['con_0001', 'con_0002', 'con_0003', 'con_0004']

    # model evidence as covariate
    df = pd.read_csv('/code/model_comparison/local_output/subject_fmri.csv')
    cov_ls = df['io_jump_freq'].to_list()

    # run second level
    l2analysis = second_level_covariate(conname_list, experiment_dir, output_1st_dir, output_2nd_dir, cov_ls, mask_path='/output/group_mask.nii.gz')
    l2analysis.run('MultiProc')