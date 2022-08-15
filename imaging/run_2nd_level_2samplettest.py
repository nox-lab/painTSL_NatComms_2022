"""
running 2nd level analysis (2 sample t-test)
"""
import os,json,glob,sys
from os.path import join as opj
from pain_compare import second_level_2sampleTTest

if __name__ == "__main__":
    code_dir = '/code'
    experiment_dir = '/output'
    
    # # frequency model, frequency minus transition group
    # print(f'Running 2nd level on model: 2-sample ttest')
    # output_1st_dir_group1 = '1stLevel_io_jf_fg'
    # output_1st_dir_group2 = '1stLevel_io_jf_tg'
    # output_2nd_dir = '2ndLevel_jf_fgtg_FDR0001'

    # transition model, transition minus frequency group
    print(f'Running 2nd level on model: 2-sample ttest')
    output_1st_dir_group1 = '1stLevel_io_jt_tg'
    output_1st_dir_group2 = '1stLevel_io_jt_fg'
    output_2nd_dir = '2ndLevel_jt_tgfg_FDR0001'

    # gather connames
    conname_list = ['con_0001', 'con_0002', 'con_0003', 'con_0004']

    # run second level
    l2analysis = second_level_2sampleTTest(conname_list, experiment_dir, output_1st_dir_group1, output_1st_dir_group2, output_2nd_dir, mask_path='/output/group_mask.nii.gz')
    l2analysis.run('MultiProc')