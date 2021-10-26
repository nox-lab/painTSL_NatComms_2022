function [lap_paths] = summarise_fit(data_set)
    % extract fitted params from mat files
    if strcmp(data_set, 'fmri')
        output_dir = '../model_fit/output_fmri';
    elseif strcmp(data_set, 'practice')
        output_dir = '../model_fit/output_practice';
    end
    % list dir
    % wildcard_str = 'fit*.mat';
    % lap_list = dir([output_dir, filesep, wildcard_str]);
    list_tmp = dir(output_dir);
    lap_list = list_tmp(3:end);
    % lap names
    lap_names = {};
    lap_paths = {};
    for f=1:length(lap_list)
        lap_paths{f} = [lap_list(f).folder, filesep, lap_list(f).name];
        lap_names{f} = lap_list(f).name;
    end

    % load lap files
    sj_mat = [];
    nll_mat = [];
    params_mat = [];
    loglik_mat = [];
    transparam_mat = [];
    names_mat = [];
    for i = 1:length(lap_names)
        % lap_names{i}
        % lap_paths{i}
        tmp_fnames = dir(lap_paths{i});
        lap_fnames = tmp_fnames(3:end);
        n_sj = length(lap_fnames);
        for j = 1:length(lap_fnames)
            fname = [lap_paths{i}, filesep, lap_fnames(j).name];
            sj_name = lap_fnames(j).name(end-5:end-4);
            tmp = load(fname);
            % record 
            nll_mat = [nll_mat; mean(tmp.fval_tmp)];
            sj_mat = [sj_mat; str2num(sj_name)];
            names_mat = [names_mat; {lap_names{i}}];
            params_mat = [params_mat; mean(tmp.parameters_tmp(:,1))];
            transparam_mat = [transparam_mat; 1 / (1 + exp(-mean(tmp.parameters_tmp(:,1))))];
            loglik_mat = [loglik_mat; -mean(tmp.fval_tmp)];
        end
    end

    % save to csv
    T = table(names_mat(:), sj_mat(:), loglik_mat(:), nll_mat(:), params_mat(:), transparam_mat(:), 'VariableNames',{'model','subject','log_evidence', 'nll','parameters','transformed_parameters'});
    save_path = ['./params/',data_set,'.csv'];
    writetable(T,save_path);
end