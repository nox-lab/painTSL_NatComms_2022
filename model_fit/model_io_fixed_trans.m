function [loglik] = model_io_fixed_trans(parameters, subject)
% IO model with no jump, learning transition

    % nd_p1 = parameters(1);
    % p1_prior = 1 / (1 + exp(-nd_p1)); 
    
    % fitting window and decay
    win = round(parameters(1));
    deca = round(parameters(2));
    
    % unpack data
    seq = subject.seq; % 1 for l, 2 for h
    sess = subject.session; % sessions
    y = subject.p1; % subject ratings

    % observer definition
    in.learned = 'transition';
    in.jump = 0;
    % if max(sess)<10 % fmri
    %     win = 17; % fixed window length for speed
    %     deca = 6; % decay window length
    % else % practice
    %     win = 21; % fixed window length for speed
    %     deca = 12; % decay window length
    % end
    in.opt.MemParam = {'Limited', win, 'Decay', deca};
    in.s = seq;
    % in.priorp1 = [p1_prior, 1-p1_prior];
    in.verbose = 0;
    in.opt.pgrid = 0:0.05:1; % reduce from 100 to 20 speed up

    % IO probs
    out = IdealObserver(in);
    p = out.p1_mean(:); % prediction given current stim

    % regress
    BIC = regress_prob(y, p, sess, parameters); 
    loglik = -BIC; % negative BIC=loglik

end
