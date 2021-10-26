function df = run_compare_local(csv_name, model_names)
% run function compare_bms
% csv_name - fmri.csv, fmri_rt.csv, practice.csv, practice_rt.csv

    % add vba to path
    % cd ../../../MATLAB/VBA-toolbox
    % VBA_setup();
    % cd ../../tsl/tsl_hbi/model_comparison
    
    output_dir = './params/';
    csv_file = [output_dir, csv_name];

    df = readtable(csv_file);
    % % BMS
    evidence_mat = [];
    if isempty(model_names)
        model_names = unique(df.model);
    end
    model_names
    for i = 1:length(model_names)
        df_tmp = df(ismember(df.model,model_names{i}),:)
        evidence_mat(i, :) = df_tmp.log_evidence;
    end
    [posterior,out] = VBA_groupBMC(evidence_mat);
    % model frequency
    f = out.Ef;
    % exceedance prob
    ep = out.ep;
    % protected ep
    pep = (1-out.bor)*out.ep + out.bor/length(out.ep);

    % save output
    T = table(model_names(:), f(:), ep(:), pep(:), 'VariableNames',{'model_name','model_frequency','exceedance_prob', 'protected_exceedance_prob'});
    writetable(T,['./local_output/', csv_name]);

    % save subject stats
    TT = array2table(posterior.r','VariableNames',model_names);
    writetable(TT,['./local_output/subject_',csv_name]);
end