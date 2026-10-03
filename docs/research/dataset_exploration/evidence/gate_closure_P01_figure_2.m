%figure 2
clear, clc
addpath(genpath('./'))

stim_display = 5;

load(['../data/Experiment_1/data_eye_experiment_1_video_',num2str(stim_display),'.mat'],'data_eye','fs','Nparticipant')

videoNames = {'Stars','Lightbulbs','Immune','Internet','Birth rate'};

figuredir = '../figures/';

%smpling frequency of experiment 1
Ts = 1/fs;

FontSize_titles = 7;
FontSize_small = 6;
FontSize_letters = 8;
marker_size = 5;
LineWidth_lines = 0.3;
LineWidth_box = 0.2;
Length_Arrow = 2;

isc_experiment_1 = load('../data/Experiment_1/ISC_eye_ts_trigger_stimtracker_bf_interp_linear_filt_0_10_miss_1_new.mat');
isc_experiment_2 = load('../data/Experiment_2/ISC_eye_ts_trigger_stimtracker_bf_interp_linear_sync_audio_offset_f_0_10_miss_1_new.mat'); %ISC_eye_ts_trigger_stimtracker_bf_interp_linear_sync_audio_offset
isc_experiment_3 = load('../data/Experiment_3/ISC_eye_ts_trigger_stimtracker_bf_interp_linear_sync_audio_offset_f_0_10_miss_1_9be9ab32eb12846c3b6752c85b4f1f12_new.mat');

Nparticipant_1 = length(isc_experiment_1.ISC_eye_delta_factor_participant{1});
Nparticipant_2 = length(isc_experiment_2.ISC_eye_delta_factor_participant{1});
Nparticipant_3 = length(isc_experiment_3.ISC_eye_delta_factor_participant{1});

[~,~,XLS] = xlsread('../data/selfreport_experiment_1_2.xlsx');
T_questions_1_2 = cell2table(XLS(2:end,:),'VariableNames',XLS(1,:));

% [~,~,XLS] = xlsread('../data/Experiment_3/Questions_categories.xlsx');
[~,~,XLS] = xlsread('../data/selfreport_experiment_3.xlsx');
T_questions_3 = cell2table(XLS(2:end,:),'VariableNames',XLS(1,:));

colors_1_2 =   [{'SlateGray'}, {'SlateBlue'},{'OrangeRed'},{'DeepSkyBlue'},{'MediumVioletRed'}];
colors_3 = {'DarkOrange','Teal','DarkMagenta','RoyalBlue','Olive','Maroon'};

colors =   [colors_1_2 colors_3];
colors_learning_styles = {'Black','Black';'Black','Black'};%{'OrangeRed','Yellow';'Olive','Cyan'};
colors_teaching_style = [{'Black','Black','Black','Black'}; {'Black','Black','Black','Black'} ];%[{'SlateBlue','DarkOliveGreen','Teal','Silver'}; {'MediumSeaGreen','Khaki','BurlyWood','MistyRose'} ];
colors_timeseries_attend = {'DarkGoldenRod','Brown','ForestGreen'};

styles_1_2 = {'Writing hand & Animation';'Writing hand & Animation';'Animation';'Animation';'Animation'};
styles_3 = {'Presenter & Animation'; 'Presenter & Animation'; 'Writing hand & Animation'; 'Writing hand & Animation'; 'Presenter & Glass Board'; 'Presenter & Glass Board'};

marker_teaching_style = {'square','diamond','h','p'};
marker_style = {'square','diamond','h','p'};
markersize_teaching_style = [10 10 11 10];
marker_scatter_size_teaching_style_small = [10 10 11 11];
marker_scatter_size_teaching_style = [90 90 110 110];
marker_scatter_size = 120;

styles_teaching_universal = [{'Animation'},...
                           {'Writing hand & Animation' },...
                           {'Presenter & Animation'   },...
                           {'Presenter & Glass Board' }];
             
topics_universal = [{'Biology'},{'Physics'},{'Computer Science'}];

%% Experiment 1-3: load demographics 
T_demographics_experiment_1 = load('../data/Experiment_1/Experiment_1_demographics.mat'); T_demographics_experiment_1 = struct2table(T_demographics_experiment_1.demographicData);
T_demographics_experiment_2 =  load('../data/Experiment_2/Experiment_2_demographics.mat'); T_demographics_experiment_2 = struct2table(T_demographics_experiment_2.demographicData);
T_demographics_experiment_3 =  load('../data/Experiment_3/Experiment_3_demographics.mat'); T_demographics_experiment_3 = struct2table(T_demographics_experiment_3.demographicData);

%% Study 3
Nstim_3 = length(unique(T_questions_3.Video_no));
for iStim = 1:Nstim_3
    VideoNames_3(1,iStim) = unique(T_questions_3(T_questions_3.Video_no==iStim,:).Video_name);
    teaching_styles_3(1,iStim) = unique(T_questions_3(T_questions_3.Video_no==iStim,:).Style);
    Nquestions_3(1,iStim) = length(unique(T_questions_3(T_questions_3.Video_no==iStim,:).Local_Question_no));
    topic_area_3(1,iStim) = unique(T_questions_3(T_questions_3.Video_no==iStim,:).Topic);
end

teaching_styles_unique_3 = unique(teaching_styles_3);
Nstyle_3 = length(teaching_styles_unique_3);

topic_area_unique_3 = unique(topic_area_3);
Ntopics_3 = length(topic_area_unique_3);

gg = load('../data/Experiment_3/Experiment_3_T_answers_baseline.mat');
Npoints_baseline_m_3 = arrayfun(@(vid_no) mean(gg.T_answers_baseline_overview_points(gg.T_answers_baseline_overview_points.Video_no==vid_no,:).Npoints),1:Nstim_3);
Npoints_baseline_std_3 = arrayfun(@(vid_no) std(gg.T_answers_baseline_overview_points(gg.T_answers_baseline_overview_points.Video_no==vid_no,:).Npoints),1:Nstim_3);

%comprehension/recall
Npoints_R_baseline_m_3 = arrayfun(@(vid_no) mean(gg.T_answers_baseline_overview_points(gg.T_answers_baseline_overview_points.Video_no==vid_no,:).Npoints_R),1:Nstim_3);
Npoints_C_baseline_m_3 = arrayfun(@(vid_no) mean(gg.T_answers_baseline_overview_points(gg.T_answers_baseline_overview_points.Video_no==vid_no,:).Npoints_C),1:Nstim_3);

%% Score
points_experiment_1 = load('../data/Experiment_1/Experiment_1_Points.mat');
points_experiment_2 =  load('../data/Experiment_2/Experiment_2_Points.mat');
points_experiment_3 =  load('../data/Experiment_3/Experiment_3_Points.mat');

%% load baseline performance
gg = load('../data/Experiment_1/Experiment_1_2_Points_baseline.mat','Npoints_baseline_subject','Npoints_baseline_stim','Npoints_baseline_m');

Npoints_baseline_stim_m_1_2 = gg.Npoints_baseline_m;
Nparticipants_baseline_1_2 = size(gg.Npoints_baseline_subject,1);
Npoints_baseline_stim_1_2 = gg.Npoints_baseline_stim;
Npoints_baseline_subject_1_2 = gg.Npoints_baseline_subject;

%%
%Study 1 and 2
Nstim_1_2 = length(unique(T_questions_1_2.Video_no));
for iStim = 1:Nstim_1_2
    VideoNames_1_2(1,iStim) = unique(T_questions_1_2(T_questions_1_2.Video_no==iStim,:).Video_name);
    teaching_styles_1_2(1,iStim) = unique(T_questions_1_2(T_questions_1_2.Video_no==iStim,:).Style);
    Nquestions_1_2(1,iStim) = length(unique(T_questions_1_2(T_questions_1_2.Video_no==iStim & strcmpi(T_questions_1_2.Position,'Post'),:).Local_Question_no));
    topic_area_1_2(1,iStim) = unique(T_questions_1_2(T_questions_1_2.Video_no==iStim,:).Topic);
end

% naive participants
Npoints_baseline_m_1_2_m = mean(Npoints_baseline_stim_m_1_2);
Npoints_baseline_m_1_2_std = sqrt(sum((Nparticipants_baseline_1_2-1).*std(Npoints_baseline_stim_1_2,[],2).^2) ./ (Nparticipants_baseline_1_2*Nstim_1_2 - Nstim_1_2));

fprintf('Naive subjects: Score M=%1.2f, SD=%1.2f\n',Npoints_baseline_m_1_2_m,Npoints_baseline_m_1_2_std)

fprintf('Lab experiments participants: N=%d\n',Nparticipant_1+Nparticipant_2+Nparticipant_3)

%% Experiment 1: intentional Learning

fprintf('\nExperiment 1: N=%d, %d females, Age %d-%d M=%1.2f, SD=%1.2f\n',Nparticipant_1,sum(contains(T_demographics_experiment_1.Sex,'Female')),min(T_demographics_experiment_1.Age),max(T_demographics_experiment_1.Age),mean(T_demographics_experiment_1.Age),std(T_demographics_experiment_1.Age))

%summary statistics over score and ISC
fprintf('Experiment 1 (intentional Learning): Score (M=%1.2f%%, SD=%1.2f%%)\n',mean(points_experiment_1.Npoints_avgstim_post),std(points_experiment_1.Npoints_avgstim_post))
fprintf('Experiment 1 (intentional learning): ISC Mdn=%1.2f, IQR=%1.2f\n',median(isc_experiment_1.ISC_eye_xypupil_persubject_avgstim{1}),iqr(isc_experiment_1.ISC_eye_xypupil_persubject_avgstim{1}))

% comparing score to native cohort
[~,p,~,stats] = ttest2(points_experiment_1.Npoints_avgstim_post,Npoints_baseline_subject_1_2);
d = cohen_d(points_experiment_1.Npoints_avgstim_post,points_experiment_2.Npoints_avgstim_post);
fprintf('Experiment 1 (intentional Learning): Score (M=%1.2f%%, SD=%1.2f%%) vs. Naive cohort (M=%1.2f, SD=%1.2f%%): t(%d)=%1.2f, p=%1.2e, d=%1.2f\n',mean(points_experiment_1.Npoints_avgstim_post),std(points_experiment_1.Npoints_avgstim_post),Npoints_baseline_m_1_2_m,Npoints_baseline_m_1_2_std,stats.df,stats.tstat,p,d)


[r,p] = corr(isc_experiment_1.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_1.Npoints_avgstim_post);
fprintf('Experiment 1 (intentional Learning): ISC vs. Score (avg stim): r=%1.2f (p=%1.2e), N=%d\n',r,p,Nparticipant_1)

for iStim = 1:Nstim_1_2
    [r_isc_score_experiment_1(iStim),p_isc_score_experiment_1(iStim)] = corr(isc_experiment_1.ISC_eye_xypupil_persubject{1,iStim},points_experiment_1.Npoints_stim_post(:,iStim));
end

fprintf('Experiment 1 (intentional): ISC vs. Score r=%1.2f +- %1.2f, SD across %d videos (p<%1.2e)\n',mean(r_isc_score_experiment_1),std(r_isc_score_experiment_1),length(r_isc_score_experiment_1), max(p_isc_score_experiment_1))

%% Experiment 2: incidental Learning

fprintf('\n\nExperiment 2: N=%d, %d females, Age %d-%d M=%1.2f, SD=%1.2f\n',Nparticipant_2,sum(contains(T_demographics_experiment_2.Sex,'Female')),min(T_demographics_experiment_2.Age),max(T_demographics_experiment_2.Age),mean(T_demographics_experiment_2.Age),std(T_demographics_experiment_2.Age))

%summary statistics over score and ISC
fprintf('Experiment 2 (incidental Learning): Score (M=%1.2f%%, SD=%1.2f%%)\n',mean(points_experiment_2.Npoints_avgstim_post),std(points_experiment_2.Npoints_avgstim_post))
fprintf('Experiment 2 (incidental learning): ISC (Mdn=%1.2f, IQR=%1.2f)\n',median(isc_experiment_2.ISC_eye_xypupil_persubject_avgstim{1}),iqr(isc_experiment_2.ISC_eye_xypupil_persubject_avgstim{1}))

[r,p] = corr(isc_experiment_2.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_2.Npoints_avgstim_post);
fprintf('Experiment 2 (incidental Learning): ISC vs. Score: r(%d)=%1.2f (p=%1.2e), N=%d\n',Nparticipant_2-2,r,p,Nparticipant_2)

for iStim = 1:Nstim_1_2
    [r_isc_score_experiment_2(iStim),p_isc_score_experiment_2(iStim)] = corr(isc_experiment_2.ISC_eye_xypupil_persubject{1,iStim},points_experiment_2.Npoints_stim_post(:,iStim));
end

fprintf('Experiment 2 (incidental learning): ISC vs. Score r=%1.2f +- %1.2f, SD across %d videos (p<%1.2e)\n',mean(r_isc_score_experiment_2),std(r_isc_score_experiment_2),length(r_isc_score_experiment_2), max(p_isc_score_experiment_2))

%% Experiment 1 vs. Experiment 2
fprintf('\nDifferent learning scenarios\n')
[p,~,stats] = ranksum(isc_experiment_1.ISC_eye_xypupil_persubject_avgstim{1},isc_experiment_2.ISC_eye_xypupil_persubject_avgstim{1});
fprintf('Experiment 1 (intentional) ISC vs. Experiment 2 (incidental learning) ISC: z=%1.2f, p=%1.2e\n',stats.zval,p)

[~,p,~,stats] = ttest2(points_experiment_1.Npoints_avgstim_post,points_experiment_2.Npoints_avgstim_post);
d = cohen_d(points_experiment_1.Npoints_avgstim_post,points_experiment_2.Npoints_avgstim_post);
fprintf('Experiment 1 (intentional) Score (M=%1.2f%%, SD=%1.2f%%) vs. Experiment 2 (incidental learning) Score (M=%1.2f, SD=%1.2f%%): t(%d)=%1.2f, p=%1.2e, d=%1.2f\n',mean(points_experiment_1.Npoints_avgstim_post),std(points_experiment_1.Npoints_avgstim_post),mean(points_experiment_2.Npoints_avgstim_post),std(points_experiment_2.Npoints_avgstim_post),stats.df,stats.tstat,p,d)


%% Experiment 3: Question types
fprintf('\n\nRecognition and comprehension questions\n')

fprintf('Experiment 3: N=%d, %d females, Age %d-%d M=%1.2f, SD=%1.2f\n',Nparticipant_3,sum(contains(T_demographics_experiment_3.Sex,'Female')),min(T_demographics_experiment_3.Age),max(T_demographics_experiment_3.Age),mean(T_demographics_experiment_3.Age),std(T_demographics_experiment_3.Age))


[r_isc_comprehension,p_isc_comprehension] = corr(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_3.Npoints_avgstim_C);
fprintf('Comprehension: r(%d)=%1.2f (p=%1.2e), N=%d\n',sum(~isnan(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1}))-2,r_isc_comprehension,p_isc_comprehension,Nparticipant_3)


[r_isc_recognition,p_isc_recognition,df_isc_recognition] = nancorr(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_3.Npoints_avgstim_R);
fprintf('Recognition: r(%d)=%1.2f (p=%1.2e), N=%d\n',df_isc_recognition,r_isc_recognition,p_isc_recognition,Nparticipant_3)

[r,p,df] = nancorr(points_experiment_3.Npoints_avgstim_C,points_experiment_3.Npoints_avgstim_R);
fprintf('Comprehension vs. Recognition: Score r(%d)=%1.2f (p=%1.2e)\n',df,r,p)

p_r_to_z = compare_correlation_coefficients(r_isc_comprehension,r_isc_recognition,Nparticipant_3,Nparticipant_3);

fprintf('Comprehension vs. Recognition ISC vs. Score: Asymptotic z-test after Fisher r-to-z conversion, p=%1.2f\n',p_r_to_z)

fprintf('Score: Experiment 3 (M=%1.2f%%, SD=%1.2f%%)\n',mean(points_experiment_3.Npoints_avgstim),std(points_experiment_3.Npoints_avgstim))

%% Experiment 3: Video styles
fprintf('\n\nDifferent styles of instructional videos\n')
for iStyle = 1:Nstyle_3
    [r,p,df] = nancorr(isc_experiment_3.ISC_eye_xypupil_persubject_avgstyle{1,iStyle},points_experiment_3.Npoints_avgstyle(:,iStyle));
    fprintf('%s: r(%d)=%1.2f (p=%1.1e)\n',teaching_styles_unique_3{iStyle},df,r,p)
end

%% Figure 2
fig = figure('Units','centimeters','Position',[2 2 17.8 10],'PaperUnits','centimeters','PaperSize', [17.8 10],'Color','White');

% Panel A: eye tracking time series - attending with 1 non attending 
ah = annotation('textbox',[0.0 0.99 0.05 0.02],'String','a)','FontSize',FontSize_small+2,'LineStyle','none'); %,'FontWeight','bold'
view_display = 1;
titles = {'Horizontal gaze','Vertical gaze','Pupil size'};

[~,idx_sort] = sort(isc_experiment_1.ISC_eye_xypupil_persubject{view_display,stim_display},'descend');

subjects = [idx_sort(1:2); idx_sort(end-2)];
timeseries = data_eye{view_display}(:,:,subjects);

ISC_selected = isc_experiment_1.ISC_eye_xypupil_persubject{view_display,stim_display}(subjects);
Npoints_selected = points_experiment_1.Npoints_stim_post(subjects,stim_display);

timescale = 0:Ts:(length(timeseries)/fs)-Ts;

% time_segment = [1 floor(timescale(end))]; %150 175 ? [50 75]
time_segment = [90 115]; %150 175 ? [50 75]
samples_segment = time_segment*fs;

for iCord = 1:3
    subplot(4,8,(iCord-1)*8+1:(iCord-1)*8+3)
    for iSubject = 1:length(subjects)
        timeseries_local = timeseries(samples_segment(1):samples_segment(2),iCord,iSubject);
        p(iSubject) = plot(timescale(samples_segment(1):samples_segment(2)),timeseries_local,...
            'Color',rgb(colors_timeseries_attend{iSubject}),'LineWidth',LineWidth_lines); hold on
    end
    
    subylim(iCord,:) = get(gca,'Ylim');
    xlim(time_segment)
    
    if iCord ==1
        line([93.5 94.5],[1140 1140],'Color',rgb('Gray'),'LineWidth',LineWidth_lines)
        text(92.2,1300,'1 second','Color',rgb('Gray'),'FontSize',FontSize_small-1)
        lh = legend(p,'S1','S2','S3','Orientation','horizontal');
        lh.ItemTokenSize = [5 5];
        ylim([0 1300])
    end
    
    set(gca,'FontSize',FontSize_small)
    
    %subplot position
    if iCord == 1
        set(gca,'Position',get(gca,'Position') + [-0.11 0.08 0.05 -0.04])
    elseif iCord == 2
        set(gca,'Position',get(gca,'Position') + [-0.11 0.14 0.05 -0.04])
    else
        set(gca,'Position',get(gca,'Position') + [-0.11 0.2 0.05 -0.04])
    end
    
    %title position
    t = title(titles{iCord},'FontSize',FontSize_titles);
    if iCord == 1
        set(t,'Position',get(t,'Position') + [0 20 0 ])
    elseif iCord == 2
        set(t,'Position',get(t,'Position') + [0 20 0 ])
    elseif iCord == 3
        set(t,'Position',get(t,'Position') + [0 140 0 ])       
    end
    
    set(gca,'TickLength',[0 0])
    set(gca,'Ytick',[])
    set(gca,'Box','off')
    set(gca,'XtickLabels',[])
    set(gca,'XColor','Black','YColor','White','TickDir','out')
    ylabel('a.u.','FontSize',FontSize_small,'Color','Black')
end

set(lh,'Position',get(lh,'Position') + [0.02 0.03 0 0])
set(lh,'Box','off', 'FontSize',FontSize_small-1)

%  Panel B: Individual videos
ah = annotation('textbox',[0.62 0.99 0.15 0.02],'String','Individual videos','FontSize',FontSize_small+2,'LineStyle','none','FontWeight','bold');
ah = annotation('textbox',[0.36 0.99 0.05 0.02],'String','b)','FontSize',FontSize_small+2,'LineStyle','none'); %,'FontWeight','bold'

x_size = 0.04;
y_size = -0.03;
y_offset = 0.02;
x_offset = [-0.03 -0.01 0.01 0.03 0.05];
xlims = [0 0.49];
marker_scatter_size = 10;
stim_list = [1 5 4 3 2];
marker_LineWidth = 0.5;

for iStim = stim_list
    sph(iStim) = subplot(4,8,[iStim+3 iStim+11]);
    
    [~,LOCB] = ismember(teaching_styles_1_2{iStim},styles_teaching_universal);
    
    if ismember(iStim,[1 2])
        s = scatter(sph(iStim),isc_experiment_1.ISC_eye_xypupil_persubject{1,iStim},points_experiment_1.Npoints_stim_post(:,iStim),marker_scatter_size,'k','Marker',marker_style{LOCB},'MarkerFaceColor',rgb(colors{iStim}),'LineWidth',marker_LineWidth,'MarkerEdgeColor','Black'); hold on;
    else
        s = scatter(sph(iStim),isc_experiment_1.ISC_eye_xypupil_persubject{1,iStim},points_experiment_1.Npoints_stim_post(:,iStim),marker_scatter_size+3,'k','Marker',marker_style{LOCB},'MarkerFaceColor',rgb(colors{iStim}),'LineWidth',marker_LineWidth-0.1,'MarkerEdgeColor','Black'); hold on;
    end
    sppos = get(sph(iStim),'Position');
    
    EdgeColors = colors_timeseries_attend;
    
    if iStim ==1
        subplot_position = get(sph(iStim),'Position');
        for iSelected = 1:length(ISC_selected)
            s = scatter(sph(iStim),ISC_selected(iSelected),Npoints_selected(iSelected),marker_scatter_size+7,'Marker',marker_style{LOCB},'MarkerEdgeColor',rgb(EdgeColors{iSelected}),'MarkerFaceColor',rgb(EdgeColors{iSelected}),'LineWidth',marker_LineWidth);     
        end
        
        % create arrows to high selection
        
        %S1
        ah = annotation('textarrow',[0.45 0.5],[0.82 0.805],'String',sprintf('S%d',1),'FontSize',FontSize_small-1,'HeadLength',3,'HeadWidth',3);
        
        %S2
        ah = annotation('textarrow',[0.45 0.5],[0.75 0.785],'String',sprintf('S%d',2),'FontSize',FontSize_small-1,'HeadLength',3,'HeadWidth',3);
        
        %S3
        ah = annotation('textarrow',[0.47 0.44],[0.6 0.62],'String',sprintf('S%d',3),'FontSize',FontSize_small-1,'HeadLength',3,'HeadWidth',3);
        
    end
    
    [r,p,df,lh,ph] = line_function_confidence(isc_experiment_1.ISC_eye_xypupil_persubject{1,iStim},points_experiment_1.Npoints_stim_post(:,iStim),0.05,[xlims(1)+0.003 xlims(2)-0.003]);
    set(lh,'LineWidth',LineWidth_lines)
    lhb = line(xlims,[Npoints_baseline_stim_m_1_2(iStim) Npoints_baseline_stim_m_1_2(iStim)],'Color',rgb('Gray'),'LineStyle','--','LineWidth',LineWidth_lines);
    uistack(s,'top')
    set(gca,'FontSize',FontSize_small)
    set(gca,'LineWidth',LineWidth_box)
    xlabel('ISC','FontSize',FontSize_small)
    set(gca,'Box','on') 
    if iStim == 1
        ylabel('Score','FontSize',FontSize_small)
        set(gca,'YTick',[0:20:100])
    else
        set(gca,'YTickLabels','')
    end
    
    set(sph(iStim),'Position',get(sph(iStim),'Position') + [ x_offset(iStim) y_offset x_size y_size])
    title(sprintf('%s',VideoNames_1_2{iStim}),'FontSize',FontSize_titles)
    ylim([-7 125])
    xlim(xlims)
    set(gca,'TickLength',[0 0])
    set(gca,'LineWidth',LineWidth_box)
    apos = get(gca,'Position');
    ah = annotation_paper([apos(1)+0.003 apos(2)+apos(4)-0.07 0.06 0.065],r,p,df,FontSize_small-1);
    set(ah,'LineWidth',LineWidth_box)
end

% Panel C: ISC correlated with test score - intentional vs. incidental learning
ah = annotation('textbox',[0.08 0.49 0.18 0.02],'String','Learning scenario','FontSize',FontSize_small+2,'LineStyle','none','FontWeight','bold');
ah = annotation('textbox',[0.0 0.49 0.05 0.02],'String','c)','FontSize',FontSize_small+2,'LineStyle','none'); %,'FontWeight','bold'
y_offset = -0.05;
x_offset = [-0.09 -0.07];
xlims = [0.05 0.43];

sph_c(1) = subplot(4,8,25);
%Intentional Learning
s = scatter(isc_experiment_1.ISC_eye_xypupil_persubject_avgstim{1}, points_experiment_1.Npoints_avgstim_post,marker_scatter_size,'ko','MarkerFaceColor','Black'); hold on
% [r,p,lh] = line_function_jenma(eyetracking_study.ISC_eye_xypupil_persubject_avgstim{1},eyetracking_points.Npoints_avgstim_post,'Black',gca,[0.05 0.45]);
[r,p,df,lh,ph] = line_function_confidence(isc_experiment_1.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_1.Npoints_avgstim_post,0.05,[xlims(1)+0.002 xlims(2)-0.002]);
set(lh,'LineWidth',LineWidth_lines)
uistack(s,'top')
set(gca,'FontSize',FontSize_small)
set(gca,'LineWidth',LineWidth_box)
l = line([0.05 0.45],[Npoints_baseline_m_1_2_m Npoints_baseline_m_1_2_m],'Color',rgb('Gray'),'LineStyle','--','LineWidth',LineWidth_lines);
title('Intentional','FontSize',FontSize_titles)
xlabel('ISC','FontSize',FontSize_small)
ylabel('Score','FontSize',FontSize_small)
ylim([0 100])
xlim(xlims)
set(gca,'Box','on')
set(gca,'TickLength',[0 0])
% set(gca,'Position',get(gca,'Position')+[x_offset(1) y_offset x_size y_size])
apos = get(gca,'Position');
bpos = get(sph(1),'Position');
set(gca,'Position',[apos(1:2)+[x_offset(1) y_offset] bpos(3) bpos(4)-0.03])
apos = get(gca,'Position');
ah = annotation_paper([apos(1)+0.003 apos(2)+apos(4)-0.07 0.06 0.065],r,p,df,FontSize_small-1);
    
%Incidental Learning
sph_c(2) = subplot(4,8,26);
s = scatter(isc_experiment_2.ISC_eye_xypupil_persubject_avgstim{1}, points_experiment_2.Npoints_avgstim_post,marker_scatter_size,'ko','MarkerFaceColor',rgb('Gray')); hold on
% [r,p,lh] = line_function_jenma(multimodal_study.ISC_eye_xypupil_persubject_avgstim{1},multimodal_points.Npoints_avgstim_post,'Black',gca,[0.05 0.45]);
[r,p,df,lh,ph] = line_function_confidence(isc_experiment_2.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_2.Npoints_avgstim_post,0.05,[xlims(1)+0.002 xlims(2)-0.002]);
set(lh,'LineWidth',LineWidth_lines)
uistack(s,'top')
set(gca,'FontSize',FontSize_small)
set(gca,'LineWidth',LineWidth_box)
l = line([0.05 0.45],[Npoints_baseline_m_1_2_m Npoints_baseline_m_1_2_m],'Color',rgb('Gray'),'LineStyle','--','LineWidth',LineWidth_lines);
title('Incidental','FontSize',FontSize_titles)
xlabel('ISC','FontSize',FontSize_small)
% ylabel('Score','FontSize',FontSize)
set(gca,'YTick',[])
ylim([0 100])
xlim(xlims)
set(gca,'Box','on')
set(gca,'TickLength',[0 0])
% set(gca,'Position',get(gca,'Position')+[x_offset(2) y_offset x_size y_size])
apos = get(gca,'Position');
bpos = get(sph(1),'Position');
set(gca,'Position',[apos(1:2)+[x_offset(2) y_offset] bpos(3) bpos(4)-0.03])
apos = get(gca,'Position');
ah = annotation_paper([apos(1)+0.003 apos(2)+apos(4)-0.07 0.06 0.065],r,p,df,FontSize_small-1);
    
% Panel D: Video styles
ah = annotation('textbox',[0.465 0.49 0.18 0.02],'String','Video style','FontSize',FontSize_small+2,'LineStyle','none','FontWeight','bold');
ah = annotation('textbox',[0.295 0.49 0.05 0.02],'String','d)','FontSize',FontSize_small+2,'LineStyle','none'); %,'FontWeight','bold'
y_offset = -0.05;
x_offset = [0.01 0.03 0.05]; 
xlims = [-0.01 0.55];
x_anno_offsets = [ 0.005 0.005]; 

for iStyle = Nstyle_3:-1:1
    sph_d(iStyle) = subplot(4,8,26+iStyle);
    [~,style_idx] = ismember(teaching_styles_unique_3(iStyle),styles_teaching_universal);
    stim_idx = find(ismember(teaching_styles_3,teaching_styles_unique_3(iStyle)));
    
    
    for iParticipant=1:Nparticipant_3
        sh(iParticipant,1) = scatter(isc_experiment_3.ISC_eye_xypupil_persubject_avgstyle{1,iStyle}(iParticipant), points_experiment_3.Npoints_avgstyle(iParticipant,iStyle),...
            marker_scatter_size_teaching_style_small(style_idx),'MarkerEdgeColor','Black','Marker',marker_teaching_style{style_idx},'MarkerFaceColor',rgb(colors_teaching_style{style_idx})); hold on
        %         text(ISC_eeg_persubject_avgstyle_sum{1,iStyle}(iParticipant)-0.01,Npoints_avgstyle(iParticipant,iStyle),num2str(options.participant_no(iParticipant)))
    end
    
    [r,p,df,lh,ph] = line_function_confidence(isc_experiment_3.ISC_eye_xypupil_persubject_avgstyle{1,iStyle},points_experiment_3.Npoints_avgstyle(:,iStyle),0.05,[xlims(1)+0.002 xlims(2)-0.002]);
    set(lh,'LineWidth',LineWidth_lines)
    l = line(xlims,[mean(Npoints_baseline_m_3(stim_idx)) mean(Npoints_baseline_m_3(stim_idx))],'Color',rgb('Gray'),'LineStyle','--','LineWidth',LineWidth_lines);
    
    set(gca,'FontSize',FontSize_small)
    title(sprintf('%s',strrep(teaching_styles_unique_3{iStyle},' & ',[' &' newline])),'FontSize',FontSize_titles)
    xlabel('ISC','FontSize',FontSize_small)
    set(gca,'Box','on')
    set(gca,'TickLength',[0 0])
    if iStyle == 1
        ylabel('Score','FontSize',FontSize_small)
    else
        set(gca,'YTickLabels','')
    end
    ylim([0 100])
    xlim(xlims)
    apos = get(gca,'Position');
    bpos = get(sph(1),'Position');
    set(gca,'Position',[apos(1:2)+[x_offset(iStyle) y_offset] bpos(3) bpos(4)-0.03])
    apos = get(gca,'Position');
    ah = annotation_paper([apos(1)+0.003 apos(2)+apos(4)-0.07 0.06 0.065],r,p,df,FontSize_small-1);
    set(gca,'LineWidth',LineWidth_box)
    set(ah,'LineWidth',LineWidth_box)
end

% Panel E: Question types
ah = annotation('textbox',[0.82 0.49 0.18 0.02],'String','Question type','FontSize',FontSize_small+2,'LineStyle','none','FontWeight','bold');
ah = annotation('textbox',[0.71 0.49 0.05 0.02],'String','e)','FontSize',FontSize_small+2,'LineStyle','none'); %,'FontWeight','bold'
x_offset = [0.03 0.05]; 
y_offset = -0.05;
xlims = [0.05 0.43];

%Comprehension
subplot(4,8,32);
scatter(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1}, points_experiment_3.Npoints_avgstim_C,marker_scatter_size,'ko','MarkerFaceColor',rgb('Black')); hold on
[r_isc_comprehension,p_isc_comprehension,df_isc_comprehension,lh] = line_function_confidence(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_3.Npoints_avgstim_C,0.05,[xlims(1)+0.002 xlims(2)-0.002]);
set(lh,'LineWidth',LineWidth_lines)
l = line(xlims,[mean(Npoints_C_baseline_m_3) mean(Npoints_C_baseline_m_3)],'Color',rgb('Gray'),'LineStyle','--','LineWidth',LineWidth_lines);
set(gca,'FontSize',FontSize_small)
title(['Comprehension'],'FontSize',FontSize_titles)
xlabel('ISC','FontSize',FontSize_small)
% ylabel('Score','FontSize',FontSize)
set(gca,'YTick',[])
ylim([0 110])
xlim(xlims)
set(gca,'Box','on')
set(gca,'LineWidth',LineWidth_box)
set(gca,'TickLength',[0 0])
apos = get(gca,'Position');
set(gca,'Position',[apos(1:2)+[x_offset(2) y_offset] bpos(3) bpos(4)-0.03])
apos = get(gca,'Position');
ah = annotation_paper([apos(1)+0.003 apos(2)+apos(4)-0.07 0.06 0.065],r_isc_comprehension,p_isc_comprehension,df_isc_comprehension,FontSize_small-1);
    
%Recognition
subplot(4,8,31);

scatter(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1}, points_experiment_3.Npoints_avgstim_R,marker_scatter_size,'ko','MarkerFaceColor',rgb('Black')); hold on
% [r,p,lh] = line_function_jenma(ISC_eye_xypupil_persubject_avgstim{1},Npoints_avgstim_R,'Black',gca,[0.05 0.45]);
[r_isc_recognition,p_isc_recognition,df_isc_recognition,lh] = line_function_confidence(isc_experiment_3.ISC_eye_xypupil_persubject_avgstim{1},points_experiment_3.Npoints_avgstim_R,0.05,[xlims(1)+0.002 xlims(2)-0.002]);
set(lh,'LineWidth',LineWidth_lines)
l = line(xlims,[mean(Npoints_R_baseline_m_3) mean(Npoints_R_baseline_m_3)],'Color',rgb('Gray'),'LineStyle','--','LineWidth',LineWidth_lines);

set(gca,'FontSize',FontSize_small)
title(['Recognition'],'FontSize',FontSize_titles)
xlabel('ISC','FontSize',FontSize_small)
ylabel('Score','FontSize',FontSize_small)
ylim([0 110])
xlim(xlims)
set(gca,'Box','on')
set(gca,'LineWidth',LineWidth_box)
set(gca,'TickLength',[0 0])
apos = get(gca,'Position');
set(gca,'Position',[apos(1:2)+[x_offset(1) y_offset] bpos(3) bpos(4)-0.03])
apos = get(gca,'Position');
ah = annotation_paper([apos(1)+0.003 apos(2)+apos(4)-0.07 0.06 0.065],r_isc_recognition,p_isc_recognition,df_isc_recognition,FontSize_small-1);

set(fig,'PaperPositionMode','manual')
print([figuredir 'Figure_2.pdf'],'-dpdf','-painters',fig)
