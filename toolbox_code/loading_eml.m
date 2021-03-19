raw = nirs.io.loadDirectory('../data/test_long_stim', {'Subject'}, {@nirs.io.loadNIRx})

% STIM ORDER

% 1 - 1 - "BIGBREAK"
% 2 - 2 - "Recal"
% 3 - 3 - "Drift Correct"
% 7 - 4 - "Page"
% 12 - 5 - "Question"
% 13 - 6 - "Question-Deep"
% 14 - 7 - "Question-Z"
% 20 - 8 - "Sham"
% 25 - 9 - "resting-state"
% 51 - 10 - "sentences"
% 52 - 11 - "words"
% 53 - 12 - "jabsent"
% 54 - 13 - "jabwords"

demographics = nirs.createDemographicsTable(raw);

j = nirs.modules.RemoveStimless( );

j = nirs.modules.RenameStims( j );

j.listOfChanges = {'stim_channel1' 'BIGBREAK';
                   'stim_channel2' 'Recal';
                   'stim_channel3' 'Drift Correct';
                   'stim_channel4' 'Page';
                   'stim_channel5' 'Question';
                   'stim_channel6' 'Question-Deep';
                   'stim_channel7' 'Question-Z';
                   'stim_channel8' 'Sham';
                   'stim_channel9' 'resting-state';
                   'stim_channel10' 'loc-sentences';
                   'stim_channel11' 'loc-words';
                   'stim_channel12' 'loc-jabsent';
                   'stim_channel13' 'loc-jabwords'};

stimsChanged = j.run(raw);