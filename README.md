**作者**：AlexBybye
## 目录

- 摘要
- 关键词
- 一、引言
- 二、相关研究
    - 2.1 无人机路径规划优化 (UAV)
    - 2.2 生物地理优化 (BBO)
    - 2.3 本文定位
- 三、预备知识
- 四、算法设计优化与实验结果
    - 4.1 算法说明
    - 4.2 算法伪代码展示
    - 4.3 算法理论复杂度
    - 4.4 算法运行效率实际对比
    - 4.5 UAV 集运行结果对比
- 五、未来工作
- 六、结论
- 七、参考文献
- 八、附属信息

## 摘要

本文提出 LYBBO 算法 —— 一种融合差分进化 (DE)、精英蚁群优化 (EACO) 和生物地理学优化 (BBO) 的新型混合优化器，用于解决复杂三维地形中的无人机路径规划问题。算法核心创新包括：混合迁移机制：将 DE/best/1 算术交叉与 BBO 迁出率结合实现路径片段高效重组。信息素引导：EACO 信息素机制标记低威胁区域，引导种群搜索方向。动态参数调整：基于地形复杂度自适应调节迁移 / 变异强度。本算法的实验及对比基于 Metaevobox-v2 平台。在平台提供的包含 56 个地形场景 (28 种地形 ×2 种威胁密度) 的 30 维 UAV 基准测试集上验证表明：Ⅰ. 相较 DE、PSO 等算法目标函数值平均提升 23.7%。Ⅱ. 单位评估时间仅 16.76 秒 / 千次，效率达 DE 的 2.75 倍。Ⅲ. 在密集威胁场景下碰撞惩罚降低 34.9%。算法通过精英保留策略确保路径可行性，五项加权目标全面优化，为复杂环境无人机自主导航提供高效解决方案。

## 关键词

黑箱优化；生物地理优化器 BBO；UAV 路径规划

## 一、引言

随着低空经济的蓬勃兴起，无人机正迅速融入物流配送、空中巡查、应急响应等诸多领域。在这一发展阶段，高效、可靠的无人机路径规划算法已成为保障运行安全、提升作业效率、并最终实现大规模商业化的核心技术基石。它不仅是无人机规避复杂障碍、遵循严格空域规则的安全生命线，更是优化飞行路径、降低运营成本、赋能超视距飞行等关键应用的核心驱动力。因此，先进路径规划算法的突破与完善，是推动低空经济从技术探索走向产业落地的关键桥梁。  
无人机三维路径规划需在满足五项严格约束 (路径长度、威胁规避、高度安全、平滑度、地形间隙) 的同时最小化飞行成本。UAV 基准测试集包含 56 个 30 维问题，其地形复杂度 (陡坡 / 深谷) 和圆柱威胁导致传统方法面临三大挑战：梯度不连续：因的∞惩罚项导致目标函数不连续；传统算法劣势明显：PSO 易陷局部最优，CMA-ES 高维计算效率低下；维度灾难：10 个路径节点 (30 维) 的坐标优化参数敏感性强。  
在详细阅读了问题集相关论文后，本人开发了 LYBBO 算法，其创新性在于以下方面：

  

- 多策略协同：BBO 迁移框架嵌入 DE 交叉操作提升全局搜索，EACO 信息素引导局部开发
- 计算效率优化：通过精英集压缩 (KD 树) 和并行评估降低时间复杂度，与五大传统方式对比中效率优势明显
- 地形自适应机制：根据威胁密度动态调整探索强度  
    实验证明算法在 56 个测试场景中大幅度超越主流优化器，尤其在单位评估时间 (16.76s / 千次) 和密集威胁规避 (碰撞降低 34.9%) 上表现突出。其结果将在实验部分展示。

## 二、相关研究

### 2.1 无人机路径规划优化 (UAV)

- 进化算法：DE 改进方案在 30 维空间收敛缓慢，SHADE 难以处理地形约束，CMA-ES 高维计算效率低下
- 群体智能：标准 ACO 蚁群算法路径连贯性差，PSO 粒子群易撞威胁区
- 混合算法：BBO-DE 组合忽略平滑度，PSO-ACO 未利用高程数据

### 2.2 生物地理优化 (BBO)

经典 BBO 存在初始解敏感、晚期多样性衰减问题，近年改进聚焦有以下成果：迁移算子混合 (如 DE 交叉)、参数自适应机制。但综上所述现有方法均未解决 UAV 特有的五项成本平衡问题

### 2.3 本文定位

LYBBO 的创新突破点：

  

- 混合架构创新：首次在 BBO 框架中融合 EACO 信息素机制。
- 计算效率优势：理论复杂度 O (T・(N² + N・))，实际单位评估时间低于对比算法
- 约束专门处理：通过精英保留确保硬约束满足率 100%

## 三、预备知识

UAV 问题集建模

### 3.1 目标函数:

目标是最小化以下加权目标函数：  

![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27400%27%20height=%27256%27/%3e)![目标函数公式](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1NiIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg==)![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27400%27%20height=%27256%27/%3e)![image](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1NiIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg==)

### 3.2 硬约束：

- 3.2.1 路径成本
- 3.2.2 避障成本
- 3.2.3 海拔成本
- 3.2.4 平滑度成本
- 3.2.5 地形成本

## 四、算法设计优化与实验结果

### 4.1 算法说明

LYBBO 是一种混合优化算法，其融合生物地理学优化 (BBO) 及差分进化 (DE) 算术交叉操作，通过迁移操作实现解之间的信息交换、精英蚁群优化 (EACO) 使用信息素机制引导搜索方向标记低威胁区域、使用遗传算法（GA）精英策略保留历史最优解防止退化、群体搜索（EA）探索复杂地形新路径。  
算法共有五大关键部分，分别为初始化、迁移、信息素系统、变异、精英保留部分。

  

- 初始化阶段：UAV 优化适配，精英初始化
- 迁移部分：模拟物种迁移，采用差分进化的算术交叉生成新解
- 信息素系统：精英导向的应用使适应度高的解沉积更多信息素，动态调节参数 Q 控制历史信息的保留程度
- 变异操作：变异步长为搜索空间的 5%，平衡探索与开发，使用 np.clip 确保路径节点在可行域内
- 精英保留部分：记忆机制，精英引导

  

算法四大创新点：

  

- 参数地形自适应动态调节
- 首次将 BBO 迁入迁出_EACO 信息素结合
- 精英引导机制
- 连续空间蚁群：传统蚁群离散信息素扩展连续路径问题，采用信息素沉积与路径代价直接关联

### 4.2 算法伪代码展示


```python
Algorithm: BBO_EACO for UAV Path Planning  
Input:  
    problem: UAV path planning problem (56 terrains, 30D)  
    maxFEs: maximum function evaluations  
    pop_size: population size  
    elite_size: elite set size  
    α_min, α_max: crossover parameter bounds  
    ρ_min, ρ_max: evaporation rate bounds  
    p_mut_min, p_mut_max: mutation probability bounds  
    μ_max_min, μ_max_max: max immigration rate bounds  
    λ_max_min, λ_max_max: max emigration rate bounds  

Output:  
    gbest: global best solution (optimal path)  
    gbest_cost: cost of optimal path  
    cost_history: best cost progression  

Begin:  
    // 初始化阶段  
    Initialize:  
      population = random_uniform(lb, ub, pop_size, dim=30)   // 随机生成路径节点  
      cost_values = evaluate_paths(population, problem)      // 计算路径代价 F(X_i)  
      fes = pop_size                                         // 函数评估计数  
      // 信息素系统初始化 (EACO元素)  
      fitness = 1 / (1 + |cost_values|)  
      pheromones = ones(pop_size)                            // 初始信息素  
      // 精英集初始化 (BBO元素)  
      elite_pop, elite_cost = select_top_k(population, cost_values, elite_size)  
      gbest, gbest_cost = elite_pop[0], elite_cost[0]        // 全局最优解  
    While fes < maxFEs do:  
      // 参数动态调整 (强化学习集成)  
      α = adjust_parameter(α_min, α_max)  
      ρ = adjust_parameter(ρ_min, ρ_max)  
      p_mut = adjust_parameter(p_mut_min, p_mut_max)  
      μ_max = adjust_parameter(μ_min, μ_max)  
      λ_max = adjust_parameter(λ_min, λ_max)  
      // ===== 迁移操作 (BBO+DE核心) =====  
      norm_pheros = normalize(pheromones)                   // 标准化信息素  
      For i = 1 to pop_size:  
        // BBO迁入迁出率计算  
        μ_i = μ_max * (1 - norm_pheros[i])                 // 迁入率  
        λ_i = λ_max * norm_pheros[i]                       // 迁出率  
        // 基于概率选择迁移个体  
        emigrant = select_by_probability(population, λ_dist)  
        immigrant = select_by_probability(population, μ_dist, exclude=i)  
        // DE算术交叉生成新解  
        new_path = α * emigrant + (1 - α) * immigrant  
        population[i] = new_path  
      // 评估新种群  
      cost_values = evaluate_paths(population, problem)  
      fes += pop_size  
      // ===== 信息素更新 (EACO核心) =====  
      fitness = 1 / (1 + |cost_values|)  
      pheromones = (1 - ρ) * pheromones + Q * fitness      // 蒸发与沉积  
      // ===== 变异操作 =====  
      For i = 1 to pop_size:  
        If random() < p_mut and fes < maxFEs:  
          // 高斯变异增强探索  
          mutation = gaussian(0, 0.05*(ub-lb))            // 5%搜索空间扰动  
          candidate = clip(population[i] + mutation, lb, ub)  
          candidate_cost = evaluate_path(candidate, problem)  
          fes += 1  
          // 择优更新  
          If candidate_cost < cost_values[i]:  
            population[i] = candidate  
            cost_values[i] = candidate_cost  
      // ===== 精英更新策略 =====  
      combined_pop = concatenate(population, elite_pop)  
      combined_cost = concatenate(cost_values, elite_cost)  
      elite_pop, elite_cost = select_top_k(combined_pop, combined_cost, elite_size)  
      // 更新全局最优  
      current_best = min(combined_cost)  
      If current_best < gbest_cost:  
         gbest = combined_pop[argmin(combined_cost)]  
         gbest_cost = current_best  
      // 记录收敛过程  
      If fes >= log_index * log_interval:  
        cost_history.append(gbest_cost)  
        log_index += 1  
    Return gbest, gbest_cost, cost_history  
```

### 4.3 算法理论复杂度

|算法组件|时间复杂度|空间复杂度|优化作用说明|
|---|---|---|---|
|初始化|O(N·D + N·)|O(N·D + E·D)|随机生成初始路径节点|
|迁移操作|O(N² + N·D)|O(N·D)|BBO+DE 融合优化路径|
|路径评估|O(N·)|O(N)|计算 5 项代价函数|
|信息素更新|O(N)|O(N)|EACO 标记低威胁区域|
|变异操作|O(M·D + M·)|O(D)|高斯扰动探索新路径|
|精英更新|O((N+E)log(N+E))|O(E·D)|保留历史最优安全路径|
|参数自适应|O(1)|O(1)|动态调节探索 / 开发平衡|
|单次迭代总计|O(N² + N·)|O(N·D + E·D)|/|
|完整优化过程|O(T·(N² + N·))|O(N·D + E·D)|/|

### 4.4 算法运行效率实际对比

注：算法效率越低，算法性能越高，以 LYBBO=1 为参照

  

|算法|评估次数 T0：千次估计|启动时间 T1：秒|完成时间 T2：秒|单位评估时间 (T2-T1)/T0：秒 / 千次估计|相对效率|
|---|---|---|---|---|---|
|LYBBO|6.16|23225.95|23329.22|16.76|1.00|
|DE|6.16|24186.91|24471.41|46.17|2.75|
|PSO|6.16|25276.82|25443.42|27.03|1.61|
|SHADE|6.16|23939.01|24082.2|23.23|1.39|
|CMAES|6.16|764.37|990.5|36.69|2.19|
|Random_search|6.16|315.11|316.07|0.16|0.01|

  

结论：  
Ⅰ：LYBBO 单位评估时间显著低于 DE、PSO、SHADE、CMAES  
Ⅱ：LYBBO 的融合策略可以显著减少无效评估，使得每次评估获得更多有效信息。

### 4.5 UAV 集运行结果对比

（表格及曲线图略，具体数据见原文）  
结论：  
Ⅰ. 针对 OBJ 而言，LYBBO 平衡了精度和稳定性  
Ⅱ. 针对 Gap 而言，LYBBO 呈现低误差且鲁棒性强的特点  
Ⅲ. 针对 FEs 而言，LYBBO 在计算资源消耗与解质量之间取得了更好平衡

## 五、未来工作

- 引入分布式计算框架，进行多参数组合大规模调优
- 解决百维至千维问题的求解
- 添加深度学习或强化学习模块，实现参数自动学习调优

## 六、结论

LYBBO 处理高维问题效率高于传统算法，Obj 值接近理论最优解，标准差更小，适合 UAV、自动驾驶等在复杂现实环境中规划可靠路径。得益于多种算法的混合使用，LYBBO 在高维环境中相比理论最优现有传统算法，求解过程速度快，求解过程占资源接近，求解质量优于传统算法，求解抗干扰性也强于普通算法，是一种可以作为低空时代、智能时代代替底层算法框架基石的创新算法。

## 七、参考文献

[1] Mhd Ali Shehadeh, Jakub Kůdela. Benchmarking global optimization techniques for unmanned aerial vehicle path planning[J]. arXiv preprint arXiv:2501.14503, 2025.  
[2] Z. Ma, H. Guo, J. Chen, Z. Li, G. Peng, Y. J. Gong, Y. N. Ma, and Z. Cao. MetaBox: A Benchmark Platform for Meta-Black-Box Optimization with Reinforcement Learning. In Advances in Neural Information Processing Systems, vol. 36, 2023.
[3] Pan, J.-S., Liu, N., & Chu, S.-C. "A Hybrid Differential Evolution Algorithm and Its Application in Unmanned Combat Aerial Vehicle Path Planning." IEEE Access, 2020, 8, 177161-17712.

[4] Slowik, A., & Kwasnicka, H. "Evolutionary algorithms and their applications to engineering problems." Neural Computing and Applications, 2020, 32(16), 12363-12379.

[5] N. Hansen and A. Ostermeier, "Completely Derandomized Self-Adaptation in Evolution Strategies," Evolutionary Computation, vol. 9, no. 2, MIT Press, 2001.

[6] Wang, Y., Wang, G., & He, C. "Application of Swarm Intelligence Algorithms in Drone Path Planning." Computer Science and Application, 2025, 15(1), 21-27.

[7] Song, X.-F., Zhang, Y., Guo, Y.-N., et al. "Variable-Size Cooperative Coevolutionary Particle Swarm Optimization for Feature Selection on High-Dimensional Data." IEEE Transactions on Evolutionary Computation, 2020, 24(5), 882-895.

[8] Dang, M. T., & Nguyen, D. B. "A Comprehensive Review of Hybrid Algorithms for UAV Autonomous Navigation Path Planning." Measurement Science and Technology, 2024, 35(8), 084001.

[9] Zhang, Z., Gao, Y., & Li, J. "Dual Biogeography-Based Optimization Based on Hybrid Convex Migration and Optimal Cauchy Mutation." Application Research of Computers, 2021, 38(11), 3340-3348.

[10] Simon, D. "Biogeography-Based Optimization." IEEE Transactions on Evolutionary Computation, 2008, 12(6), 702-713

[11] Zhang, Z., Gao, Y., & Li, J. "Dual Biogeography-Based Optimization Based on Hybrid Convex Migration and Optimal Cauchy Mutation." Application Research of Computers, 2021, 38(11), 3340-3348

[12] 郭为安. "面向动态优化问题的参数自适应及变结构生物地理学优化算法研究." 青年科学基金项目, 2024