import torch
import gym
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, VecFrameStack, SubprocVecEnv
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnNoModelImprovement
from stable_baselines3.common.utils import set_random_seed

from time import time

from tqdm.rich import tqdm
import rich
import pretty_errors
#===========================================================
# create the environment

def make_env(env_id: str, rank: int, seed: int=0):

    def _init():

        env = Monitor(gym.make(env_id))
        env.reset()
        return env
    
    set_random_seed(seed)
    return _init
#---------------------------------------------------------
def train3():
        
    n_env = 4
    env_id = "LunarLander-v2"

    env = SubprocVecEnv([make_env(env_id, i) for i in range(n_env)])
    eval_env = SubprocVecEnv([make_env(env_id, i) for i in range(n_env)])
    # env = gym.make('LunarLander-v2')
    # eval_env = gym.make('LunarLander-v2')
    # eval_env = Monitor(eval_env)

    #---------------------------------------------------------
    stop_train_callback = StopTrainingOnNoModelImprovement(max_no_improvement_evals=11, 
                                                           min_evals=51, verbose=1)
    eval_callback = EvalCallback(eval_env, 
                                callback_after_eval=stop_train_callback, 
                                eval_freq = 250,
                                n_eval_episodes=5, 
                                render=False, verbose=1)
    #---------------------------------------------------------
    # create the model and the training loop
    start_time = time()
    model = PPO('MlpPolicy', env, verbose=0)
    model.learn(total_timesteps=int(1e4), 
                callback=eval_callback,
                progress_bar=True) 

    cpu_time = time() - start_time

    # repeat the experiment using GPU if available
    if torch.cuda.is_available():
        start_time = time()
        # env = DummyVecEnv([lambda: gym.make('LunarLander-v2')])
        # env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=10.)
        # env = VecFrameStack(env, n_stack=4)
        env = SubprocVecEnv([make_env(env_id, i) for i in range(n_env)])
        eval_env = SubprocVecEnv([make_env(env_id, i) for i in range(n_env)])
        model = PPO('MlpPolicy', env, verbose=0)
        model.learn(total_timesteps=int(1e4), 
                    callback=eval_callback,
                    progress_bar=True) 

        gpu_time = time() - start_time
        print(f"Training time with GPU: {gpu_time:.2f} seconds")
    else:
        print("No GPU available to test.")

    # print the results
    print(f"Training time with CPU: {cpu_time:.2f} seconds")


#---------------------------------------------------------
if __name__ == "__main__":
#    start_time = time()
    train3()
#    eval2()
#    end_time = time()
#    print(f"{end_time - start_time:4.2f} s")

#===========================================================