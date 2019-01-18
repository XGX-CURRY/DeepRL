#######################################################################
# Copyright (C) 2017 Shangtong Zhang(zhangshangtong.cpp@gmail.com)    #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################

from ..network import *
from ..component import *
from .BaseAgent import *
import torchvision

class ModelDDPGAgent(BaseAgent):
    def __init__(self, config):
        BaseAgent.__init__(self, config)
        self.config = config
        self.task = config.task_fn()
        self.network = config.network_fn()
        self.target_network = config.network_fn()
        self.target_network.load_state_dict(self.network.state_dict())
        self.replay = config.replay_fn()
        self.random_process = config.random_process_fn()
        self.total_steps = 0
        self.state = None
        self.episode_reward = 0
        self.episode_rewards = []

        self.models = [config.model_fn() for _ in range(config.num_models)]
        self.model_opts = [config.model_opt_fn(m.parameters()) for m in self.models]
        self.model_replays = [config.model_replay_fn() for _ in self.models]

    def soft_update(self, target, src):
        for target_param, param in zip(target.parameters(), src.parameters()):
            target_param.detach_()
            target_param.copy_(target_param * (1.0 - self.config.target_network_mix) +
                                    param * self.config.target_network_mix)

    def eval_step(self, state):
        self.config.state_normalizer.set_read_only()
        state = self.config.state_normalizer(state)
        action = self.network(state)
        self.config.state_normalizer.unset_read_only()
        return to_np(action)

    def train_model(self, model_index):
        config = self.config
        model = self.models[model_index]
        model_opt = self.model_opts[model_index]
        model_replay = self.model_replays[model_index]
        for i in range(config.model_opt_epochs):
            s, a, r, next_s, _ = model_replay.sample()
            s = tensor(s)
            a = tensor(a)
            r = tensor(r).unsqueeze(1)
            next_s = tensor(next_s)

            p_loss, r_loss = model.loss(s, a, r, next_s)
            config.logger.add_scalar('model_%d_tran_loss' % (model_index), p_loss.mean())
            config.logger.add_scalar('model_%d_r_loss' % (model_index), r_loss.mean())

            loss = p_loss.sum(-1).mean() + r_loss.sum(-1).mean()

            model_opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            model_opt.step()

    def real_transitions(self, transitions):
        states, actions, rewards, next_states, mask = transitions
        config = self.config
        phi_next = self.target_network.feature(next_states)
        a_next = self.target_network.actor(phi_next)
        q_next = self.target_network.critic(phi_next, a_next)
        q_next = rewards + config.discount * mask * q_next
        q_next = q_next.detach()
        phi = self.network.feature(states)
        q = self.network.critic(phi, actions)
        critic_loss = (q - q_next).pow(2).mul(0.5).mean()
        config.logger.add_scalar('q_loss_replay', critic_loss)

        self.network.zero_grad()
        critic_loss.backward()
        self.network.critic_opt.step()

        phi = self.network.feature(states)
        action = self.network.actor(phi)
        policy_loss = -self.network.critic(phi.detach(), action).mean()
        config.logger.add_scalar('pi_loss_replay', policy_loss)

        self.network.zero_grad()
        policy_loss.backward()
        self.network.actor_opt.step()

    def imaginary_transitions(self, states, actions):
        config = self.config
        with torch.no_grad():
            rewards, next_states = self.model_predict(states, actions)
            a_next = self.target_network.actor(next_states)
            q_next = self.target_network.critic(next_states, a_next)
            target = rewards + config.discount * q_next.squeeze(-1)
            uncertainty = target.std(-1).unsqueeze(-1)
            t_mask = (uncertainty < config.max_uncertainty).float()
            config.logger.add_histogram('uncertainty_dist', uncertainty)
            config.logger.add_scalar('uncertainty_max', uncertainty.max())
            config.logger.add_scalar('uncertainty_mean', uncertainty.mean())
            config.logger.add_scalar('uncertainty_ratio', t_mask.mean())

        q = self.network.critic(states, actions.detach())
        critic_loss = (q - target).mul(t_mask).pow(2).mul(0.5).sum() / t_mask.sum().add(1e-5)
        config.logger.add_scalar('q_loss_plan', critic_loss)

        self.network.zero_grad()
        critic_loss.backward()
        self.network.critic_opt.step()

        # policy_loss = -self.network.critic(states, actions).mul(t_mask).sum() / t_mask.sum().add(1e-5)
        # config.logger.add_scalar('pi_loss_plan', policy_loss)
        #
        # self.network.zero_grad()
        # policy_loss.backward()
        # self.network.actor_opt.step()

    def model_predict(self, s, a):
        rewards = []
        next_states = []
        for m in self.models:
            r, next_s = m(s, a)
            rewards.append(r)
            next_states.append(next_s)
        r = torch.cat(rewards, dim=-1)
        next_s = torch.cat(next_states, dim=1)
        return r, next_s

    def step(self):
        config = self.config
        if self.state is None:
            self.random_process.reset_states()
            self.state = self.task.reset()
            self.state = config.state_normalizer(self.state)
        if self.total_steps < config.agent_warm_up:
            action = [self.task.action_space.sample()]
        else:
            action = self.network(self.state)
            action = to_np(action)
            action += self.random_process.sample()
        action = np.clip(action, self.task.action_space.low, self.task.action_space.high)
        next_state, reward, done, _ = self.task.step(action)
        next_state = self.config.state_normalizer(next_state)
        self.episode_reward += reward[0]
        reward = self.config.reward_normalizer(reward)

        batch_data = list(zip(self.state, action, reward, next_state, 1 - done))
        self.replay.feed_batch(batch_data)
        for m_replay in self.model_replays:
            m_replay.feed_batch(batch_data)

        if done[0]:
            config.logger.add_scalar('train_episode_return', self.episode_reward)
            self.episode_rewards.append(self.episode_reward)
            self.episode_reward = 0
            self.random_process.reset_states()

        self.state = next_state
        self.total_steps += 1

        if self.total_steps >= config.model_warm_up and config.plan:
            for i in range(config.num_models):
                self.train_model(i)

        if self.replay.size() >= config.agent_warm_up:
            experiences = self.replay.sample()
            states, actions, rewards, next_states, mask = experiences
            states = tensor(states)
            actions = tensor(actions)
            rewards = tensor(rewards).unsqueeze(1)
            next_states = tensor(next_states)
            mask = tensor(mask).unsqueeze(1)
            self.real_transitions([states, actions, rewards, next_states, mask])

            if config.plan:
                actions = actions + torch.randn(actions.size(), device=Config.DEVICE).mul(0.1)
                self.imaginary_transitions(states, actions)

            self.soft_update(self.target_network, self.network)