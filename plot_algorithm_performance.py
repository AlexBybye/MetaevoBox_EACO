import pickle
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from matplotlib import colormaps
from typing import List, Dict, Optional, Tuple
import numpy.typing as npt

# 配置参数
BASE_DIR = "output/test/20250603T033056_uav_difficult/metadata"
ALGORITHMS = ['BBO_EACO', 'CMAES', 'DE', 'PSO', 'Random_search', 'SHADE']
TERRAINS = [4, 6, 16, 24, 26, 28, 30, 32, 34, 36, 38, 42, 44, 50]
COLORS = [tuple(color) for color in colormaps['tab20'](np.linspace(0, 1, len(ALGORITHMS)))]
STYLES = ['-', '--', '-.', ':', '-', '--']
MARKERS = ['o', 's', 'D', '^', 'v', 'p']


def load_algorithm_data(algorithm: str, terrain_id: int) -> Optional[List[float]]:
    """加载算法数据并进行清洗"""
    file_path = os.path.join(BASE_DIR, algorithm, f"Terrain {terrain_id}.pkl")

    try:
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 {file_path}")
            return None

        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        # 检查数据是否为字典格式
        if isinstance(data, dict):
            # 提取 'X' 或 'Cost' 键对应的值
            if 'X' in data:
                performance_list = data['X']
            elif 'Cost' in data:
                performance_list = data['Cost']
            else:
                print(f"警告: 数据文件 {file_path} 中没有找到 'X' 或 'Cost' 键")
                return None
        else:
            performance_list = data

        # 如果是numpy数组，转换为列表
        if isinstance(performance_list, np.ndarray):
            performance_list = performance_list.tolist()

        # 如果是嵌套列表，尝试展平
        if isinstance(performance_list, list) and all(isinstance(item, list) for item in performance_list):
            performance_list = [item for sublist in performance_list for item in sublist]

        if not isinstance(performance_list, list):
            print(f"警告: 数据文件 {file_path} 内容不是列表或numpy数组")
            return None

        if not performance_list:
            print(f"警告: 数据文件 {file_path} 内容为空列表")
            return None

        cleaned_data: List[float] = []
        for item in performance_list:
            try:
                # 如果是列表或数组，取第一个元素
                if isinstance(item, (list, np.ndarray)):
                    if len(item) > 0:
                        numeric_value = float(item[0])
                        cleaned_data.append(numeric_value)
                    else:
                        continue
                else:
                    numeric_value = float(item)
                    cleaned_data.append(numeric_value)
            except (ValueError, TypeError, IndexError) as e:
                print(f"警告: 数据文件 {file_path} 包含无法转换的元素: {item}")
                print(f"错误详情: {str(e)}")

        if not cleaned_data:
            print(f"警告: 数据文件 {file_path} 不包含有效的数值数据")
            return None

        return cleaned_data

    except Exception as e:
        print(f"加载 {file_path} 时出错: {str(e)}")
        return None


def plot_algorithm_comparison_per_terrain() -> None:
    """绘制每个地形上的算法性能对比图"""
    plt.figure(figsize=(15, 12))
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14

    axes = []
    max_iterations = 0

    for idx, terrain_id in enumerate(TERRAINS):
        ax = plt.subplot(4, 4, idx + 1)
        axes.append(ax)

        terrain_iterations = []

        for algo_idx, algorithm in enumerate(ALGORITHMS):
            performance = load_algorithm_data(algorithm, terrain_id)
            if performance is None:
                continue

            # 检查 performance 是否是数值列表
            if not all(isinstance(x, (int, float)) for x in performance):
                print(f"警告: 数据文件 Terrain {terrain_id} 的 {algorithm} 数据包含非数值元素")
                continue

            terrain_iterations.append(len(performance))
            iterations = np.arange(len(performance))

            marker = MARKERS[algo_idx] if idx % 5 == 0 else None
            markevery = 5
            markersize = 6

            ax.plot(iterations, performance,
                    color=COLORS[algo_idx],
                    linestyle=STYLES[algo_idx],
                    linewidth=2.0,
                    alpha=0.9,
                    marker=marker,
                    markevery=markevery,
                    markersize=markersize,
                    label=algorithm)

        if terrain_iterations:
            max_terrain_iter = max(terrain_iterations)
            max_iterations = max(max_iterations, max_terrain_iter)
            ax.set_xlim(0, max_terrain_iter)
        else:
            ax.set_xlim(0, max_iterations)

        ax.set_title(f"Terrain {terrain_id}", fontsize=13, pad=8)
        ax.set_xlabel("Iterations", fontsize=10)
        ax.set_ylabel("Performance", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        plt.figlegend(handles, labels, loc='lower center',
                      ncol=3, fontsize=10, framealpha=0.9)
    else:
        print("警告: 没有有效数据用于生成图例")

    plt.tight_layout(rect=[0, 0.05, 1, 0.98])
    plt.suptitle("Algorithm Performance Comparison Across Terrains",
                 fontsize=16, y=0.99)
    plt.savefig("algorithm_comparison_per_terrain.png", bbox_inches='tight', dpi=120)
    plt.close()


def plot_algorithm_average_performance() -> Tuple[
    Dict[str, npt.NDArray[np.float64]], Dict[str, npt.NDArray[np.float64]]]:
    """绘制算法平均性能对比图"""
    plt.figure(figsize=(12, 7))
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'DejaVu Sans'

    algo_performance: Dict[str, npt.NDArray[np.float64]] = {algo: np.array([]) for algo in ALGORITHMS}
    algo_std: Dict[str, npt.NDArray[np.float64]] = {algo: np.array([]) for algo in ALGORITHMS}
    all_perf_data: Dict[str, List[List[float]]] = {algo: [] for algo in ALGORITHMS}

    for terrain_id in TERRAINS:
        for algo_idx, algorithm in enumerate(ALGORITHMS):
            performance = load_algorithm_data(algorithm, terrain_id)
            if performance is not None:
                all_perf_data[algorithm].append(performance)

    max_iter = 0
    for algorithm in ALGORITHMS:
        perf_list = all_perf_data[algorithm]
        if not perf_list:
            continue

        max_len = max(len(perf) for perf in perf_list)
        max_iter = max(max_iter, max_len)

        perf_matrix = np.full((len(perf_list), max_len), np.nan)
        for i, perf in enumerate(perf_list):
            perf_matrix[i, :len(perf)] = np.array(perf)

        avg_perf = np.nanmean(perf_matrix, axis=0)
        std_perf = np.nanstd(perf_matrix, axis=0)

        algo_performance[algorithm] = avg_perf
        algo_std[algorithm] = std_perf

    for algo_idx, algorithm in enumerate(ALGORITHMS):
        if len(algo_performance[algorithm]) == 0:
            continue

        iterations = np.arange(len(algo_performance[algorithm]))
        plt.plot(iterations, algo_performance[algorithm],
                 color=COLORS[algo_idx],
                 linestyle=STYLES[algo_idx],
                 linewidth=2.5,
                 alpha=0.9,
                 label=f"{algorithm}")

        plt.fill_between(iterations,
                         algo_performance[algorithm] - algo_std[algorithm],
                         algo_performance[algorithm] + algo_std[algorithm],
                         color=COLORS[algo_idx],
                         alpha=0.2)

    plt.title("Average Performance of Algorithms Across All Terrains",
              fontsize=16, pad=15)
    plt.xlabel("Iterations", fontsize=12)
    plt.ylabel("Performance Metric", fontsize=12)
    plt.grid(True, alpha=0.4)
    plt.legend(fontsize=10, loc='best', framealpha=0.9)
    plt.tight_layout()
    plt.savefig("algorithm_average_performance.png", bbox_inches='tight', dpi=120)
    plt.close()

    return algo_performance, algo_std


def plot_final_performance_boxplot(algo_performance: Dict[str, npt.NDArray[np.float64]]) -> None:
    """绘制算法最终性能箱线图"""
    plt.figure(figsize=(12, 7))
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'DejaVu Sans'

    final_perf_data: List[List[float]] = []
    algorithm_names: List[str] = []

    min_iterations = 10

    for algorithm in ALGORITHMS:
        final_values: List[float] = []
        for terrain_id in TERRAINS:
            performance = load_algorithm_data(algorithm, terrain_id)
            if performance is not None and len(performance) >= min_iterations:
                n_points = max(1, int(len(performance) * 0.1))
                final_value = float(np.mean(performance[-n_points:]))
                final_values.append(final_value)

        if final_values:
            final_perf_data.append(final_values)
            algorithm_names.append(algorithm)

    if not final_perf_data:
        print("警告: 没有有效数据可绘制最终性能对比")
        return

    plt.boxplot(final_perf_data, labels=algorithm_names, patch_artist=True)

    for i, patch in enumerate(plt.gca().artists):
        if hasattr(patch, 'set_facecolor'):
            patch.set_facecolor(COLORS[i])
            patch.set_alpha(0.7)

    plt.title('Algorithm Final Performance Comparison Across Terrains', fontsize=16)
    plt.ylabel('Performance Metric', fontsize=12)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig("algorithm_final_performance_boxplot.png", bbox_inches='tight', dpi=120)
    plt.close()


if __name__ == "__main__":
    print("开始分析算法性能...")

    print("绘制每个地形上的算法对比图...")
    plot_algorithm_comparison_per_terrain()

    print("绘制算法平均性能图...")
    algo_performance, algo_std = plot_algorithm_average_performance()

    print("绘制算法最终性能箱线图...")
    if algo_performance:
        plot_final_performance_boxplot(algo_performance)

    print("分析完成！结果已保存为PNG文件")