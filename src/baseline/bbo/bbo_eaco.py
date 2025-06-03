import numpy as np
from typing import Any, Tuple
from ...environment.optimizer.basic_optimizer import Basic_Optimizer
from metaevobox.environment.problem.basic_problem import Basic_Problem

class BBO_EACO(Basic_Optimizer):
    def __init__(self, config):
        super().__init__(config)

        self.config = config
        self.max_fes = config.maxFEs
        self.fes = 0
        self.log_index = 1
        self.log_interval = config.log_interval
        # Algorithm parameters with default values
        self.pop_size = getattr(config, 'BBO_EACO_params', {}).get('pop_size', 100)
        self.alpha = getattr(config, 'BBO_EACO_params', {}).get('alpha', 0.2)
        self.rho = getattr(config, 'BBO_EACO_params', {}).get('rho', 0.2)
        self.Q = getattr(config, 'BBO_EACO_params', {}).get('Q', 100)
        self.p_mutate = getattr(config, 'BBO_EACO_params', {}).get('p_mutate', 0.3)
        self.mu_max = getattr(config, 'BBO_EACO_params', {}).get('mu_max', 0.8)
        self.lambda_max = getattr(config, 'BBO_EACO_params', {}).get('lambda_max', 0.8)
        self.elite_size = getattr(config, 'BBO_EACO_params', {}).get('elite_size', 8)

        # Placeholders for algorithm state
        self.population = None
        self.cost_values = None
        self.fitness = None
        self.pheromones = None
        self.gbest = None
        self.gbest_cost = float('inf')
        self.elite_pop = None
        self.elite_cost = None
        self.dim = None
        self.lb = None
        self.ub = None
        self.cost_history = []
        self.__n_logpoint = config.maxFEs // config.log_interval

    def __str__(self):
        """
             Returns a string representation of the object.
             # Returns:
            - str: The string "BBO_EACO" representing the object.
        """
        return "BBO_EACO"

    def init_population(self, problem: Basic_Problem) -> Any:
        """Initialize population and algorithm state"""
        self.dim = problem.dim
        self.lb = problem.lb
        self.ub = problem.ub
        self.fes = 0
        self.log_index = 1
        self.cost_history = []

        # Initialize population
        self.population = np.random.uniform(
            self.lb, self.ub, (self.pop_size, self.dim))

        # Evaluate initial population
        self.cost_values = problem.eval(self.population)
        self.fes = self.pop_size

        # Initialize fitness
        self.fitness = 1 / (1 + np.abs(self.cost_values))

        # Initialize pheromones
        self.pheromones = np.ones(self.pop_size)

        # Initialize global best
        best_idx = np.argmin(self.cost_values)
        self.gbest = self.population[best_idx].copy()
        self.gbest_cost = self.cost_values[best_idx]

        # Initialize elite set
        elite_idx = np.argsort(self.cost_values)[:self.elite_size]
        self.elite_pop = self.population[elite_idx].copy()
        self.elite_cost = self.cost_values[elite_idx].copy()

        # Initialize cost history
        self.cost_history = [self.gbest_cost]

        # Return initial state
        return self._get_state()

    def update(self, action: np.ndarray, problem: Basic_Problem) -> Tuple[Any, float, bool]:
        """Update population using agent's action"""
        if self.fes >= self.max_fes:
            return self._get_state(), 0.0, True

        # Save current best for reward calculation
        old_gbest_cost = self.gbest_cost

        # Update parameters from agent's action
        self.alpha = action[0]  # Crossover parameter
        self.rho = action[1]  # Evaporation rate
        self.p_mutate = action[2]  # Mutation probability
        self.mu_max = action[3]  # Immigration rate
        self.lambda_max = action[4]  # Emigration rate

        # Migration
        self._migrate()

        # Evaluate new population after migration
        self.cost_values = problem.eval(self.population)
        self.fes += self.pop_size

        # Update fitness and pheromones
        self.fitness = 1 / (1 + np.abs(self.cost_values))
        self._update_pheromones()

        # Mutation (handles FEs internally)
        self._mutate(problem)

        # Update elite solutions
        self._update_elite()

        # Calculate reward as improvement in best cost
        reward = old_gbest_cost - self.gbest_cost

        # Update cost history for logging
        if self.fes >= self.log_index * self.log_interval:
            self.log_index += 1
            self.cost_history.append(self.gbest_cost)

        # Check termination
        is_done = self.fes >= self.max_fes

        return self._get_state(), reward, is_done

    def _get_state(self) -> np.ndarray:
        """Get current optimizer state for agent"""
        if self.cost_values is None or len(self.cost_values) == 0:
            # Return default state before initialization
            return np.array([
                0.0,  # best_cost
                0.0,  # worst_cost
                0.0,  # mean_cost
                0.0,  # fes_ratio
                self.alpha,
                self.rho,
                self.p_mutate,
                self.mu_max,
                self.lambda_max
            ])

        best_cost = np.min(self.cost_values)
        worst_cost = np.max(self.cost_values)
        mean_cost = np.mean(self.cost_values)
        fes_ratio = self.fes / self.max_fes

        return np.array([
            best_cost,
            worst_cost,
            mean_cost,
            fes_ratio,
            self.alpha,
            self.rho,
            self.p_mutate,
            self.mu_max,
            self.lambda_max
        ])

    def _migrate(self):
        """Migration operation"""
        # Normalize pheromones
        norm_pheromones = self.pheromones / (np.max(self.pheromones) + 1e-10)

        # Calculate migration rates
        mu = self.mu_max * (1 - norm_pheromones)  # Immigration rate
        lamb = self.lambda_max * norm_pheromones  # Emigration rate

        # Create probability distributions and ensure they sum to 1
        mu_sum = np.sum(mu)
        lamb_sum = np.sum(lamb)
        
        # Handle edge cases where sums are 0
        if mu_sum == 0:
            mu_dist = np.ones(self.pop_size) / self.pop_size
        else:
            mu_dist = mu / mu_sum
            
        if lamb_sum == 0:
            lamb_dist = np.ones(self.pop_size) / self.pop_size
        else:
            lamb_dist = lamb / lamb_sum

        # Create temporary population copy
        temp_pop = self.population.copy()

        for i in range(self.pop_size):
            # Select emigrant (根据迁出率)
            j = np.random.choice(self.pop_size, p=lamb_dist)

            # Select immigrant (根据迁入率，不能是自己)
            k = np.random.choice(self.pop_size, p=mu_dist)
            while k == i:
                k = np.random.choice(self.pop_size, p=mu_dist)

            # Create new solution through crossover (算术交叉)
            alpha_val = self.alpha * np.random.rand(self.dim)
            self.population[i] = alpha_val * temp_pop[j] + (1 - alpha_val) * temp_pop[k]

    def _mutate(self, problem: Basic_Problem):
        """Mutation operation"""
        # Calculate mutation strength (5% of the range)
        sigma = 0.05 * (problem.ub - problem.lb)

        for i in range(self.pop_size):
            if self.fes >= self.max_fes:
                break

            if np.random.rand() < self.p_mutate:
                # Gaussian mutation
                mutation = np.random.normal(0, sigma, self.dim)
                candidate = self.population[i] + mutation

                # Apply bounds
                candidate = np.clip(candidate, problem.lb, problem.ub)

                # Evaluate candidate
                candidate_cost = problem.eval(candidate.reshape(1, -1))[0]
                self.fes += 1

                # Update if better
                if candidate_cost < self.cost_values[i]:
                    self.population[i] = candidate
                    self.cost_values[i] = candidate_cost
                    self.fitness[i] = 1 / (1 + np.abs(candidate_cost))

    def _update_elite(self):
        """Update elite solutions"""
        # Combine current population and elite
        combined_pop = np.vstack([self.population, self.elite_pop])
        combined_cost = np.concatenate([self.cost_values, self.elite_cost])

        # Select new elite
        elite_idx = np.argsort(combined_cost)[:self.elite_size]
        self.elite_pop = combined_pop[elite_idx]
        self.elite_cost = combined_cost[elite_idx]

        # Update global best
        current_best = np.min(combined_cost)
        if current_best < self.gbest_cost:
            self.gbest = combined_pop[np.argmin(combined_cost)].copy()
            self.gbest_cost = current_best

    def _update_pheromones(self):
        """Update pheromone levels"""
        # Evaporation
        self.pheromones *= (1 - self.rho)

        # Pheromone deposit proportional to fitness
        self.pheromones += self.Q * self.fitness

        # Prevent negative values
        self.pheromones = np.clip(self.pheromones, 0, None)

    def run_episode(self, problem: Basic_Problem) -> dict:
        """Run a complete optimization episode
        Args:
            problem: The optimization problem to solve
        Returns:
            dict: Dictionary containing optimization results
        """
        # Initialize variables for logging
        self.meta_X = []  # Store populations at each generation
        self.meta_Cost = []  # Store cost values at each generation
        self.cost = []  # Store best cost at each logging interval
        log_index = 1  # Track current logging index

        # Initialize population
        self.init_population(problem)

        # Check if metadata collection is enabled
        if self.config.full_meta_data:
            self.meta_X.append(self.population.copy())
            self.meta_Cost.append(self.cost_values.copy())

        # Run optimization until max FEs is reached
        is_end = False
        while not is_end:
            # Create dummy action (no learning in this case)
            action = np.array([self.alpha, self.rho, self.p_mutate, self.mu_max, self.lambda_max])

            # Update population
            _, _, done = self.update(action, problem)
            is_end = done

            # Log population and cost values if metadata collection is enabled
            if self.config.full_meta_data and not is_end:
                self.meta_X.append(self.population.copy())
                self.meta_Cost.append(self.cost_values.copy())

            # Log best cost at specified intervals
            if self.fes >= log_index * self.config.log_interval:
                self.cost.append(self.gbest_cost)
                log_index += 1

        # Ensure we have at least one cost entry
        if not self.cost:
            self.cost.append(self.gbest_cost)

        # Prepare results dictionary
        results = {
            'cost': self.cost,
            'fes': self.fes
        }

        # Add metadata if collection is enabled
        if self.config.full_meta_data:
            metadata = {
                'X': self.meta_X,
                'Cost': self.meta_Cost
            }
            results['metadata'] = metadata

        return results