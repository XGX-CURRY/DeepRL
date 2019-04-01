from deep_rl import *


def batch_atari():
    cf = Config()
    cf.add_argument('--i', type=int, default=0)
    cf.add_argument('--j', type=int, default=0)
    cf.merge()

    games = [
        'BreakoutNoFrameskip-v4',
        'AsterixNoFrameskip-v4',
        'MsPacmanNoFrameskip-v4',
        'AlienNoFrameskip-v4',
        # 'DemonAttackNoFrameskip-v4',
        # 'SeaquestNoFrameskip-v4',
    ]
    # game = games[cf.i // 14]

    # algos = [
    #     IOPG_pixel,
    #     # OC_pixel,
    #     # a2c_pixel,
    # ]
    #
    # params = [
    #     [OC_pixel, dict(game=game, remark='OC', beta_reg=0)],
    #     [OC_pixel, dict(game=game, remark='OC', beta_reg=0.01)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='posterior', beta_grad='direct', ent_hat=0.01, beta_reg=0.01)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='expected', beta_grad='direct', ent_hat=0.01, beta_reg=0.01)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='sample', beta_grad='direct', ent_hat=0.01, beta_reg=0.01)],
    #
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='posterior', beta_grad='direct', ent_hat=0.01, beta_reg=0)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='expected', beta_grad='direct', ent_hat=0.01, beta_reg=0)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='sample', beta_grad='direct', ent_hat=0.01, beta_reg=0)],
    #
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='posterior', beta_grad='indirect', ent_hat=0.01)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='expected', beta_grad='indirect', ent_hat=0.01)],
    #
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='posterior', beta_grad='indirect', ent_hat=0)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='expected', beta_grad='indirect', ent_hat=0)],
    #
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='posterior', beta_grad='indirect', ent_hat=0.1)],
    #     [IOPG_pixel, dict(game=game, remark='IOPG', pi_hat_grad='expected', beta_grad='indirect', ent_hat=0.1)],
    #
    # ]

    params = []
    for game in games:
        for r in range(1):
            for pre in [True, False]:
                for grad in ['sample', 'expected', 'posterior']:
                    params.append(
                        [IO_pixel, dict(game=game, run=r, pi_hat_grad=grad, pretrained_phi=pre, control_type='pi')])
                params.append([IO_pixel, dict(game=game, run=r, pretrained_phi=pre, control_type='q')])
            params.append([IO_pixel, dict(game=game, run=r, random_option=True)])

    params = params[cf.i]
    params[0](**params[1])

    exit()


def batch_mujoco():
    cf = Config()
    cf.add_argument('--i', type=int, default=0)
    cf.add_argument('--j', type=int, default=0)
    cf.merge()

    games = [
        'dm-acrobot-swingup',
        'dm-acrobot-swingup_sparse',
        'dm-ball_in_cup-catch',
        'dm-cartpole-swingup',
        'dm-cartpole-swingup_sparse',
        'dm-cartpole-balance',
        'dm-cartpole-balance_sparse',
        'dm-cheetah-run',
        'dm-finger-turn_hard',
        'dm-finger-spin',
        'dm-finger-turn_easy',
        'dm-fish-upright',
        'dm-fish-swim',
        'dm-hopper-stand',
        'dm-hopper-hop',
        'dm-humanoid-stand',
        'dm-humanoid-walk',
        'dm-humanoid-run',
        'dm-manipulator-bring_ball',
        'dm-pendulum-swingup',
        'dm-point_mass-easy',
        'dm-reacher-easy',
        'dm-reacher-hard',
        'dm-swimmer-swimmer15',
        'dm-swimmer-swimmer6',
        'dm-walker-stand',
        'dm-walker-walk',
        'dm-walker-run',
    ]

    # games = ['HalfCheetah-v2', 'Walker2d-v2', 'Swimmer-v2', 'Hopper-v2', 'Reacher-v2']
    # games = ['HalfCheetah-v2', 'Walker2d-v2']
    games = ['dm-walker']

    params = []

    # for game in games:
    #     for r in range(2):
    #         for num_o in [2, 4]:
    #             for learning in ['all', 'alt']:
    #                 for opt_ep in [5, 10]:
    #                     for entropy_weight in [0, 0.01]:
    #                         params.append([a_squared_c_ppo_continuous,
    #                                        dict(game=game, run=r, learning=learning, num_o=num_o, opt_ep=opt_ep,
    #                                            freeze_v=False, entropy_weight=entropy_weight, tasks=True)])
    #         params.append([ppo_continuous, dict(game=game, run=r, tasks=True)])

    for game in games:
        for r in range(30):
            params.append([a_squared_c_ppo_continuous, dict(game=game, run=r, tasks=True, remark='ASC')])
            params.append([ppo_continuous, dict(game=game, run=r, tasks=True, remark='PPO')])


    algo, param = params[cf.i]
    algo(**param)
    # a_squared_c_ppo_continuous(**params[cf.i])
    exit()


def IOPG_feature(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    kwargs.setdefault('pi_hat_grad', 'posterior')
    kwargs.setdefault('beta_grad', 'indirect')
    kwargs.setdefault('ent_hat', 0)
    kwargs.setdefault('beta_reg', 0)
    config = Config()
    config.merge(kwargs)

    config.num_workers = 5
    config.task_fn = lambda: Task(config.game, num_envs=config.num_workers)
    config.eval_env = Task(config.game)
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, 0.001)
    config.network_fn = lambda: InterOptionPGNet(FCBody(config.state_dim), config.action_dim, num_options=2)
    config.discount = 0.99
    config.target_network_update_freq = 200
    config.rollout_length = 5
    config.entropy_weight = 0.01
    config.gradient_clip = 5
    run_steps(InterOptionPGAgent(config))


def IOPG_pixel(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    kwargs.setdefault('pi_hat_grad', 'posterior')
    kwargs.setdefault('beta_grad', 'indirect')
    kwargs.setdefault('ent_hat', 0)
    kwargs.setdefault('beta_reg', 0.01)
    config = Config()
    config.merge(kwargs)

    config.task_fn = lambda: Task(config.game, num_envs=config.num_workers)
    config.eval_env = Task(config.game)
    config.num_workers = 16
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=1e-4, alpha=0.99, eps=1e-5)
    config.network_fn = lambda: InterOptionPGNet(NatureConvBody(), config.action_dim, num_options=4)
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.rollout_length = 5
    config.gradient_clip = 0.5
    config.max_steps = int(2e7)
    config.entropy_weight = 0.01
    run_steps(InterOptionPGAgent(config))


def IO_pixel(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    kwargs.setdefault('pi_hat_grad', 'posterior')
    kwargs.setdefault('ent_hat', 0.01)
    kwargs.setdefault('beta_reg', 0.01)
    kwargs.setdefault('pretrained_phi', True)
    kwargs.setdefault('control_type', 'q')
    kwargs.setdefault('num_options', 4)
    kwargs.setdefault('verify', False)
    kwargs.setdefault('random_option', False)
    config = Config()
    config.merge(kwargs)

    config.saved_option_net = 'data/options/model-OptionCriticAgent-%s-beta_reg_%s-remark_OC-run-0.bin' % \
                              (config.game, config.beta_reg)
    config.task_fn = lambda: Task(config.game, num_envs=config.num_workers)
    config.eval_env = Task(config.game)
    config.num_workers = 16
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=1e-4, alpha=0.99, eps=1e-5)
    config.network_fn = lambda: InterOptionPGNet(NatureConvBody(), config.action_dim, num_options=config.num_options)
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    # config.random_option_prob = LinearSchedule(1.0, 0.05, 1e6)
    config.random_option_prob = LinearSchedule(0.1)
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.rollout_length = 5
    config.gradient_clip = 0.5
    config.max_steps = int(2e7)
    config.entropy_weight = 0.01
    run_steps(InterOptionAgent(config))


def OC_pixel(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    kwargs.setdefault('beta_reg', 0.01)
    kwargs.setdefault('verify', False)
    config = Config()
    config.merge(kwargs)

    config.saved_option_net = 'data/options/model-OptionCriticAgent-%s-beta_reg_%s-remark_OC-run-0.bin' % \
                              (config.game, config.beta_reg)

    config.task_fn = lambda: Task(config.game, num_envs=config.num_workers)
    config.eval_env = Task(config.game)
    config.num_workers = 16
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=1e-4, alpha=0.99, eps=1e-5)
    config.network_fn = lambda: InterOptionPGNet(NatureConvBody(), config.action_dim, num_options=4)
    config.random_option_prob = LinearSchedule(0.1)
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.rollout_length = 5
    config.gradient_clip = 5
    config.max_steps = int(2e7)
    config.entropy_weight = 0.01
    config.save_interval = config.num_workers * int(1e5)
    agent = OptionCriticAgent(config)
    agent.load(config.saved_option_net)
    run_steps(agent)


def a2c_pixel(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    config = Config()
    config.merge(kwargs)

    config.num_workers = 16
    config.task_fn = lambda: Task(config.game, num_envs=config.num_workers)
    config.eval_env = Task(config.game)
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=1e-4, alpha=0.99, eps=1e-5)
    config.network_fn = lambda: CategoricalActorCriticNet(config.state_dim, config.action_dim, NatureConvBody())
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.use_gae = False
    config.entropy_weight = 0.01
    config.rollout_length = 5
    config.gradient_clip = 5
    config.max_steps = int(2e7)
    run_steps(A2CAgent(config))


def a_squared_c_ppo_continuous(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    kwargs.setdefault('num_o', 4)
    kwargs.setdefault('learning', 'all')
    kwargs.setdefault('gate', nn.ReLU())
    kwargs.setdefault('freeze_v', False)
    kwargs.setdefault('opt_ep', 5)
    kwargs.setdefault('entropy_weight', 0.01)
    kwargs.setdefault('tasks', False)
    config = Config()
    config.merge(kwargs)

    if config.tasks:
        if config.game == 'dm-walker':
            tasks = ['stand', 'walk', 'run']
        else:
            raise NotImplementedError
        games = ['%s-%s' % (config.game, t) for t in tasks]
        config.tasks = [Task(g) for g in games]
        config.game = games[0]


    config.task_fn = lambda: Task(config.game)
    config.eval_env = config.task_fn()

    config.network_fn = lambda: OptionGaussianActorCriticNet(
        config.state_dim, config.action_dim,
        num_options=config.num_o,
        actor_body=FCBody(config.state_dim, gate=config.gate),
        critic_body=FCBody(config.state_dim, gate=config.gate),
        option_body_fn=lambda: FCBody(config.state_dim, gate=config.gate),
    )
    config.optimizer_fn = lambda params: torch.optim.Adam(params, 3e-4, eps=1e-5)
    config.discount = 0.99
    config.use_gae = True
    config.gae_tau = 0.95
    config.gradient_clip = 0.5
    config.rollout_length = 2048
    config.optimization_epochs = config.opt_ep
    config.mini_batch_size = 64
    config.ppo_ratio_clip = 0.2
    config.log_interval = 2048
    config.max_steps = 1e6
    config.state_normalizer = MeanStdNormalizer()
    run_steps(ASquaredCPPOAgent(config))


def ppo_continuous(**kwargs):
    generate_tag(kwargs)
    kwargs.setdefault('log_level', 0)
    kwargs.setdefault('gate', nn.ReLU())
    kwargs.setdefault('tasks', False)
    config = Config()
    config.merge(kwargs)

    if config.tasks:
        tasks = ['stand', 'walk', 'run']
        games = ['%s-%s' % (config.game, t) for t in tasks]
        config.tasks = [Task(g) for g in games]
        config.game = games[0]

    config.task_fn = lambda: Task(config.game)
    config.eval_env = config.task_fn()

    config.network_fn = lambda: GaussianActorCriticNet(
        config.state_dim, config.action_dim,
        actor_body=FCBody(config.state_dim, gate=config.gate),
        critic_body=FCBody(config.state_dim, gate=config.gate))
    config.optimizer_fn = lambda params: torch.optim.Adam(params, 3e-4, eps=1e-5)
    config.discount = 0.99
    config.use_gae = True
    config.gae_tau = 0.95
    config.gradient_clip = 0.5
    config.rollout_length = 2048
    config.optimization_epochs = 10
    config.mini_batch_size = 64
    config.ppo_ratio_clip = 0.2
    config.log_interval = 2048
    config.max_steps = 1e6
    config.state_normalizer = MeanStdNormalizer()
    run_steps(PPOAgent(config))


if __name__ == '__main__':
    mkdir('log')
    mkdir('data')
    random_seed()
    set_one_thread()

    # select_device(0)
    # batch_atari()

    select_device(-1)
    batch_mujoco()

    # game = 'HalfCheetah-v2'
    # game = 'Walker2d-v2'
    # game = 'Swimmer-v2'
    game = 'dm-walker-walk'
    # ppo_continuous(
    #     # game=game,
    #     game='dm-walker',
    #     tasks=['stand', 'walk', 'run'],
    #     log_level=1,
    #     gate=nn.ReLU(),
    # )

    a_squared_c_ppo_continuous(
        game=game,
        learning='all',
        log_level=1,
        num_o=4,
        opt_ep=10,
        freeze_v=False,
        tasks=False,
        gate=nn.ReLU(),
    )

    # game = 'AlienNoFrameskip-v4'
    # # OC_pixel(
    # #     game=game,
    # #     verify=True,
    # # )
    # IO_pixel(
    #     game=game,
    #     pi_hat_grad='posterior',
    #     verify=False,
    #     random_option=False,
    #     control_type='pi',
    #     pretrained_phi=True,
    # )
    #
    # from examples import *

    # a2c_feature(game='LunarLander-v2')
    # option_critic_feature(game='CartPole-v0')
    # IOPG_feature(
    #     # game='CartPole-v0',
    #     game='LunarLander-v2',
    #     # game='Acrobot-v1',
    #     # pi_hat_grad='sample',
    #     # pi_hat_grad='expected',
    #     pi_hat_grad='posterior',
    #     beta_grad='direct',
    #     # beta_grad='indirect',
    #     ent_hat=0.1,
    #     beta_reg=0.01,
    # )