# CogniVal
This tool is based on the framework described in the following paper:  
Nora Hollenstein, Antonio de la Torre, Ce Zhang & Nicolas Langer. "CogniVal: A Framework for Cognitive Word Embedding Evaluation". _CoNLL_ 
(2019).

## Requirements
- Python 3.7.4 or newer
- For PDF generation of reports: wkhtmltopdf version 0.12.5 or newer (available from https://wkhtmltopdf.org/)
- For manual browsing and viewing of user files: vim (any recent version)
- 16+ GB of RAM recommended
- When using an NVIDIA GPU:
    - CUDA >= 10.1
    - CuDNN >= 7.6.5
    - NVIDIA drivers >= 418.39 (can be determined with nvidia-smi)
    - NVIDIA SMI (for scheduling and monitoring)

## A framework for cognitive word embedding evaluation
The tool generates and fits a neural network regression to predict cognitive data such as fMRI, eye-tracking and EEG (corpora mapping words to cognitive signals) from word embedding inputs.
Thus, it allows determining the predictive power of sets of of word embeddings with respect to cognitive sources. Currently supported modalities are **eye-tracking**, **electroencephalography (EEG)** and **functional magnetic resonance imaging (fMRI)**. Furthermore, the significance of the prediction can be estimated by comparing a set of embeddings with n-fold random embeddings of identical dimensionality and computing statistic significance using the Wilcoxon signed-rank test with conservative Bonferroni correction, counteracting the multiple hypotheses problem.

## Terminology
- Embeddings: Word embeddings in textual format, with a single vector per word. Context-sensitive embedding types like BERT and ELMo thus require preprocessing
- Cognitive source: per-word cognitive signal vectors (e.g. EEG electrodes or eye-tracking statistics)
- Experiment: Combination of a set of embeddings, associated n-fold set of random embeddings and a cognitive source.

In the cases of fMRI and EEG, we want to predict a vector representing the data and not a specific feature.

In case of big word embeddings like word2vec, files are chunked into several pieces to avoid a MemoryError.

## Overview of functionality
The CogniVal interactive shell allows:

- Importing and preprocessing embeddings
- Generating corresponding random embedding sets for significance testing
- Evaluating embeddings against the readily preprocessed CogniVal cognitive sources or any (preprocessed) user-provided cognitive sources
- Setting up regression experiments of cognitive source and embedding pairs (grid search and training parameters)
- Performing regression experiments on CPUs and GPUs in a parallelized fashion
- Computing significance statistics for the results
- Aggregating MSE and significance statistic
- Generating an interactive HTML or static PDF report, showing both aggregate and detail statistics in tabular and plot form,
  as well as plots visualizing the training history and history of key statistics over different experimental runs.

## Overview of commands
`<Tab>` shows all available commands, subcommands and parameters at the given position, as well as argument types and default values where applicable.
By pressing `<Left>`, previously executed commands can be auto-completed. When a command is executed with only one argument, it can be
provided in a positional manner: `command argument`. Otherwise, each parameter must be named: `command parameter1=argument2 parameter2=argument2`.

Note that the syntax is a simplified version of Python's, as strings and ints can be provided without quotes (except for URLs in the context of custom embedding installation), however lists must be enclosed in brackets: `list-param=[value1, value2]`. List parameters require lists even for single values (`list-param=[value]`) and the special value `all`, indicating all possbile values (`list-param=[all]`).

### Basic commands
- clear: Clears the shell
- history: Shows the history of executed commands in descending order. The history is stored in $HOME/.cognival_history
- readme: Shows this README file in less
- welcome: Shows the welcome message in less
- help / ?: Shows a brief overview over all commands
- quit / exit: Terminates the shell session.
- example-calls: Lists example calls for a single or all commands.
- browse: Browses the user directory and view files using vim, per default in read-only mode. (requires that vim is installed).
- update-vocabulary: Scans all installed cognitive sources and updates the vocabulary file.

### Main commands and subcommands
- config
    - open: Opens configuration if it already exists or creates an empty configuration file and, when setting edit=True, the general parameters  of the specified configuration.
            In the editor, default values are provided for most fields (cpu_count corresponds to number of CPU cores - 1) and reset
            automatically for all empty fields upon saving. Configurations can be overwritten with the `overwrite` flag.

      Call: `config open configuration=demo [overwrite=False] [edit=False]`

    - properties: Edit general CogniVal properties (user directory, etc.). This is mainly used to set the directory for user
                  data (embeddings, cognitive sources, configurations and results), in case this data should not reside
                  in $HOME (e.g. due to quota restrictions).

      Call: `config properties`

    - show: Shows details of a configuration, associated cognitive sources and embeddings as well as experiments. The basic view shows
            general configuration properties (editable by `config open`) and lists cognitive sources and embeddings/random embeddings (without informations about how they are paired):
            `config show demo`
            
        Experiment details can either be viewed for a single cognitive source or for the entire configuration (this can be quite verbose!):

        `config show details=True`
        `config show details=True cognitive-source=eeg_zuco`
            
      Call: `config show [details=False] [cognitive-source=None] [hide-random=True]`

    - experiment: Edits one or multiple experiments (arbitrary combinations of cognitive sources and embeddings). Allows to set grid search parameters for activations, batch size, epochs and layers (both number of layers and sizes per layer) as well as the cross-validation folds and validation split during training.
                  
        Call: `config experiment [rand-embeddings=False] [modalities=None] [cognitive-sources=[all]] [embeddings= [all] [single-edit=False] [edit-cog-source-params=False]`
        
        Parameter details:
        
        - rand-embeddings: Whether to include random embeddings in the configuration. Note that this parameter is ignored if the combination(s) have already been associated with random embeddings. In this case, changes to the proper embeddings
        are always propagated to the random embeddings.
        - modalities: Allows to populate or edit combinations of cognitive-sources of an entire modality and corresponding embeddings
        - cognitive-sources: Specifies either single, multiple or all installed cognitive sources (`[all]`) for editing or population.
        - embeddings: Specifies either single, multiple or all installed cognitive sources (`[all]`) for editing or population.
        - single-edit: When editing combinations featuring multiple embeddings, whether to edit the embeddings specifics for all embeddings at once (`False`) or one by one.
        parametrizations are required
        - edit-cog-source-params: Whether to edit parameters of the cognitive source. In general, this is only required when
                                in the case of a multi-feature source, not all features are to be evaluated.

            
    
    - delete: Deletes experiments, cognitive sources (along with experiments) or the entire configuration.
    
      Deleting experiments(s):
      `config delete cognitive-sources=[eeg_zuco] embeddings=[glove.6B.50]`

      Deleting cognitive sources:
      `config delete cognitive-sources=[eeg_zuco]`
      `config delete modalities=[eeg_zuco]`

      Deleting configurations:
      `config delete demo`

      Call: `config delete [modalities=None] [cognitive-sources=None] [embeddings=None]`

- install
    - cognitive-sources: Install the entire batch of preprocessed CogniVal cognitive sources or a custom cognitive source.
                         Custom sources must be manually placed in the path indicated by the assistant.
                         
        CogniVal sources: `install cognitive-sources`
        Custom source: `install cognitive-sources source=yoursource`
    
    - embeddings: Install and preprocess default embeddings (see CogniVal paper) as well as custom embeddings (word2vec compliant text/binary or BERT compliant). Allows to directly associate random embeddings with the embeddings.

      Default embeddings: `install embeddings glove.6B.50`
      Custom embeddings: `install embeddings http://example.org/example.zip`
    
    - random embeddings: Associate or re-associate (`force` parameter) embeddings with a set of random embeddings. Random embeddings of a set are generated with different seeds and results are averaged during evaluation to increase robustness of significance testing.

                         The parameter `no-embeddings` specifies the number of "folds" to generate (default: 10). Generation is parallelized greedily across available CPU cores - 1.
      
      Call: `install random-embeddings embeddings=glove.6B.50 [no-embeddings=10] [seed-func=exp_e_floored] [force=False]`
    
-  list
    - configs: List available configurations. Note that the reference configuration cannot be edited as it is used to populate newly
               created configurations with default values.
    - embeddings: List available and installed default embeddings as well as installed custom embeddings and generated random embeddings.
    - cognitive-sources: Lists installed cognitive sources along with their features (where applicable).
    
- run: Run all or a subset of experiments specified in a configuration. The parameters `embeddings`, `modalities` and `cognitive-sources` correspond to `config experiment`. Note that `cognitive-features` is a nested list that must specify features
for all cognitive-sources. Each inner list must be specified as semicolon-separated string within quotes.
    Call: `run [embeddings=[all]] [modalities=None] [cognitive-sources=[all]] [cognitive-features=None]`

- significance:  Compute the significance of results of an experimental run. Note that this requires that random embeddings have been
                 associated and evaluated during the run. Evaluates the results of the last run by default. Results are printed to the
                 shell and stored in the reports directory of the results path.

    Call: `significance [version=0] [modalities=[eye-tracking, eeg, fmri]] [alpha=0.01 test=Wilcoxon]`

    Parameters:
    - version: Either 0 for the last experimental run or any version before the current version of the configuration.
    - modalities: Modalities for which significane is to be termined
    - alpha: Alpha for significance computation
    - test: Significance test. Currently, only the Wilcoxon rank-sum test is implemented (implementation of the Wilcoxon test for NLP provided by [Dror et al. (2018)](https://github.com/rtmdrr/testSignificanceNLP)).

- aggregate: Aggregate the significance test results of an ecxperimental run. This will output how many of your hypotheses are accepted under the Bonferroni correction (see paper for detailed description).
     
     Call: `aggregate [version=0] [modalities=[eye-tracking, eeg, fmri]] [test=Wilcoxon]`
     
     Parameters:
    - version: Either 0 for the last experimental run or any version before the current version of the configuration.
    - modalities: Modalities for which significane is to be termined
    - test: Significance test. Currently, only the Wilcoxon rank-sum test is implemented

- report: Perform significance testing and result aggregation, and generate a HTML or PDF report tabulating and plotting statistics.
     
     Call: `significance [version=0] [modalities=[eye-tracking, eeg, fmri]] [alpha=0.01] [test=Wilcoxon] [html=True] [open-html=False] [pdf=False] [open-pdf=False]`

     Parameters:
    - version: Either 0 for the last experimental run or any version before the current version of the configuration.
    - modalities: Modalities for which significane is to be termined
    - alpha: Alpha for significance computation
    - test: Significance test. Currently, only the Wilcoxon rank-sum test is implemented
    - html: Whether to generate a HTML report (stored in the reports directory of the results path)
    - open-html: Whether to open the HTML report with the default browser. Note: In case of remote access, this requires a server-side installation of a browser and X11 forwarding.
    - pdf: Whether to generate a PDF version of the HTML report (stored in the reports directory of the results path)
    - open-pdf: Whether to open the PDF report with the default document viewer. Note: In case of remote access, this requires a server-side installation of a document viewer and X11 forwarding.

## Custom embedding installation
Custom embeddings can be directly downloaded from a specified URL and extracted from an archive (if applicable).
The assistant is started by executing `install embeddings "<some URL or local path>"`.

The following criteria must be met:

- The passed value is either a local path or an URL representing a direct HTTP(S) link to the file or a Google Drive link.
- The file is either a ZIP archive, gzipped file or usable as-is.

Other modes of hosting and archival are currently NOT supported and will cause the installation to fail.                        
In those instances, please manually download, extract and preprocess the files in the "embeddings" directory.
The last dialog box of the assistant will prompt the user regarding manual installation (defaulting to "No").

First, a name must be specified for addressing the embeddings in subsequent commands. Next, the name of the main embeddings file must be specified. Optionally, the name of the embeddings path can be customized. Following, the user is prompted with respect to the embeddings dimensionality, whether the embeddings are binary or textual. In the binary case, conversion from word2vec- and BERT-compliant formats can be performed (Note: BERT conversion requires at least 16GB of RAM). Embeddings can also be chunked to avoid memory errors, with the number of chunks being parametrizable.

## Custom cognitive source installation
Custom cognitive sources can be installed in a semi-automatic manner, in that the associated file must be placed manually in the corresponding path (shown by the assistant). 

Call: `install cognitive-sources source=<name of the source>`

Custom cognitive sources MUST conform to the CogniVal format (space-separated, columns word, feature or dimension columns (named e[i], see below)) and be put manually in the corresponding directory (`.cognival/<cognitive_sources/<modality>/`) after running this assistant. The specified name must match the corresponding text file! Multi-hypothesis (multi-file) sources must currently be added manually.

The assistant prompts the user to specify the cognitive source modality (either EEG, Eye-Tracking or fMRI). It will the then specify in which path to place the file and how to name it. Subsequently, the dimensionality of the source has to be specified, if it is not subdivided into features (Note: Multi-dimensional multi-feature sources are not supported). If the source has multiple features, the column names must be given, separated by comma.

## Input data format
The input format for the embeddings is raw text, for example:

`island 1.4738 0.097269 -0.87687 0.95299 -0.17249 0.10427 -1.1632 ...`

Embeddings in binary formats must be converted. Supported formats are word2vec- and BERT-compliant.

The input format for the cognitive data source is also raw text, and all feature values are scale between 0 and 1.

EEG example:

``word e1 e2 e3 e4 e5 ...``  
``his 0.5394774791900334 0.4356708610374691 0.523294558226597 0.5059544824545096 0.466957449316214 ...``

fMRI example:

``word v0 v1 v2 v3 ...``  
``beginning 0.3585450775710978 0.43270347838578155 0.7947947579149615 ...``

Eye-tracking example:

``word WORD_FIXATION_COUNT WORD_GAZE_DURATION WORD_FIRST_FIXATION_DURATION ...``  
``the 0.1168531943034873 0.11272377054039184 0.25456297601240524 ...`` 

All cognitive data sources are freely available for you to download and preprocess. 

The fully preprocessed vectors as described in the publication can however be downloaded from the tool, as well as [here](https://drive.google.com/uc?id=1ouonaByYn2cnDAWihnQ3cGmMT6bJ4NaP).