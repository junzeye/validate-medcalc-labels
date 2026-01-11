# Hardware requirement:
# 8 H100 GPUs (80GB each). Each training run takes about 9 hours (1 hr per epoch).
# Conda environment: make sure you have installed and activated the conda environment for Verl (0.4.0)
# with vLLM inference backend.

# Run the RL (GRPO) experiment using new labels we recomputed for MedCalc-Bench's training set.
# The final test accuracy is reported on MedCalc-Bench's test set, but with the recomputed labels
# we obtained, which show much higher agreement with physician-computed gold standard labels.
# These labels shape the RL reward function's behavior.
LR=1e-5
KL_COEF=0.001
echo "LR: $LR, KL_COEF: $KL_COEF"
# Clean up any existing Ray instances before starting
ray stop --force 2>/dev/null || true
unset RAY_ADDRESS
python -u -m verl.trainer.main_ppo \
      --config-path config_medcalc \
      --config-name ppo_trainer \
      exp=qwen3_8b_grpo \
      trainer.experiment_name=new_train_labels_lr${LR}_kl${KL_COEF}_$(date +%m%d_%H%M) \
      trainer.total_epochs=9 \
      actor_rollout_ref.actor.optim.lr=${LR} \
      actor_rollout_ref.actor.kl_loss_coef=${KL_COEF}

sleep 10

# Run the RL (GRPO) experiment using the original labels of MedCalc-Bench's training set.
# You could relocate the following code to another bash script and run it separately.
LR=1e-5
KL_COEF=0.001
echo "LR: $LR, KL_COEF: $KL_COEF"
# Clean up any existing Ray instances before starting
ray stop --force 2>/dev/null || true
unset RAY_ADDRESS
python -u -m verl.trainer.main_ppo \
      --config-path config_medcalc \
      --config-name ppo_trainer \
      exp=qwen3_8b_grpo \
      trainer.experiment_name=original_train_labels_lr${LR}_kl${KL_COEF}_$(date +%m%d_%H%M) \
      trainer.total_epochs=9 \
      actor_rollout_ref.actor.optim.lr=${LR} \
      actor_rollout_ref.actor.kl_loss_coef=${KL_COEF} \
      data.train_files=/PATH/TO/PROJECT/ROOT/data/RL/train_old_labels.parquet
      # The default train_file (specified by the config file verl/trainer/config_medcalc/exp/qwen3_8b_grpo.yaml) 
      # contains the new training labels, so we override the path with the one to the original training labels.