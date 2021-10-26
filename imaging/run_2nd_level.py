"""
running 2nd level analysis
"""
import os,json,glob,sys
from os.path import join as opj
from pain_compare import second_level

if __name__ == "__main__":
    code_dir = '/code'
    experiment_dir = '/output'
    
    model_name = sys.argv[1]
    print(f'Running 2nd level on model: {model_name}')
    output_1st_dir = '1stLevel_' + model_name
    output_2nd_dir = '2ndLevel_' + model_name + '_FDR0001'

    # gather connames
    # conname_list = ['con_0001', 'con_0002']
    tmp = opj(experiment_dir, output_1st_dir, '1stLevel', 'sub-06')
    conname_list = []
    for f in os.listdir(tmp):
        if f.startswith('con_'):
            conname_list.append(f[:-4]) # exluding .nii
    print(conname_list)

    # run second level
    l2analysis = second_level(conname_list, experiment_dir, output_1st_dir, output_2nd_dir, mask_path='/output/group_mask.nii.gz')
    l2analysis.run('MultiProc')