#!/usr/bin/env python3

import numpy as np
import rospkg
# ROS packages required
import rospy
from openai_ros.openai_ros_common import StartOpenAI_ROS_Environment
from stable_baselines3 import PPO


def main():
    env, modelPath = init()

    rospy.logwarn("Loading Model...")
    model = PPO.load(modelPath)
        
    rospy.logwarn("Start prediction...")
    evaluate(model, env, False)


def evaluate(model, env, inited, num_episodes=10):
    """
    Evaluate a RL agent
    :param model: (BaseRLModel object) the RL Agent
    :param num_episodes: (int) number of episodes to evaluate it
    :return: (float) Mean reward for the last num_episodes
    """
    all_episode_rewards = []
    
    for i in range(num_episodes):
        episode_rewards = []

        #Hack needed to enable evaluation post training :/
        if inited:
            obs,info = env.getObs()
            inited = False
            rospy.logwarn(str(obs))
        else:
            obs,info = env.reset()
            
            
        done = False
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done,_, info = env.step(action)
            episode_rewards.append(reward)

        all_episode_rewards.append(sum(episode_rewards))

    mean_episode_reward = np.mean(all_episode_rewards)
    rospy.logwarn("Mean reward: " + str(mean_episode_reward) + " Num episodes: " + str(num_episodes))

    return mean_episode_reward

def init():
    rospy.init_node('example_turtlebot3_maze_qlearn',
                    anonymous=True, log_level=rospy.WARN)
    task_and_robot_environment_name = rospy.get_param(
        '/turtlebot3/task_and_robot_environment_name')
    env = StartOpenAI_ROS_Environment(
        task_and_robot_environment_name)

    rospack = rospkg.RosPack()
    pkg_path = rospack.get_path('drl_agent')
    outdir = pkg_path + '/training_results'
    modelPath = outdir + "/PPO_laser_rl_model_260000_steps"
    return env, modelPath

if __name__ == '__main__':
    main()
