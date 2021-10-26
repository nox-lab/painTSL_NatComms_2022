function [loglik] = model_rw(parameters, subject)
% rescorla-wagner model

    % parameters
    nd_alph = parameters(1); % learning rate
    alph = 1 / (1 + exp(-nd_alph)); 

    % unpack data
    seq = subject.seq; % 1 for l, 2 for h
    sess = subject.session; % sessions
    y = subject.p1; % subject ratings

    % number of trials
    T = size(seq, 1);
    
    % value calculation
    V = 0; % initialise
    V_rec = [];
    for t = 1:T
        V_rec(t) = V;
        if seq(t)==1
            r = 1; % low pain=reward
        else
            r = 0;
        end
        V = V + alph * (r - V);
    end
    p = V_rec;

    % regress
    BIC = regress_prob(y, p(:), sess, parameters); 
    loglik = -BIC; % negative BIC=loglik

end
