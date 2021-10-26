function [] = model_gen_local_mean(csv_name, model_names)
    % generate model output given model and dataset
    % csv_name - fmri.csv, practice.csv
    % add io to path
    addpath('../../../MATLAB/MinimalTransitionProbsModel/IdealObserversCode');

    % output_dir = '../model_gen/params/';
    output_dir = '../model_comparison/params/';
    csv_file = [output_dir, csv_name];

    df = readtable(csv_file);
    % load data
    data_set = split(csv_name,'.');
    data_path = ['../data/',data_set{1},'_behavioural.mat'];
    fdata = load(data_path);
    data  = fdata.subj;
    sj_n = length(data);


    % load params (not transformed)
    if isempty(model_names)
        model_names = unique(df.model)
    end
    for m = 1:length(model_names)
        model_str = model_names{m};
        df_tmp = df(ismember(df.model,model_names{m}),:);
        parameters = df_tmp.parameters;
        % calculate mean parameter
        parameters_mean = mean(parameters)
        % apply model
        seq = [];
        p_out = [];
        psurp_out = [];
        sj_out = [];
        sess_out = [];
        p1_out = [];
        runtime_out = [];
        start_idx = 1;
        for i = 1:sj_n
            subj_data = data{i};
            end_idx = start_idx+length(subj_data.seq)-1;
            sj_out(start_idx:end_idx) = subj_data.subject;
            sess_out(start_idx:end_idx) = subj_data.session;
            runtime_out(start_idx:end_idx) = subj_data.runtime;
            p1_out(start_idx:end_idx) = subj_data.p1;
            % apply model
            % if strcmp(model_str, 'subjects_io_jump_freq')
            if strcmp(model_str, 'io_jump_freq')
                [p1_mean, p_surp, p1_sd, p_distUpdate, p1_dist] = model_io_jump_freq(parameters_mean, subj_data);
            elseif strcmp(model_str, 'io_jump_trans')
                [p1_mean, p_surp, p1_sd, p_distUpdate] = model_io_jump_trans(parameters_mean, subj_data);
            elseif strcmp(model_str, 'rw')
                [p1_mean, p_surp, p_distUpdate] = model_rw(parameters_mean, subj_data);
                p1_sd = zeros(size(p1_mean));
            end
            % append output
            % [start_idx, end_idx, length(p)]
            seq(start_idx:end_idx) = subj_data.seq;
            p_out(start_idx:end_idx) = p1_mean;
            psurp_out(start_idx:end_idx) = p_surp;
            psd_out(start_idx:end_idx) = p1_sd;
            ppe_out(start_idx:end_idx) = p_distUpdate;
            start_idx = start_idx + length(subj_data.seq);
        end
        T = table(sj_out(:), sess_out(:), runtime_out(:), seq(:), p1_out(:), 1-p1_out(:), p_out(:), 1-p_out(:), psurp_out(:), psd_out(:), ppe_out(:), 'VariableNames',{'subject','session','runtime', 'seq', 'p1', 'p2','pmod_mean', 'pmod_mean_p2', 'pmod_surprise', 'pmod_sd', 'pmod_pe'});
        save_path = ['./local_output_mean/',data_set{1},'_',model_str,'.csv'];
        writetable(T,save_path);
        % save dist for plot
        save_dist_path = ['./local_output_mean/',data_set{1},'_',model_str,'_p1dist.csv'];
        writematrix(p1_dist, save_dist_path);
    end        
end