function trigger(current)

daqreset;

%% START DAQ
s = daq.createSession('ni');
devices = daq.getDevices();
s.addAnalogOutputChannel(devices.ID,'ao0','Voltage');               % Set device and channel/s (NI box)
s.Rate = 100000;
s.IsContinuous = false;
stimWave             = zeros(20,1);                             % Create square wave
stimWave(6:15,1)     = ones(10,1);
% current              = 5;                                      % change this to change intensity for a DS5 device

%% SET SHOCK PARAMETERS
% load('maggie_shock_pars.mat');
% reps = 1;
%
% for rep = 1:reps

%% PREPARE & RUN TRAIN
Npulses = 2;
isi = 1;
iti = 3;

for i = 1:Npulses(1)
    s.queueOutputData(current/5 * stimWave); % Transfom mA in Volt for the NI box
    s.startForeground(); %send pulse
    WaitSecs(isi);
end
WaitSecs(iti);

% end

stop(s);

end
% to kill script: ctrl + c, then type stop(s)