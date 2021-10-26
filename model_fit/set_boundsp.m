function [lb, ub, sp, A, b] = set_boundsp(model_str, nfits)
% setting upper lower bounds and random starting points
    
    model_single = strcmp(model_str, {'io_jump_freq', 'rw', 'random', 'io_jump_trans', });
    model_multi = strcmp(model_str, {'io_fixed_freq',  'io_fixed_trans'});
    if sum(model_single)>0
        lb = [-10];
        ub = [10];
        sp = [randn(nfits, 1)];
        A = []; % inequality matrix
        b = []; % inequality bounds
    elseif sum(model_multi)>0
        % lb = [-10, 2, 2];
        % ub = [10, 30, 30];
        lb = [2, 2];
        ub = [30, 30];
        sp = [randn(nfits, length(lb))];
        % A = [0, -1, 1]; % inequality matrix
        A = [-1, 1]; % inequality matrix
        b = 0; % inequality bounds
    end

end