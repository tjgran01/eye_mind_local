% Stim Stuff -----------------

demographics = nirs.createDemographicsTable(raw);

j = nirs.modules.RemoveStimless( );

j = nirs.modules.RenameStims( j );

j.listOfChanges = {'stim_channel1' 'BIGBREAK';
                   'stim_channel2' 'Recal';
                   'stim_channel3' 'Drift-Correct';
                   'stim_channel4' 'Page';
                   'stim_channel5' 'Question';
                   'stim_channel6' 'Question_Deep';
                   'stim_channel7' 'Question_Z';
                   'stim_channel8' 'Sham';
                   'stim_channel9' 'resting_state';
                   'stim_channel10' 'loc_sentences';
                   'stim_channel11' 'loc_words';
                   'stim_channel12' 'loc_jabsent';
                   'stim_channel13' 'loc_jabwords'};

stimsChanged = j.run(raw);

job = nirs.modules.DiscardStims();
job.listOfStims = {'Drift-Correct' 'Recal' 'BIGBREAK'};
stimsChanged = job.run(stimsChanged)


% Pre-processing -----------------

% Resample --- default resample is to 4 hz.
job=nirs.modules.Resample
% job.Fs = 2
rs=job.run(stimsChanged)

% Convert Voltage to Optical Density (Also known as absorbtion)
job=nirs.modules.OpticalDensity
od=job.run(rs)
job.cite

% Convert Optical Density Values to (HbO and HbR)
job=nirs.modules.BeerLambertLaw
hb=job.run(od)
job.cite

% Motion Correction
job=nirs.modules.AddAuxRegressors;
mot_corr=job.run(hb)
job.cite

% % End Pre-processing

% Fitting Data to GLM -------------------
job=nirs.modules.GLM
SubjStats=job.run(hb)
job.cite
