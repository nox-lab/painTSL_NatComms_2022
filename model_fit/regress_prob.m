function [BIC] = regress_prob(obs_rating, model_prob, session, parameters)
%regress_prob - perform regression on model prob

    y = obs_rating(:); % observed ratings from subject
    p = model_prob; % model output prob
    sess = session(:); % indicate sessions within subject
    
    exnan_idx = ~isnan(y); % indices of not nans
    if size(p,2)==2
        X = [ones(size(p(exnan_idx,1))) p(exnan_idx,:) sess(exnan_idx)]; % design matrix
        b = X\y(exnan_idx);
        y_hat = b(1) + b(2)*p(exnan_idx,1)+ b(3)*p(exnan_idx,2) + b(4)*sess(exnan_idx); % predicted ratings
        n_params = length(parameters) + 4; % 4 bs in regression
    elseif size(p,2)==1
        X = [ones(size(p(exnan_idx))) p(exnan_idx) sess(exnan_idx) randn(size(p(exnan_idx))) ]; % design matrix
        % X = [ones(size(p(exnan_idx))) p(exnan_idx)]; % design matrix
        % b = X\y(exnan_idx);
        [b,~,residuals] = regress(y(exnan_idx),X);
        % y_hat = b(1) + b(2)*p(exnan_idx) + b(3)*sess(exnan_idx); % predicted ratings
        % y_hat = b(1)*ones(size(p(exnan_idx))) + b(2)*p(exnan_idx); % predicted ratings
        % y_hat = b(1)*p(exnan_idx); % predicted ratings
        % n_params = length(parameters) + 3; % 3 bs 
        n_params = length(parameters) + 4; % 4 bs 
    end
    % residuals = y(exnan_idx) - y_hat; % residuals
    meanse = mean(residuals(~isnan(residuals)).^ 2); % mean square error of residuals
    n = length(y(exnan_idx));
    BIC = n*log(meanse) + n_params*log(n);
    % Mayhue 2019 log model likelihood approx
    % loglik = exp((-BIC)./2);
end