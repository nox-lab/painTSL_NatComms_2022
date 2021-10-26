function [loglik] = model_random(parameters, subject)
% random base model assuming H/L with fixed prob

    nd_ph = parameters(1); % normally distributed p(h)
    p_h = 1 / (1 + exp(-nd_ph)); % p(h) (transformed to be between zero and one)
    p_l = 1 - p_h; % p(l) reciprocal to p(h)

    % unpack data
    seq = subject.seq; % 1 for l, 2 for h
    sess = subject.session; % sessions
    y = subject.p1; % subject ratings

    % number of trials
    T = size(seq, 1);

    % initialise prob
    p = nan(T, 1);

    % random prob for h/l
    for t = 1:T
        if seq(t) == 1
            p(t) = p_l;
        elseif seq(t) == 2
            p(t) = p_h;
        end
    end

    % regress
    BIC = regress_prob(y, p(:), sess, parameters); 
    loglik = -BIC; % negative BIC=loglik

end
