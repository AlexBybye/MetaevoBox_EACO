import numpy as np
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt
# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Droid Sans Fallback']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号


# 加载所有算法的元数据
def load_metadata(algorithm):
    load_path = f"output/test/20250602T162758_bbob-10D_difficult/metadata/{algorithm}/"
    problem_list = [f.split('.')[0] for f in os.listdir(load_path) if f.endswith('.pkl')]

    metadata = {}
    for problem in problem_list:
        with open(os.path.join(load_path, f"{problem}.pkl"), 'rb') as f:
            data = pickle.load(f)
        metadata[problem] = data

    return metadata, problem_list


# 绘制单次运行优化曲线
def plot_optimization_curve_for_single_run(problem, algorithm, run_index=0, max_generations=200):
    metadata, _ = load_metadata(algorithm)

    if problem not in metadata:
        print(f"Problem {problem} not found in {algorithm} metadata.")
        return

    data = metadata[problem]
    if run_index >= len(data):
        print(f"Run index {run_index} out of range for problem {problem} in algorithm {algorithm}.")
        return

    all_Y = data[run_index]['Cost']
    all_Y = all_Y[:max_generations]  # 限制最大代数

    current_min = all_Y[0].min()
    min_tracking = [current_min]

    for gen in all_Y[1:]:
        current_min = min(current_min, gen.min())
        min_tracking.append(current_min)

    plt.figure(figsize=(10, 6))
    plt.plot(min_tracking, label=f'{algorithm} - {problem}')
    plt.xlabel('代数')
    plt.ylabel('最小成本')
    plt.title(f'{algorithm} - {problem} 的优化进度')
    plt.legend()
    plt.grid()
    plt.show()


# 绘制归一化跨问题曲线
def plot_normalized_across_problems(algorithm, max_generations=200):
    metadata, problem_list = load_metadata(algorithm)

    draw_data = []
    for problem in problem_list:
        data = metadata[problem]
        for run in data:
            all_Y = run['Cost'][:max_generations]  # 限制最大代数
            min_Y_0 = all_Y[0].min()
            min_tracking = [min_Y_0]

            current_min = min_Y_0
            for gen in all_Y[1:]:
                current_min = min(current_min, gen.min())
                min_tracking.append(current_min)

            # 归一化到 [0-1] 范围
            normalized = (np.array(min_tracking) - min_Y_0) / (min_Y_0 - 1e-8)
            draw_data.append(normalized)

    draw_data = np.array(draw_data)

    plt.figure(figsize=(12, 6))
    mean_curve = draw_data.mean(axis=0)
    std_curve = draw_data.std(axis=0)

    plt.plot(mean_curve, label=f'{algorithm} - 平均归一化进度')
    plt.fill_between(range(len(mean_curve)),
                     mean_curve - std_curve,
                     mean_curve + std_curve,
                     alpha=0.3, label='标准差范围')

    plt.xlabel('代数')
    plt.ylabel('归一化性能')
    plt.title(f'{algorithm} 的归一化优化进度')
    plt.legend()
    plt.grid()
    plt.show()


# 生成性能比较表格
def generate_performance_table():
    algorithms = ["BBO_EACO", "CMAES", "DE", "PSO", "Random_search", "SHADE"]
    results = []

    for algorithm in algorithms:
        metadata, problem_list = load_metadata(algorithm)

        for problem in problem_list:
            data = metadata[problem]
            final_min = min(run['Cost'][-1].min() for run in data)
            results.append({
                '算法': algorithm,
                '问题': problem,
                '最终最小值': final_min
            })

    df = pd.DataFrame(results)
    df_pivot = df.pivot_table(index='问题', columns='算法', values='最终最小值')

    # 保存到Excel
    save_path = "output/test/20250602T162758_bbob-10D_difficult/"
    os.makedirs(save_path, exist_ok=True)
    df_pivot.to_excel(os.path.join(save_path, 'performance_comparison.xlsx'))

    return df_pivot


# 反NFL性能比较分析
def anti_nfl_analysis():
    algorithms = ["BBO_EACO", "CMAES", "DE", "PSO", "Random_search", "SHADE"]
    problem_list = [
        "Attractive_Sector", "Bent_Cigar", "Buche_Rastrigin",
        "Composite_Grie_rosen", "Different_Powers", "Discus",
        "Ellipsoidal_high_cond", "Gallagher_21Peaks", "Katsuura",
        "Lunacek_bi_Rastrigin", "Rosenbrock_original", "Rosenbrock_rotated",
        "Schaffers_high_cond", "Schwefel", "Sharp_Ridge", "Step_Ellipsoidal"
    ]

    results = []

    for algorithm in algorithms:
        metadata, _ = load_metadata(algorithm)

        for problem in problem_list:
            if problem not in metadata:
                print(f"No data found for {algorithm} - {problem}")
                continue

            data = metadata[problem]
            final_min = min(run['Cost'][-1].min() for run in data)
            results.append({
                '算法': algorithm,
                '问题': problem,
                '最终最小值': final_min
            })

    df = pd.DataFrame(results)

    # 计算每个问题的排名
    df['排名'] = df.groupby('问题')['最终最小值'].rank()

    # 保存到Excel
    save_path = "output/test/20250602T162758_bbob-10D_difficult/"
    os.makedirs(save_path, exist_ok=True)
    df.to_excel(os.path.join(save_path, 'anti_nfl_analysis.xlsx'))

    return df


# 示例用法
if __name__ == "__main__":
    # 绘制单次运行优化曲线
    plot_optimization_curve_for_single_run("Attractive_Sector", "BBO_EACO")
    plot_optimization_curve_for_single_run("Bent_Cigar", "CMAES")

    # 绘制归一化跨问题曲线
    plot_normalized_across_problems("DE")
    plot_normalized_across_problems("PSO")

    # 生成性能比较表格
    performance_table = generate_performance_table()
    print("性能比较表格:")
    print(performance_table)

    # 反NFL性能比较分析
    anti_nfl_df = anti_nfl_analysis()
    print("\n反NFL分析结果:")
    print(anti_nfl_df)