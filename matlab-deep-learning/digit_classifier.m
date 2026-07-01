% Digit classification with a small CNN, using MATLAB's built-in sample
% digit dataset (10,000 synthetic 28x28 images, 0-9) - no download needed,
% it ships with Deep Learning Toolbox. Uses the current trainnet/testnet
% API (trainNetwork is deprecated as of R2024a).

digitDatasetPath = fullfile(matlabroot, "toolbox", "nnet", "nndemos", ...
    "nndatasets", "DigitDataset");
imds = imageDatastore(digitDatasetPath, ...
    IncludeSubfolders=true, ...
    LabelSource="foldernames");

numTrainFiles = 750; % per class, out of 1000 - the rest is held out for testing
[imdsTrain, imdsTest] = splitEachLabel(imds, numTrainFiles, "randomized");

inputSize = [28 28 1];
classNames = categories(imds.Labels);
numClasses = numel(classNames);

layers = [
    imageInputLayer(inputSize)
    convolution2dLayer(5, 20)
    batchNormalizationLayer
    reluLayer
    fullyConnectedLayer(numClasses)
    softmaxLayer];

options = trainingOptions("sgdm", ...
    MaxEpochs=4, ...
    Verbose=true, ...
    Metrics="accuracy");

net = trainnet(imdsTrain, layers, "crossentropy", options);

accuracy = testnet(net, imdsTest, "accuracy");
fprintf("Held-out test accuracy: %.1f%%\n", accuracy);

% Next steps:
% - Swap in a deeper network (more conv/pool blocks) and compare accuracy.
% - Try classifying your own images: load them with imageDatastore pointed
%   at a folder under /work (persistent), instead of the bundled dataset.
% - Use gpuDeviceCount / ExecutionEnvironment="gpu" in trainingOptions to
%   confirm training is actually using the workspace's GPU.
