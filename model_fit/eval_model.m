function nll = eval_model(parameters, data, model_str)
% evaluate model and return negative log likelihood

    if strcmp(model_str, 'io_jump_freq')
        loglik = model_io_jump_freq(parameters, data);
    elseif strcmp(model_str, 'io_fixed_freq')
        loglik = model_io_fixed_freq(parameters, data);
    elseif strcmp(model_str, 'io_fixed_trans')
        loglik = model_io_fixed_trans(parameters, data);
    elseif strcmp(model_str, 'io_jump_trans')
        loglik = model_io_jump_trans(parameters, data);
    elseif strcmp(model_str, 'random')
        loglik = model_random(parameters, data);
    elseif strcmp(model_str, 'rw')
        loglik = model_rw(parameters, data);
    end
    nll = -loglik;

end