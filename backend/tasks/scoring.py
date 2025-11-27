"""
Task Scoring Algorithm Module

This module contains the core logic for calculating task priority scores
based on multiple factors: urgency, importance, effort, and dependencies.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Set
import math


class TaskScorer:
    """
    Handles task priority scoring with configurable strategies.
    """

    # Default weights for balanced scoring
    DEFAULT_WEIGHTS = {
        'urgency': 0.35,
        'importance': 0.30,
        'effort': 0.20,
        'dependencies': 0.15
    }

    def __init__(self, strategy='smart_balance', custom_weights=None):
        """
        Initialize scorer with a specific strategy.
        
        Args:
            strategy: One of 'smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'
            custom_weights: Optional dict to override default weights
        """
        self.strategy = strategy
        self.weights = self._get_weights(strategy, custom_weights)

    def _get_weights(self, strategy, custom_weights):
        """Determine weights based on strategy."""
        if custom_weights:
            return custom_weights

        strategy_weights = {
            'smart_balance': {'urgency': 0.35, 'importance': 0.30, 'effort': 0.20, 'dependencies': 0.15},
            'fastest_wins': {'urgency': 0.15, 'importance': 0.15, 'effort': 0.60, 'dependencies': 0.10},
            'high_impact': {'urgency': 0.15, 'importance': 0.65, 'effort': 0.05, 'dependencies': 0.15},
            'deadline_driven': {'urgency': 0.70, 'importance': 0.15, 'effort': 0.05, 'dependencies': 0.10}
        }

        return strategy_weights.get(strategy, self.DEFAULT_WEIGHTS)

    def calculate_urgency_score(self, due_date: str) -> float:
        """
        Calculate urgency score based on how soon the task is due.
        
        Returns a score from 0-100:
        - Past due: 100 (maximum urgency)
        - Due today: 95
        - Due within 3 days: 80-90
        - Due within 7 days: 60-80
        - Due within 14 days: 40-60
        - Due within 30 days: 20-40
        - Due later: 10-20
        """
        try:
            if isinstance(due_date, str):
                due = datetime.strptime(due_date, '%Y-%m-%d').date()
            elif isinstance(due_date, date):
                due = due_date
            else:
                return 50  # Default for invalid date

            today = date.today()
            days_until_due = (due - today).days

            if days_until_due < 0:
                # Past due - exponentially increase urgency
                return min(100, 100 + abs(days_until_due) * 2)
            elif days_until_due == 0:
                return 95
            elif days_until_due <= 3:
                return 90 - (days_until_due * 3)
            elif days_until_due <= 7:
                return 80 - ((days_until_due - 3) * 5)
            elif days_until_due <= 14:
                return 60 - ((days_until_due - 7) * 3)
            elif days_until_due <= 30:
                return 40 - ((days_until_due - 14) * 1.25)
            else:
                # Asymptotic approach to minimum score
                return max(10, 20 - math.log(days_until_due - 29, 2))

        except (ValueError, TypeError):
            return 50  # Default score for invalid dates

    def calculate_importance_score(self, importance: int) -> float:
        """
        Convert importance rating (1-10) to a 0-100 score.
        Uses exponential scaling to emphasize high-importance tasks.
        """
        if not isinstance(importance, (int, float)) or importance < 1 or importance > 10:
            return 50  # Default for invalid importance

        # Exponential scaling: importance^1.5 normalized to 0-100
        return (importance ** 1.5) / (10 ** 1.5) * 100

    def calculate_effort_score(self, estimated_hours: float, strategy_type: str = None) -> float:
        """
        Calculate effort score. Lower effort = higher score for quick wins.
        
        Returns a score from 0-100:
        - < 1 hour: 95-100 (quick wins)
        - 1-3 hours: 80-95
        - 3-8 hours: 50-80
        - 8-16 hours: 30-50
        - > 16 hours: 10-30
        """
        if not isinstance(estimated_hours, (int, float)) or estimated_hours <= 0:
            return 50  # Default for invalid effort

        if estimated_hours < 1:
            return 100 - (estimated_hours * 5)
        elif estimated_hours <= 3:
            return 95 - ((estimated_hours - 1) * 7.5)
        elif estimated_hours <= 8:
            return 80 - ((estimated_hours - 3) * 6)
        elif estimated_hours <= 16:
            return 50 - ((estimated_hours - 8) * 2.5)
        else:
            # Asymptotic decrease
            return max(10, 30 - math.log(estimated_hours - 15, 2) * 5)

    def calculate_dependency_score(self, task_id: Any, all_tasks: List[Dict]) -> float:
        """
        Calculate dependency score based on how many tasks depend on this one.
        Tasks that block others should have higher priority.
        
        Returns a score from 0-100.
        """
        blocking_count = 0

        for task in all_tasks:
            dependencies = task.get('dependencies', [])
            if task_id in dependencies:
                blocking_count += 1

        # Score increases with number of blocked tasks
        if blocking_count == 0:
            return 30  # Base score for non-blocking tasks
        elif blocking_count == 1:
            return 60
        elif blocking_count == 2:
            return 80
        else:
            # Cap at 100
            return min(100, 80 + (blocking_count - 2) * 10)

    def detect_circular_dependencies(self, tasks: List[Dict]) -> List[str]:
        """
        Detect circular dependencies using depth-first search.
        
        Returns list of task IDs involved in circular dependencies.
        """
        task_dict = {task.get('id') or i: task for i, task in enumerate(tasks)}
        circular = []
        visited = set()
        rec_stack = set()

        def has_cycle(task_id, path):
            if task_id in rec_stack:
                circular.extend(path[path.index(task_id):])
                return True

            if task_id in visited:
                return False

            visited.add(task_id)
            rec_stack.add(task_id)

            task = task_dict.get(task_id)
            if task:
                dependencies = task.get('dependencies', [])
                for dep_id in dependencies:
                    if has_cycle(dep_id, path + [task_id]):
                        return True

            rec_stack.remove(task_id)
            return False

        for task_id in task_dict.keys():
            if task_id not in visited:
                has_cycle(task_id, [])

        return list(set(circular))

    def calculate_score(self, task: Dict, all_tasks: List[Dict] = None) -> Dict[str, Any]:
        """
        Calculate overall priority score for a task.
        
        Args:
            task: Task dictionary with title, due_date, estimated_hours, importance, dependencies
            all_tasks: List of all tasks (needed for dependency calculation)

        Returns:
            Dictionary with score, component scores, and explanation
        """
        if all_tasks is None:
            all_tasks = [task]

        task_id = task.get('id')
        
        # Calculate component scores
        urgency = self.calculate_urgency_score(task.get('due_date'))
        importance = self.calculate_importance_score(task.get('importance', 5))
        effort = self.calculate_effort_score(task.get('estimated_hours', 1))
        dependencies = self.calculate_dependency_score(task_id, all_tasks)

        # Calculate weighted total
        total_score = (
            urgency * self.weights['urgency'] +
            importance * self.weights['importance'] +
            effort * self.weights['effort'] +
            dependencies * self.weights['dependencies']
        )

        # Generate explanation
        explanation = self._generate_explanation(
            task, urgency, importance, effort, dependencies, total_score
        )

        return {
            'score': round(total_score, 2),
            'components': {
                'urgency': round(urgency, 2),
                'importance': round(importance, 2),
                'effort': round(effort, 2),
                'dependencies': round(dependencies, 2)
            },
            'explanation': explanation
        }

    def _generate_explanation(self, task, urgency, importance, effort, dependencies, total_score):
        """
        Generate human-readable explanation for the score.
        """
        reasons = []

        # Analyze each component
        if urgency > 80:
            due_date = task.get('due_date')
            try:
                if isinstance(due_date, str):
                    due = datetime.strptime(due_date, '%Y-%m-%d').date()
                else:
                    due = due_date
                days = (due - date.today()).days
                if days < 0:
                    reasons.append(f"OVERDUE by {abs(days)} days")
                elif days == 0:
                    reasons.append("Due TODAY")
                else:
                    reasons.append(f"Due very soon ({days} days)")
            except:
                reasons.append("High urgency")
        elif urgency > 60:
            reasons.append("Approaching deadline")

        if importance > 75:
            reasons.append("High importance rating")
        
        if effort > 80:
            reasons.append("Quick win (low effort)")
        elif effort < 30 and self.strategy != 'fastest_wins':
            reasons.append("High effort task")

        if dependencies > 60:
            reasons.append("Blocks other tasks")

        if not reasons:
            reasons.append("Balanced priority")

        return ' • '.join(reasons)

    def score_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Score and sort multiple tasks.
        
        Args:
            tasks: List of task dictionaries

        Returns:
            List of tasks with scores, sorted by priority (highest first)
        """
        # Add IDs if not present
        for i, task in enumerate(tasks):
            if 'id' not in task:
                task['id'] = i

        # Check for circular dependencies
        circular = self.detect_circular_dependencies(tasks)
        
        # Score each task
        scored_tasks = []
        for task in tasks:
            score_data = self.calculate_score(task, tasks)
            
            result = {
                **task,
                'priority_score': score_data['score'],
                'score_components': score_data['components'],
                'explanation': score_data['explanation']
            }
            
            if task.get('id') in circular:
                result['warning'] = 'Circular dependency detected'
            
            scored_tasks.append(result)

        # Sort by score (descending)
        scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return scored_tasks

    def get_top_suggestions(self, tasks: List[Dict], count: int = 3) -> List[Dict]:
        """
        Get top N task suggestions with detailed explanations.
        
        Args:
            tasks: List of task dictionaries
            count: Number of suggestions to return

        Returns:
            List of top priority tasks with enhanced explanations
        """
        scored_tasks = self.score_tasks(tasks)
        top_tasks = scored_tasks[:count]

        # Enhance explanations for suggestions
        for i, task in enumerate(top_tasks, 1):
            task['rank'] = i
            task['suggestion_reason'] = f"Rank #{i}: {task['explanation']}"

        return top_tasks