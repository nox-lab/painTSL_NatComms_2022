function [p1_mean, p_surp, p1_sd, p_distUpdate, p_fulldist] = model_io_jump_freq(parameters, subject)
% IO model with jumps

    nd_pj = parameters(1); % normally distributed
    pj = 1 / (1 + exp(-nd_pj)); % jump prob (positive and integer)

    % unpack data
    seq = subject.seq; % 1 for l, 2 for h
    % sess = subject.session; % sessions
    % y = subject.p1; % subject ratings

    % observer definition
    in.learned = 'frequency';
    in.jump = 1;
    in.s = seq;
    in.opt.pJ = pj;
    in.verbose = 0;
    in.opt.pgrid = 0:0.05:1; % reduce from 100 to 20 speed up

    % IO probs
    out = IdealObserver(in);
    p1_mean = out.p1_mean(:); % prob given current stim
    p1_sd = out.p1_sd(:); % posterior sd
    p_surp = out.surprise(:); % prob given current stim and surprise
    % calculate predcition error as KL divergence of successive posterior mean
    p_distUpdate = out.distUpdate(:); 
    % distribution
    p_fulldist = out.p1_dist;
    % regress
    % BIC = regress_prob(y, p, sess, parameters); 
    % loglik = -BIC; % negative BIC=loglik

end
