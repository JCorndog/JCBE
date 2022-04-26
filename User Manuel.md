# User Manuel

###### *All files necessary to run are located in `CSFinal/PythonServer`. All paths given will be relative to this directory.

### Create Environment

To create the necessary conda environment run

`conda env create -f env.yml`

This will create a conda environment named `tagAI`.

#### Create New Config File

Make a copy of `config_template.yaml` located in the `config` directory. The values in this file dictate how the model will train.

These values are:

`REPLAY_MEMORY_SIZE`: The number of past states stored
`MIN_REPLAY_MEMORY_SIZE`: The minimum required number of past states stored for training to start
`MODEL_NAME`: name of the model that will be created (changes name of directory where logs and model weights are stored)
`MINIBACH_SIZE`: number of states to use to train each iteration
`DISCOUNT`: discount for future reward
`UPDATE_TARGET_EVERY`: how often to update the target model in number of epochs
`MIN_REWARD`: minimum reward for model weights to be saved
`EPISODES`: number of episodes 
`epsilon`: starting epsilon value
`EPSILON_DECAY`: decay of epsilon each epoch
`MIN_EPSILON`: minimum epoch value
`AGGREGATE_STATS_EVERY`: frequency for aggregating model performance stats
`SAVE_EVERY`: how often to save the models weights
`EPISODE_LENGTH`: how long a episode lasts in seconds

### Begin Training

To begin training first activate the conda environment

`conda activate tagAI`

Then run 

`python model.py --cfg_file configs/{CFG.YML} --port {PORT} --num_sess {NUM_SESS}`

where `{CFG.YML}` is the name of the new config file, `{PORT}` is the port used for communication, and `{NUM_SESS}` is the number of sessions that you are planning to run at the same time. `--num_sess` limits the memory used by the training to prevent out of memory error from the GPU.

