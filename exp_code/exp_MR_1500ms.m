function exp_MR_1500ms(sub,sess,stimCurrent,MR_state)
% This function needs launches the main experiments. It requires
% Psychotoolbox 3, a NI DAQ toolbox, a Digitimer DS5, and a number of
% subfiles in the same directory: GenRandSeq.m, sample_lists.m,
% seq_source.m, trigger.m
% stimCurrent is a 2D vector specifying the desired intensity of the
% stimuli (e.g. [2.5 6])
% MR_state indicates whether we are in a MR environment, 0 = no MRI, 1 = MRI

% Copyright Flavia Mancini 2018

clear MEX

nttls=4;
GetSecs;
%% Parameters
trial=260; % number of trials per session
isi = [1.4:0.05:1.6]; %interstimulus interval
resptime = 7; % max time allowed for a response, in sec
[trials_resp,tot_trial_time,timings,tot_run_time]=sample_lists(trial,isi,resptime);

%% GENERATE SEQUENCE

[L,pLL,pLH]=seq_source(trial);
L_sel = [1:500];
L_sel = L_sel(randperm(500));
L_sel_size = length(L{L_sel(1)});
p(:,1) = pLL(1:L_sel_size);
p(:,2) = pLH(1:L_sel_size);
[ s, gen_p1, gen_p1g2, gen_p2g1 ] = GenRandSeq( L{L_sel(1)}, p );

[trials_resp,tot_trial_time,timings,tot_run_time]=sample_lists(trial,isi,resptime);

%% INITIALISE DAQ

daqreset;
ds = daq.createSession('ni');
devices = daq.getDevices();
ds.addAnalogOutputChannel(devices.ID,'ao0','Voltage');               % Set device and channel/s (NI box)
ds.Rate = 100000;
ds.IsContinuous = false;
stimWave             = zeros(20,1);                             % Create square wave
stimWave(6:15,1)     = ones(10,1);


%% Setup visuals and keyboard
Screen('Preference', 'SkipSyncTests', 1); %no checks
% Here we call some default settings for setting up Psychtoolbox
PsychDefaultSetup(2);
AssertOpenGL;

% Choosing the display with the highest dislay number
screens=Screen('Screens');
screenNumber=max(screens);

[w, rect] = Screen('OpenWindow', screenNumber, 0);

% Enable alpha blending with proper blend-function. We need it
% for drawing of smoothed points:
Screen('BlendFunction', w, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
[center(1), center(2)] = RectCenter(rect);
fps=Screen('FrameRate',w);      % frames per second
ifi=Screen('GetFlipInterval', w);
if fps==0
    fps=1/ifi;
end

% Get the size of the on screen window
[screenXpixels, screenYpixels] = Screen('WindowSize', w);

% Get the centre coordinate of the window
[xCenter, yCenter] = RectCenter(rect);

% Define black and white
white = WhiteIndex(w);
black = BlackIndex(w);
red = [255 0 0];
blue = [0 0 255];
HideCursor; % Hide the mouse cursor
Priority(MaxPriority(w));

% set keyboard
KbName('UnifyKeyNames');
escapeKey = KbName('q');
oneKey = KbName('1!');
twoKey = KbName('2@');
threeKey = KbName('3#');
fourKey = KbName('4$');
sevenKey = KbName('7&');
% leftKey = KbName('LeftArrow');
% rightKey = KbName('RightArrow');

% suppress echo to the command line for keypresses
ListenChar(2);

%% MAKE VAS
% Make a base Rect of x by y pixels
vasL = 300;
baseRect = [0 0 15 vasL];
% Make our vas rectangle coordinates
vasRect = CenterRectOnPointd(baseRect, xCenter, yCenter);

% make slider
sbaseRect = [0 0 50 6];
% Set the intial position of the square to be in the centre of the screen
sliderX = xCenter;
sliderY = yCenter;
sliderRect = CenterRectOnPointd(sbaseRect, sliderX, sliderY);
% Set the amount we want our square to move on each button press
pixelsPerPress = 5;

% tick
tick = [0 0 30 6];
tickRect_m=CenterRectOnPointd(tick, xCenter, yCenter);
tickRect_t=CenterRectOnPointd(tick, xCenter, yCenter-(vasL/2));
tickRect_b=CenterRectOnPointd(tick, xCenter, yCenter+(vasL/2));

%% GET VAS MIN MAX

% Do initial flip...
Screen('Flip', w);

sliderY = yCenter;
DrawFormattedText(w, 'Please select the LOWEST point in the scale and enter', xCenter-230, screenYpixels * 0.20, white);
Screen('FillRect', w, [125 125 125], tickRect_m);
Screen('FillRect', w, [125 125 125], tickRect_t);
Screen('FillRect', w, [125 125 125], tickRect_b);
Screen('FillRect', w, [125 125 125], vasRect);
Screen('FillRect', w, red, sliderRect);
Screen('Flip', w);
% This is the cue which determines whether we exit the vas
exitvas = false;

% Loop the animation until the escape key is pressed
while exitvas == false
    
    % Check the keyboard to see if a button has been pressed
    [keyIsDown,secs, keyCode] = KbCheck;
    
    % Depending on the button press, move slider up and down
    if keyCode(oneKey)
        exitvas = true;
    elseif keyCode(twoKey)
        sliderY = sliderY + pixelsPerPress;
    elseif keyCode(threeKey)
        sliderY = sliderY - pixelsPerPress;
    end
    
    % We set bounds to make sure our slider doesn't go completely off of
    % the VAS boundaries
    if sliderY < yCenter-(vasL/2)
        sliderY = yCenter-(vasL/2);
    elseif sliderY > yCenter+(vasL/2)
        sliderY = yCenter+(vasL/2);
    end
    sliderRect = CenterRectOnPointd(sbaseRect, sliderX, sliderY);
    
    % Draw to the screen
    DrawFormattedText(w, 'Please select the LOWEST point in the scale and enter', xCenter-230, screenYpixels * 0.20, white);
    Screen('FillRect', w, [125 125 125], tickRect_m);
    Screen('FillRect', w, [125 125 125], tickRect_t);
    Screen('FillRect', w, [125 125 125], tickRect_b);
    Screen('FillRect', w, [125 125 125], vasRect);
    Screen('FillRect', w, red, sliderRect);
    
    % Flip to the screen
    Screen('Flip', w);
end

vas.min = sliderY;
Screen('Flip', w);
WaitSecs(0.5);

sliderY = yCenter;
DrawFormattedText(w, 'Now select the HIGHEST point in the scale and enter', xCenter-230, screenYpixels * 0.20, white);
Screen('FillRect', w, [125 125 125], tickRect_m);
Screen('FillRect', w, [125 125 125], tickRect_t);
Screen('FillRect', w, [125 125 125], tickRect_b);
Screen('FillRect', w, [125 125 125], vasRect);
Screen('FillRect', w, red, sliderRect);
Screen('Flip', w);
% This is the cue which determines whether we exit the vas
exitvas = false;

% Loop the animation until the escape key is pressed
while exitvas == false
    
    % Check the keyboard to see if a button has been pressed
    [keyIsDown,secs, keyCode] = KbCheck;
    
    % Depending on the button press, move slider up and down
    if keyCode(oneKey)
        exitvas = true;
    elseif keyCode(twoKey)
        sliderY = sliderY + pixelsPerPress;
    elseif keyCode(threeKey)
        sliderY = sliderY - pixelsPerPress;
    end
    
    % We set bounds to make sure our slider doesn't go completely off of
    % the VAS boundaries
    if sliderY < yCenter-(vasL/2)
        sliderY = yCenter-(vasL/2);
    elseif sliderY > yCenter+(vasL/2)
        sliderY = yCenter+(vasL/2);
    end
    sliderRect = CenterRectOnPointd(sbaseRect, sliderX, sliderY);
    
    % Draw to the screen
    DrawFormattedText(w, 'Now select the HIGHEST point in the scale and enter', xCenter-230, screenYpixels * 0.20, white);
    Screen('FillRect', w, [125 125 125], tickRect_m);
    Screen('FillRect', w, [125 125 125], tickRect_t);
    Screen('FillRect', w, [125 125 125], tickRect_b);
    Screen('FillRect', w, [125 125 125], vasRect);
    Screen('FillRect', w, red, sliderRect);
    
    % Flip to the screen
    Screen('Flip', w);
end

vas.max = sliderY;
DrawFormattedText(w, '+', xCenter, yCenter, white);
Screen('Flip', w);

%% WAIT TTLs

if MR_state == 1
    ttls=0;
    while ttls < nttls
        [keyIsDown,secs,keyCode] = KbCheck;
        if keyCode(sevenKey)
            WaitSecs(0.1)
            ttls=ttls+1;
        end
    end
else
    WaitSecs(0.1);
end

%% PRESENTATION

DrawFormattedText(w, '+', xCenter, yCenter, white);
tstart=GetSecs;

for t=1:length(s)
    DrawFormattedText(w, '+', xCenter, yCenter, white);
    Screen('Flip', w);
    
    if t == 1
        trial_est_startime(t) = tstart;
    else
        trial_est_startime(t) = tstart + (tot_run_time(t-1)) ;
    end
    
    [realWakeupTimeSecs(t,1)] = WaitSecs('UntilTime', trial_est_startime(t) + timings(t,2) );
    ds.queueOutputData(stimCurrent(s(t))/5 * stimWave); % Transfom mA in Volt for the NI box
    ds.startForeground(); %send pulse
    
    resp_idx=find(t==trials_resp);
    if isempty(resp_idx)
        probab_pxl(t)=NaN;
        RT(t,:)=NaN;
        missed_resp(t,:)=NaN;
        prob_type(t)=NaN;
    else
        
        t0=GetSecs;
        
        %% probability estimate
        sliderY = yCenter;
        disp(s(t));
        DrawFormattedText(w, 'ESTIMATE PROBABILITY', xCenter-130, screenYpixels * 0.20, white);
        if s(t) == 2 % i.e. H
            prob_type(t) = 0;
            DrawFormattedText(w, 'H > H', xCenter-30, yCenter - 180, white);
            DrawFormattedText(w, 'H > L', xCenter-30, yCenter + 200, white);
        else
            prob_type(t) = 1;
            DrawFormattedText(w, 'L > L', xCenter-30, yCenter - 180, white);
            DrawFormattedText(w, 'L > H', xCenter-30, yCenter + 200, white);
        end
        DrawFormattedText(w, '100%', xCenter+25, yCenter - 145, [125 125 125]);
        DrawFormattedText(w, '100%', xCenter+25, yCenter + 155, [125 125 125]);
        DrawFormattedText(w, '50%', xCenter+25, yCenter+10, [125 125 125]);
        Screen('FillRect', w, [125 125 125], tickRect_m);
        Screen('FillRect', w, [125 125 125], tickRect_t);
        Screen('FillRect', w, [125 125 125], tickRect_b);
        Screen('FillRect', w, [125 125 125], vasRect);
        Screen('FillRect', w, red, sliderRect);
        Screen('Flip', w);
        
        % This is the cue which determines whether we exit the vas
        exitvas = false;
        missed_resp(t,1) = 1;
        
        % Loop the animation until the one key is pressed or time has
        % elapsed
        while exitvas == false
            
            % quit if max time elapses
            clock=GetSecs;
            if ((clock - t0) > resptime), exitvas = true; end
            
            % Check the keyboard to see if a button has been pressed
            [keyIsDown,keyTime, keyCode] = KbCheck;
            
            if ((keyTime - t0) > resptime), exitvas = true; end
            
            % Depending on the button press, move slider up and down
            if keyCode(oneKey)
                exitvas = true;
                RT(t,1) = keyTime - t0;
                missed_resp(t,1) = 0;
            elseif keyCode(twoKey)
                sliderY = sliderY + pixelsPerPress;
            elseif keyCode(threeKey)
                sliderY = sliderY - pixelsPerPress;
            end
            
            % We set bounds to make sure our slider doesn't go completely off of
            % the VAS boundaries
            if sliderY < yCenter-(vasL/2)
                sliderY = yCenter-(vasL/2);
            elseif sliderY > yCenter+(vasL/2)
                sliderY = yCenter+(vasL/2);
            end
            sliderRect = CenterRectOnPointd(sbaseRect, sliderX, sliderY);
            
            % Draw to the screen
            DrawFormattedText(w, 'ESTIMATE PROBABILITY', xCenter-130, screenYpixels * 0.20, white);
            if s(t) == 2 % i.e. H
                DrawFormattedText(w, 'H > H', xCenter-30, yCenter - 180, white);
                DrawFormattedText(w, 'H > L', xCenter-30, yCenter + 200, white);
            else
                DrawFormattedText(w, 'L > L', xCenter-30, yCenter - 180, white);
                DrawFormattedText(w, 'L > H', xCenter-30, yCenter + 200, white);
            end
            DrawFormattedText(w, '100%', xCenter+25, yCenter - 145, [125 125 125]);
            DrawFormattedText(w, '100%', xCenter+25, yCenter + 155, [125 125 125]);
            DrawFormattedText(w, '50%', xCenter+25, yCenter+10, [125 125 125]);
            Screen('FillRect', w, [125 125 125], tickRect_m);
            Screen('FillRect', w, [125 125 125], tickRect_t);
            Screen('FillRect', w, [125 125 125], tickRect_b);
            Screen('FillRect', w, [125 125 125], vasRect);
            Screen('FillRect', w, red, sliderRect);
            
            % Flip to the screen
            Screen('Flip', w);
        end
        probab_pxl(t) = sliderY;
        
        DrawFormattedText(w, '+', xCenter, yCenter, white);
        Screen('Flip', w);
        WaitSecs('UntilTime', (trial_est_startime(t) + tot_trial_time(t)) );
        
    end
    
    save(['probexp_1500ms_sub' num2str(sub) '-sess' num2str(sess) '.mat'],...
        'probab_pxl','RT','missed_resp','stimCurrent',...
        's', 'gen_p1', 'gen_p1g2', 'gen_p2g1', 'screenXpixels', 'screenYpixels',...
        'xCenter','yCenter','vas','prob_type',...
        'trials_resp','tot_trial_time','timings','tot_run_time',...
        'trial_est_startime','realWakeupTimeSecs','tstart');
    
end

%% close

stop(ds);
Priority(0);
ShowCursor;
sca;







