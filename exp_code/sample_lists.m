function [trials_resp,tot_trial_time,timings,tot_run_time]=sample_lists(trial,isi,resptime)

sample_resp = [12:18];

blocks=trial/mean(sample_resp);
for b = 1:blocks+2
   sample_resp=sample_resp(randperm(length(sample_resp))); 
    samp_resp_list(b)=sample_resp(1);
end
trials_resp=cumsum(samp_resp_list);
del_idx=find(trials_resp>trial);
trials_resp(del_idx)=[];


resp_dur = resptime; %sec
resp_dur_list = zeros(trial,1);
resp_dur_list(trials_resp)= resp_dur;

for t = 1:trial
    
    isi=Shuffle(isi);
    tot_trial_time(t) = (isi(1) + resp_dur_list(t) );
    
    timings(t,:)= [ tot_trial_time(t), isi(1), resp_dur_list(t) ]; 
    tot_run_time(t) = sum( tot_trial_time(1:t) ) ;
    
end