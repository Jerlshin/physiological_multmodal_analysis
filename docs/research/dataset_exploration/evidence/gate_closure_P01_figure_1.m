%figure 1
clear, clc, close all
addpath(genpath('./'))

%load raw data from experiment 1
load('../data/Experiment_1/data_eye_experiment_1_video_1','data_eye','fs','Nparticipant')

%load frequency resolved ISC
load('../data/Experiment_1/ISC_eye_freq_cluster_experiment_1_39fe5519cf74e52fb7aaf0956cd89e4a2_fs=125.mat',...
    'ISC_eye_xy_persubject_freq_avgstim','ISC_eye_pupil_persubject_freq_avgstim','clusters_ISC_eye_pupil_attend_distract_significant','clusters_ISC_eye_xy_attend_distract_significant')

% isc
isc_experiment_lab_1 = load('../data/Experiment_1/ISC_eye_ts_trigger_stimtracker_bf_interp_linear_filt_0_10_miss_1_new.mat');
Nstim = size(isc_experiment_lab_1.ISC_eye_xypupil_persubject,2);
Nview  = size(isc_experiment_lab_1.ISC_eye_xypupil_persubject,1);

Nparticipant_lab_1 = Nparticipant;

% demographics
demographics_experiment_lab_1 = load('../data/Experiment_1/Experiment_1_demographics.mat');

% points
points_experiment_lab_1 = load('../data/Experiment_1/Experiment_1_Points.mat');

% load baseline performance
load('../data/Experiment_1/Experiment_1_2_Points_baseline.mat','Npoints_baseline_subject','Npoints_baseline_stim','Npoints_baseline_m');

%sampling frequency of the lab data from experiment 1
Ts = 1/fs;

%% plot variables
colors =   [{'DarkSlateGray'}, {'SlateBlue'},{'OrangeRed'},{'DodgerBlue'},{'MediumVioletRed'},{'DarkOrange'},{'Teal'},{'DarkMagenta'},{'RoyalBlue'},{'Olive'},{'Maroon'}];
colors_degree = {'Gold','Red','Purple'};
colors_timeseries_attend = {'DarkGoldenRod','Brown','ForestGreen'};
colors_style = {'Black','Black','Black','Black'};
marker_style = {'square','diamond','h','p'};
color_attend = rgb('Black');
color_distract = rgb('Red');

styles_universal = [{'Animation'},...
                    {'Writing hand & Animation' },...
                    {'Presenter & Animation'   },...
                    {'Presenter & Glass Board' }];

markersize_teaching_style = [10 10 11 10];
marker_scatter_size_teaching_style = [90 90 110 110];
marker_scatter_size = 120;

videoNames = {'Stars','Lightbulbs','Immune','Internet','Birth rate'};

figuredir = '../figures/';

FontSize_titles = 7;
FontSize_small = 6;
FontSize_letters = 8;
marker_size = 5;
LineWidth_lines = 0.3;
LineWidth_box = 0.2;
Length_Arrow = 2;

%% Section 1: Effects of attention on eye movements during video presentation

% demographics
demographics_experiment_lab_1 = struct2table(demographics_experiment_lab_1.demographicData);

fprintf('Experiment 1: N=%d, %d females, age %d-%d, mean=%1.2f, SD=%1.2f\n',Nparticipant_lab_1,sum(contains(demographics_experiment_lab_1.Sex,'Female')),min(demographics_experiment_lab_1.Age),max(demographics_experiment_lab_1.Age),mean(demographics_experiment_lab_1.Age),std(demographics_experiment_lab_1.Age))

% ISC
fprintf('Experiment 1: Attending, ISC median %1.2f, IQR=%1.2f\n',median(isc_experiment_lab_1.ISC_eye_xypupil_persubject_avgstim{1}), iqr(isc_experiment_lab_1.ISC_eye_xypupil_persubject_avgstim{1}))

fprintf('Experiment 1: Disctracted, ISC median %1.2f, IQR=%1.2f\n',median(isc_experiment_lab_1.ISC_eye_xypupil_persubject_avgstim{2}), iqr(isc_experiment_lab_1.ISC_eye_xypupil_persubject_avgstim{2}))

% three way anova
interaction_mat = eye(3);
[p_xypupil_attend,tbl_xypupil_attend,stats_xypupil_attend,terms_xypupil_attend] = anovan(cat(1,isc_experiment_lab_1.ISC_eye_xypupil_persubject{:}),{cat(1,isc_experiment_lab_1.ISC_eye_factor_participant{:}),cat(1,isc_experiment_lab_1.ISC_eye_factor_stimuli{:}),cat(1,isc_experiment_lab_1.ISC_eye_factor_view{:})},'model',interaction_mat,'random',[1],'varnames',{'Subject','Stimuli','Attention'},'display','off');

fprintf('\nthree way anova\n')
displayAnova(tbl_xypupil_attend)

% AUC
AUC_xypupil_avgstim = rocarea([isc_experiment_lab_1.ISC_eye_xypupil_persubject_avgstim{1,1}; isc_experiment_lab_1.ISC_eye_xypupil_persubject_avgstim{2,1}],[ones(Nparticipant_lab_1,1); zeros(Nparticipant_lab_1,1)]);

for iStim = 1:Nstim
    [AUC_xypupil_perstim(iStim,:),TP_xypupil_perstim(iStim,:),FP_xypupil_perstim(iStim,:),FC_xypupil_perstim(iStim,:)] = ...
        rocarea([isc_experiment_lab_1.ISC_eye_xypupil_persubject{1,iStim}; isc_experiment_lab_1.ISC_eye_xypupil_persubject{2,iStim}],[ones(Nparticipant_lab_1,1); zeros(Nparticipant_lab_1,1)]);
end

fprintf('ISC attend vs. disattend AUC_avg=%1.3f +- %1.3f\n',AUC_xypupil_avgstim,std(AUC_xypupil_perstim));

%% Figure 1
fig = figure('Units','centimeters','Position',[2 2 17.8 10],'PaperUnits','centimeters','PaperSize', [17.8 10],'Color','White');


% Panel A: eye tracking time series - attending
ah = annotation('textbox',[0.0 0.99 0.05 0.02],'String','a)','FontSize',FontSize_letters,'LineStyle','none'); %,'FontWeight','bold'
ah = annotation('textbox',[0.15 0.99 0.2 0.02],'String','Attending condition','FontSize',FontSize_titles+1,'LineStyle','none','FontWeight','bold');

iStim = 1;
iView = 1;
[~,idx_sort] = sort(isc_experiment_lab_1.ISC_eye_xypupil_persubject{iView,iStim},'descend');

subjects = [1 5]; 
timeseries = data_eye{iView,iStim}(:,:,subjects);

timescale = 0:Ts:(length(timeseries)/fs)-Ts;

time_segment = [150 175]; 
samples_segment = time_segment*fs;
titles = {'Horizontal gaze','Vertical gaze','Pupil size'};

subplot_pos = [1 2; 5 6; 9 10];
for iCord = 1:3
    subplot(4,4,subplot_pos(iCord,:))
    for iSubject = 1:length(subjects)
        timeseries_local = timeseries(samples_segment(1):samples_segment(2),iCord,iSubject);
        p(iSubject) = plot(timescale(samples_segment(1):samples_segment(2)),timeseries_local,...
            'Color',rgb(colors_timeseries_attend{iSubject}),'LineWidth',LineWidth_lines); hold on
    end
    
    subylim(iCord,:) = get(gca,'Ylim');
    xlim(time_segment)
    
    if iCord ==1
        line([150.5 151.5],[1140 1140],'Color',rgb('Gray'),'LineWidth',LineWidth_lines)
        text(149.6,1320,'1 second','Color',rgb('Gray'),'FontSize',FontSize_small)
        legh = legend(p,'S1','S2','Orientation','horizontal');
        legh.ItemTokenSize = [5 5];
        ylim([0 1300])
        
        set(legh,'Position',get(legh,'Position') + [0.0 0.05 0 0])
        set(legh,'Box','off', 'FontSize',FontSize_small-1)
    end
    
    set(gca,'FontSize',FontSize_small)
    
    %subplot position
    if iCord == 1
        set(gca,'Position',get(gca,'Position') + [-0.11 0.04 0.09 -0.04])
    elseif iCord == 2
        set(gca,'Position',get(gca,'Position') + [-0.11 0.10 0.09 -0.04])
    else
        set(gca,'Position',get(gca,'Position') + [-0.11 0.16 0.09 -0.04])
    end
    
    %title position
    t = title(titles{iCord},'FontSize',FontSize_titles);
    if iCord == 1
        set(t,'Position',get(t,'Position') + [0 -40 0 ])
    elseif iCord == 2
        set(t,'Position',get(t,'Position') + [0 20 0 ])
    elseif iCord == 3
        set(t,'Position',get(t,'Position') + [0 100 0 ])       
    end
    
    set(gca,'TickLength',[0 0])
    set(gca,'Ytick',[])
    set(gca,'Box','off')
    set(gca,'XtickLabels',[])
    set(gca,'XColor','Black','YColor','White','TickDir','out')
    ylabel('a.u.','FontSize',FontSize_small,'Color','Black')
end


% Panel B: eye tracking time series - disctracted
ah = annotation('textbox',[0.5 0.99 0.05 0.02],'String','b)','FontSize',FontSize_letters,'LineStyle','none'); %,'FontWeight','bold'
ah = annotation('textbox',[0.65 0.99 0.2 0.02],'String','Distracted condition','FontSize',FontSize_titles+1,'LineStyle','none','FontWeight','bold');

iStim = 1;
iView = 2;
subjects = [1 5]; 

timeseries = data_eye{iView,iStim}(:,:,subjects);

timescale = 0:Ts:(length(timeseries)/fs)-Ts;

time_segment = [120 145]; %120 145
samples_segment = time_segment*fs;

colors_timeseries_distracted = {'Maroon','LightSeaGreen'};

subplot_pos = [3 4; 7 8; 11 12];
for iCord = 1:3
    subplot(4,4,subplot_pos(iCord,:))
    for iSubject = 1:length(subjects)
        timeseries_local = timeseries(samples_segment(1):samples_segment(2),iCord,iSubject);
        p(iSubject) = plot(timescale(samples_segment(1):samples_segment(2)),timeseries_local,...
            'Color',rgb(colors_timeseries_attend{iSubject}),'LineWidth',LineWidth_lines); hold on
    end
    
    subylim(iCord,:) = get(gca,'Ylim');
    xlim(time_segment)
    
    if iCord ==1
        line([120.5 121.5],[1140 1140],'Color',rgb('Gray'),'LineWidth',LineWidth_lines)
        text(119.6,1320,'1 second','Color',rgb('Gray'),'FontSize',FontSize_small)
        legh = legend(p,'S1','S2','Orientation','horizontal');
        legh.ItemTokenSize = [5 5];
        ylim([0 1300])
        set(legh,'Position',get(legh,'Position') + [0.1 0.05 0 0])
        set(legh,'Box','off', 'FontSize',FontSize_small-1)
    end
    
    set(gca,'FontSize',FontSize_small)
    
    %subplot position
    if iCord == 1
        set(gca,'Position',get(gca,'Position') + [-0.02 0.04 0.09 -0.04])
    elseif iCord == 2
        set(gca,'Position',get(gca,'Position') + [-0.02 0.10 0.09 -0.04])
    else
        set(gca,'Position',get(gca,'Position') + [-0.02 0.16 0.09 -0.04])
    end
    
    %title position
    t = title(titles{iCord},'FontSize',FontSize_titles);
    if iCord == 1
        set(t,'Position',get(t,'Position') + [0 -40 0 ])
    elseif iCord == 2
        set(t,'Position',get(t,'Position') + [0 20 0 ])
    elseif iCord == 3
        set(t,'Position',get(t,'Position') + [0 100 0 ])       
    end
    
    set(gca,'TickLength',[0 0])
    set(gca,'Ytick',[])
    set(gca,'Box','off')
    set(gca,'XtickLabels',[])
    set(gca,'XColor','Black','YColor','White','TickDir','out')
    ylabel('a.u.','FontSize',FontSize_small,'Color','Black')
end

% Panel C: ISC attend vs. distracted

%define points used for panel c:
f1 = [1 3 5 7 9];
f2 = [2 4 6 8 10];
for iStim = 1:Nstim
    xpoints_eye_v1{iStim,1} = f1(iStim)*ones(1,Nparticipant_lab_1);
    xpoints_eye_v2{iStim,1} = f2(iStim)*ones(1,Nparticipant_lab_1);
end

subplot(4,4,13:14)
for iStim=1:Nstim
    for iParticipant = 1:Nparticipant_lab_1
        if ~isnan(isc_experiment_lab_1.ISC_eye_xypupil_persubject{1,iStim}(iParticipant)) && ~isnan(isc_experiment_lab_1.ISC_eye_xypupil_persubject{2,iStim}(iParticipant))
            s1 = scatter(xpoints_eye_v1{iStim}(iParticipant),isc_experiment_lab_1.ISC_eye_xypupil_persubject{1,iStim}(iParticipant),marker_size,'MarkerFaceColor',rgb(colors{iStim}),'MarkerEdgeColor',rgb(colors{iStim})); hold on
            s2 = scatter(xpoints_eye_v2{iStim}(iParticipant),isc_experiment_lab_1.ISC_eye_xypupil_persubject{2,iStim}(iParticipant),marker_size,'MarkerFaceColor',rgb(colors{iStim}),'MarkerEdgeColor',rgb(colors{iStim}));
            ah = line([xpoints_eye_v1{iStim}(iParticipant),xpoints_eye_v2{iStim}(iParticipant)], [isc_experiment_lab_1.ISC_eye_xypupil_persubject{1,iStim}(iParticipant),isc_experiment_lab_1.ISC_eye_xypupil_persubject{2,iStim}(iParticipant)],...
                'Color',rgb(colors{iStim}),'LineWidth',LineWidth_lines);
        end
    end
   
    if iStim == Nstim
        text(f1(iStim),0.5,videoNames{iStim}(1:5),'Color','Black','FontSize',FontSize_small)
    else
        text(f1(iStim),0.5,videoNames{iStim},'Color','Black','FontSize',FontSize_small)
    end
end

set(gca,'Position',get(gca,'Position') + [-0.08 -0.03 0.02 0.2])
set(gca,'XTick',sort([f1 f2]))
set(gca,'FontSize',FontSize_small)
set(gca,'XTickLabel',repmat({'A','D'},1,Nstim))
ylabel('ISC','FontSize',FontSize_small)
title('Attentional modulation','FontSize',FontSize_titles)
set(gca,'TickLength',[0 0])
set(gca,'Box','on')
xlim([0.5,10.5])
ylim([-0.05 0.55])
sb_pos = get(gca,'Position'); offset_x = 0.03; offset_y = 0.06;
annotation('textbox',[0 sb_pos(2)+offset_y sb_pos(3) sb_pos(4)], 'string', 'c)','FontSize', FontSize_letters,'LineStyle','none')
set(gca,'LineWidth',LineWidth_box)

% Panel D: Frequency resolved ISC
center_frequencies = 2.^(-5:0.1:5);
cutoff_frequencies = center_frequencies'.*[0.9 1.1];
Nfrequency = length(center_frequencies);

ylims = [-0.1 0.4];
sb_A = subplot(4,4,15);

% panel D1
[s_attend,ph_attend] = boundedline(center_frequencies, squeeze(nanmean(ISC_eye_xy_persubject_freq_avgstim(:,1,:),1)), squeeze(nanstd(ISC_eye_xy_persubject_freq_avgstim(:,1,:),[],1))./sqrt(size(ISC_eye_xy_persubject_freq_avgstim,1)),'-k.','transparency',0.05);
set(s_attend,'LineWidth',LineWidth_lines), set(s_attend,'Marker','none'), hold on, set(s_attend,'Color',color_attend),set(ph_attend,'FaceColor',color_attend),set(ph_attend,'FaceAlpha',0.3)

[s_distracted,ph_distracted] = boundedline(center_frequencies, squeeze(nanmean(ISC_eye_xy_persubject_freq_avgstim(:,2,:),1)), squeeze(nanstd(ISC_eye_xy_persubject_freq_avgstim(:,1,:),[],1))./sqrt(size(ISC_eye_xy_persubject_freq_avgstim,1)),'-r.','transparency',0.05);
set(s_distracted,'LineWidth',LineWidth_lines), set(s_distracted,'Marker','none'), set(s_distracted,'Color',color_distract),set(ph_distracted,'FaceColor',color_distract),set(ph_distracted,'FaceAlpha',0.3)

% title('Eye movements','FontSize',FontSize)
title('Horizontal and vertical','FontSize',FontSize_titles)

set(gca,'Xscale','log')
set(gca,'Box','on')
xlabel('Frequency [Hz]')
ylabel('ISC')
set(gca,'FontSize',FontSize_small)
set(gca,'LineWidth',LineWidth_box)
xlim([min(center_frequencies) max(center_frequencies)])
xticks = 10.^(-4:1:1);
set(gca,'Xtick',xticks)
set(gca,'XTickLabel',cellfun(@(s) strrep(s,'.00',''),arrayfun(@(s) sprintf('%1.2f',s),xticks,'UniformOutput',false),'UniformOutput',false))
set(sb_A,'Position',get(sb_A,'Position')+[-0.04 -0.03 0.07 0.2])
sb_A_pos = get(sb_A,'Position'); offset_x = 0.06; offset_y = 0.06;
annotation('textbox',[sb_A_pos(1)-offset_x sb_A_pos(2)+offset_y sb_A_pos(3) sb_A_pos(4)], 'string', 'd)','FontSize', FontSize_small+2,'LineStyle','none')


[idx_start,idx_end] = plot_significance_areas(sb_A,clusters_ISC_eye_xy_attend_distract_significant,[],cutoff_frequencies,ylims);
fprintf('ISC eye: Frequency range %1.2f-%1.2fHz\n',cutoff_frequencies(idx_start,1),cutoff_frequencies(idx_end,2))
uistack(s_attend,'top')
uistack(s_distracted,'top')

% panel D2
sb_B = subplot(4,4,16);
[s_attend,ph_attend] = boundedline(center_frequencies, squeeze(nanmean(ISC_eye_pupil_persubject_freq_avgstim(:,1,:),1)), squeeze(nanstd(ISC_eye_pupil_persubject_freq_avgstim(:,1,:),[],1))./sqrt(size(ISC_eye_pupil_persubject_freq_avgstim,1)),'-k.','transparency',0.05);
set(s_attend,'LineWidth',LineWidth_lines), set(s_attend,'Marker','none'), hold on, set(s_attend,'Color',color_attend),set(ph_attend,'FaceColor',color_attend),set(ph_attend,'FaceAlpha',0.3)

[s_distracted,ph_distracted] = boundedline(center_frequencies, squeeze(nanmean(ISC_eye_pupil_persubject_freq_avgstim(:,2,:),1)), squeeze(nanstd(ISC_eye_pupil_persubject_freq_avgstim(:,1,:),[],1))./sqrt(size(ISC_eye_pupil_persubject_freq_avgstim,1)),'-r.','transparency',0.05);
set(s_distracted,'LineWidth',LineWidth_lines), set(s_distracted,'Marker','none'), set(s_distracted,'Color',color_distract),set(ph_distracted,'FaceColor',color_distract),set(ph_distracted,'FaceAlpha',0.3)

title('Pupil size','FontSize',FontSize_titles)
set(gca,'Box','on')
set(gca,'Xscale','log')
xlabel('Frequency [Hz]')
set(gca,'FontSize',FontSize_small)
set(gca,'LineWidth',LineWidth_box)
xlim([min(center_frequencies) max(center_frequencies)])
% ylim([-0.015 0.02])
xticks = 10.^(-4:1:1);
set(gca,'Xtick',xticks)
set(gca,'XTickLabel',cellfun(@(s) strrep(s,'.00',''),arrayfun(@(s) sprintf('%1.2f',s),xticks,'UniformOutput',false),'UniformOutput',false))
% set(gca,'Ytick',(-10:5:10)/1e3)
set(sb_B,'Position',get(sb_B,'Position')+[0.01 -0.03 0.07 0.2])

[idx_start,idx_end] = plot_significance_areas(sb_B,clusters_ISC_eye_pupil_attend_distract_significant,[],cutoff_frequencies,ylims);
for idx = 1:length(idx_start)
    fprintf('ISC pupil: Frequency range %1.2f-%1.2fHz\n',cutoff_frequencies(idx_start(idx),1),cutoff_frequencies(idx_end(idx),2))
end

legh = legend([s_attend s_distracted],{'Attending','Distracted'},'FontSize',FontSize_small);
legh.ItemTokenSize = [5 5];
uistack(s_attend,'top')
uistack(s_distracted,'top')

set(fig,'PaperPositionMode','manual')
print([figuredir 'Figure_1.pdf'],'-dpdf','-painters',fig)
