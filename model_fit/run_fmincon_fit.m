function run_fmincon_fit(subj_id, model_str, data_set)
% fmin con fit for subject

    % add to path
    % addpath('../../../MATLAB/cbm/codes');
    addpath('../../../MATLAB/MinimalTransitionProbsModel/IdealObserversCode');
    
    % create a directory for individual output files:
    if strcmp(data_set, 'fmri')
        output_dir = ['./output_fmri/', model_str]
    else
        output_dir = ['./output_practice/', model_str]
    end
    mkdir(output_dir);
    
    % load data
    data_path = ['../data/', data_set, '_behavioural.mat']
    fdata = load(data_path);
    data  = fdata.subj{subj_id};
    subj_num = data.subject(1);
    chunk_size = 100; % number of starting points
    
    % fmincon settings
    options = optimset('Display', 'off', 'FunValCheck','on');
    % set bounds and random start points
    [lb, ub, start_point, A, b]= set_boundsp(model_str, chunk_size);
    % initialise
    parameters_tmp=nan(chunk_size, size(start_point,2));
    fval_tmp=nan(1,chunk_size);
    exit_flag_tmp=nan(1,chunk_size);
    output_tmp= cell(1,chunk_size);
    lambda_tmp= cell(1,chunk_size);
    gradient_tmp= nan(chunk_size, size(start_point,2));
    hessian_tmp= nan(chunk_size, size(start_point,2),size(start_point,2));
    
    % fit 
    for aa = 1:chunk_size
        disp(['Currently running chunk ', num2str(aa)])
        [parameters_tmp(aa, :),fval_tmp(aa),exit_flag_tmp(aa),output_tmp{aa}, lambda_tmp{aa}, gradient_tmp(aa, :), hessian_tmp(aa, :,:)] = ...
            fmincon(@(parameters)eval_model(parameters, data, model_str), start_point(aa,:),A, b,[],[],lb,ub,[],options);
    end
    sv_file= [output_dir,'/fit_subject_' num2str(subj_num, '%02d'),'.mat'];
    save(sv_file, 'parameters_tmp', 'fval_tmp');

end