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
    'test_problem': 'uav',
    'test_difficulty': 'difficult',  # 测试难度
    'user_test_problem_list': None,  # 不使用自定义问题列表
    'device': 'cpu',  # 使用CPU设备
    'full_meta_data':True,
    # 测试模式配置
    'test_batch_size': 4,  # 测试批次大小
    'test_parallel_mode': 'Serial',  # 使用串行模式
    'test_run': 20,  # 标准测试运行次数
    'rollout_run': 10,  # rollout运行次数

    # 基准算法配置
    'baselines': {
        'BBO_EACO': {
            'optimizer': BBO_EACO,
            'params': {}
        },
        'DE': {
            'optimizer': DE,
            'params': {'F': 0.6, 'CR': 0.9}  # 增加F值以增强局部搜索
        },
        'PSO': {
            'optimizer': PSO,
            'params': {'w': 0.7, 'c1': 1.5, 'c2': 1.5}  # 略微调整以平衡局部和全局搜索
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