# Learning the statistics of pain: computational and neural mechanisms

Flavia Mancini,Suyi Zhang, Ben Seymour

doi: https://doi.org/10.1101/2021.10.21.465270


## Usage

The code in folder exp_code is used to generate the sequence of stimuli.
The experiment is launched by the matlab function exp_MR_1500ms(sub,sess,stimCurrent,MR_state). See detailed comments inside the exp_MR_1500ms.m file.

For behavioural data analysis, the following directories contain code for specific use. 
* data (behavioural data from fMRI sessions)
* model_fit (fit models to behavioural data)
* model_comparison (performs model comparison)
* model_gen (generate parametric modulators for fMRI analyses using fitted model parameters)

For imaging analysis, 
* imaging (1st and 2nd level analysis scripts based on nipype)
* imaging_plot (result visualisation using nilearn)

Please change data paths and parameter settings within the scripts. The analysis code is written by Suyi Zhang and can also be found on [her GitHub page](https://github.com/syzhang/tsl_paper).


The raw MRI data are available on [OpenNeuro](https://openneuro.org/datasets/ds003836).

## Requirements

To run the code for sequence generation, you will need:
* MATLAB
* [Psychotoolbox 3](http://psychtoolbox.org)
* a DAQ
* a stimulus generator

To run the code for behavioural analyses, you will need the following:
* MATLAB
* [Minimal Transition Probs Model package](https://github.com/florentmeyniel/MinimalTransitionProbsModel)
* [VBA toolbox](https://mbb-team.github.io/VBA-toolbox/)

For imaging analyses, the required python packages are listed in `requirements.txt`. Nipype scripts are best run inside its docker/singularity container, a useful tutorial can be found [here](https://miykael.github.io/nipype_tutorial/).


