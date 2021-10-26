function [loglik] = model_io_fixed_freq(parameters, subject)
% IO model with fixed window

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
    in.learned = 'frequency';
    in.jump = 0;
    % if max(sess)<10 % fmri
    %     win = 15; % fixed window length for speed
    %     deca = 5; % decay window length
    % else % practice
    %     win = 20; % fixed window length for speed
    %     deca = 4; % decay window length
    % end
    in.opt.MemParam = {'Limited', win, 'Decay', deca};
    in.s = seq;
    % in.opt.priorp1 = [p1_prior, 1-p1_prior];
    in.verbose = 0;
    in.opt.pgrid = 0:0.05:1; % reduce from 100 to 20 speed up

    % IO probs
    out = IdealObserver(in);
    p = out.p1_mean(:); % prediction given current stim
    % regress
    BIC = regress_prob(y, p, sess, parameters); 
    loglik = -BIC; % negative BIC=loglik

end
