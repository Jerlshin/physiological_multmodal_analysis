function data = preprocessEEGdata(data,options,fs,chanlocs)
% data = preprocessEEGdata(data,options,fs,chanlocs)
%
% jmad/jenma 2018

if ~isfield(options,'artifact_extension')
	options.artifact_extension = 0.04; % 40 ms
end
	
if ~isfield(options,'center_frequency_eeg')
    options.center_frequency_eeg = []; % this is used to indicate what the center frequency is for a bandpass filtering (not used in this routine)
end

if ~isfield(options,'doVisualization')
    options.doVisualization = false;
end

if ~isfield(options,'doRPCA')
    options.doRPCA = false;
end

fprintft('Preprocessing EEG data\n')

%% Design filters to remove drift in signal. 
% Important!!! this step should be done BEFORE segmentation of the stimuli to reduce effects of potential ringing of the filter

if isempty(options.center_frequency_eeg)
    HPcutoff = 0.5; % HP filter cut-off frequequency in Hz
else
    HPcutoff = 0.01; % HP filter cut-off frequequency in Hz
end

[zhp,php,khp]=butter(5,HPcutoff/fs*2,'high'); % drift removal
[znotch,pnotch,knotch]=butter(5,[59 61]/fs*2,'stop'); % 60Hz line noise
Z = [zhp;znotch];
P = [php;pnotch];
k = khp*knotch;
sos = zp2sos(Z,P,k);

% high-pass filter and remove line noise
data = sosfilt(sos,data);

%% remove eye blinks using least squares filtering using EOG channels
data_eog = data(:, options.eogchannels);

% remove eog channels that are constant (messes up the EOG regression)
data_eog(:, std(data_eog,[],1) == 0) = [];

%do not include outliers when doing the eog removal (if outliers are present in the EOG signal the regression introduces artifacts, it doesnt remove them)
mask = all(bsxfun(@lt,abs(data-median(data,1)),options.kIQR_eog*iqr(data,1)),2);

% regression with clean eog
data = data - data_eog*(data_eog(mask,:)\data(mask,:));

% return only eeg channels
data = data(:,options.eegchannels);

%% clean data using robust-PCA
if options.doRPCA
    fprintft('Computing RPCA...')
    % run RPCA on data
    data = inexact_alm_rpca(data);
    fprintf('done\n')
end

%% artifact rejection
if options.doRPCA, kIQD=4; else kIQD = 3; end      % multiple of interquartile differences to mark as outliers
threshold = kIQD*iqr(data,1);
mask = bsxfun(@gt,abs(data-median(data,1)),threshold);

% NaN data
data(mask) = NaN;

% remove <options.artifact_extension> before and after an artifact
h=[1; zeros(round(options.artifact_extension*fs)-1,1)];
data = filter(h,1,flipud(filter(h,1,flipud(data))));

%fill bad samples (artifacts)
data = fillBadSamples(data,options.artifactFill,chanlocs,fs,options);

%% Mark outliers as 0, to avoid NaN coding and to discount noisy channels
% (not really needed as the fillBadSamples routine cleans it, but better be safe than sorry)
if sum(isnan(data(:)))~=0
    fprintf('Setting %d NaNs to zero\n',sum(isnan(data(:))))
    data(isnan(data))=0;
end

fprintft('Preprocessing complete\n')
