import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import ray
# Create a shorter temp directory for Ray
ray_temp_dir = os.path.join(tempfile.gettempdir(), 'ray_tmp')
os.makedirs(ray_temp_dir, exist_ok=True)
# Initialize Ray with limited resources
ray.init(_temp_dir=ray_temp_dir, num_cpus=4)  # Reduced to 4 CPUs

from metaevobox import Config, Tester, get_baseline
from src.baseline.bbo.bbo_eaco import BBO_EACO
from metaevobox.baseline.bbo import CMAES, DE, PSO, SHADE
from metaevobox.environment.problem.utils import construct_problem_set

# 配置测试参数
config = {
    # 问题集配置
    'test_problem': 'bbob-10D',  # BBOB标准测试集（10维）
    'test_difficulty': 'difficult',  # 测试难度
    'user_test_problem_list': None,  # 不使用自定义问题列表
    'device': 'cpu',  # 使用CPU设备
    'full_meta_data':True,
    # 测试模式配置
    'test_batch_size': 4,  # 测试批次大小
    'test_parallel_mode': 'Serial',  # 使用串行模式
    'test_run': 51,  # 标准测试运行次数
    'rollout_run': 10,  # rollout运行次数

    # 基准算法配置
    'baselines': {
        'BBO_EACO': {
            'optimizer': BBO_EACO,
            'params': {
                'pop_size': 100,  # 增加种群大小以保持多样性
                'alpha': 0.2,     # 降低交叉参数使交叉更保守
                'rho': 0.2,       # 增加信息素蒸发率以加快更新
                'Q': 100,         # 增加信息素增量以增强影响
                'p_mutate': 0.3,  # 降低变异概率以减少随机性
                'mu_max': 0.8,    # 调整迁入率使迁移更平衡
                'lambda_max': 0.8,# 调整迁出率使迁移更平衡
                'elite_size': 8   # 增加精英解数量以保留更多好的解
            }
        },
        'DE': {
            'optimizer': DE,
            'params': {'F': 0.5, 'CR': 0.9}
        },
        'PSO': {
            'optimizer': PSO,
            'params': {'w': 0.729, 'c1': 1.494, 'c2': 1.494}
        },
         # 添加SHADE算法
        'SHADE': {
             'optimizer': SHADE,
             'params': {}  # 使用默认参数
        },
         # 添加CMAES算法
        'CMAES': {
             'optimizer': CMAES,
             'params': {}  # 使用默认参数
        }
    },
}

# 创建配置对象
config = Config(config)

# 加载测试数据集
config, datasets = construct_problem_set(config)

# 初始化所有基准算法
baselines, config = get_baseline(config)

# 初始化测试器
tester = Tester(config, baselines, datasets)

# 执行测试
results = tester.test()

print("测试完成! 结果保存在:", config.output_dir)

# 关闭Ray
ray.shutdown()