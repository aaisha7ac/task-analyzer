from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer


class TaskScorerTestCase(TestCase):
    """
    Unit tests for the TaskScorer class.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.scorer = TaskScorer(strategy='smart_balance')
        self.today = date.today()

    def test_urgency_score_past_due(self):
        """
        Test urgency scoring for past-due tasks.
        Past-due tasks should have urgency score >= 100.
        """
        past_date = (self.today - timedelta(days=5)).strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(past_date)
        
        self.assertGreaterEqual(score, 100, "Past-due tasks should have urgency >= 100")

    def test_urgency_score_due_today(self):
        """
        Test urgency scoring for tasks due today.
        Should return 95.
        """
        today_str = self.today.strftime('%Y-%m-%d')
        score = self.scorer.calculate_urgency_score(today_str)
        
        self.assertEqual(score, 95, "Tasks due today should have urgency score of 95")

    def test_urgency_score_future(self):
        """
        Test urgency scoring for future tasks.
        Further dates should have lower scores.
        """
        near_future = (self.today + timedelta(days=2)).strftime('%Y-%m-%d')
        far_future = (self.today + timedelta(days=20)).strftime('%Y-%m-%d')
        
        near_score = self.scorer.calculate_urgency_score(near_future)
        far_score = self.scorer.calculate_urgency_score(far_future)
        
        self.assertGreater(near_score, far_score, 
                          "Nearer deadlines should have higher urgency scores")

    def test_importance_score_range(self):
        """
        Test importance scoring with valid range (1-10).
        Higher importance should yield higher scores.
        """
        low_score = self.scorer.calculate_importance_score(1)
        high_score = self.scorer.calculate_importance_score(10)
        
        self.assertGreater(high_score, low_score, 
                          "Higher importance should yield higher scores")
        self.assertGreaterEqual(low_score, 0)
        self.assertLessEqual(high_score, 100)

    def test_importance_score_invalid(self):
        """
        Test importance scoring with invalid values.
        Should return default score of 50.
        """
        score_negative = self.scorer.calculate_importance_score(-1)
        score_too_high = self.scorer.calculate_importance_score(11)
        
        self.assertEqual(score_negative, 50, "Invalid importance should return 50")
        self.assertEqual(score_too_high, 50, "Invalid importance should return 50")

    def test_effort_score_quick_wins(self):
        """
        Test effort scoring for quick wins (< 1 hour).
        Lower effort should yield higher scores.
        """
        quick_task = self.scorer.calculate_effort_score(0.5)
        long_task = self.scorer.calculate_effort_score(10)
        
        self.assertGreater(quick_task, long_task, 
                          "Lower effort tasks should have higher scores")
        self.assertGreaterEqual(quick_task, 90, "Quick tasks should score >= 90")

    def test_effort_score_invalid(self):
        """
        Test effort scoring with invalid values.
        Should return default score of 50.
        """
        score_zero = self.scorer.calculate_effort_score(0)
        score_negative = self.scorer.calculate_effort_score(-5)
        
        self.assertEqual(score_zero, 50, "Zero effort should return 50")
        self.assertEqual(score_negative, 50, "Negative effort should return 50")

    def test_dependency_score_blocking_tasks(self):
        """
        Test dependency scoring for tasks that block others.
        Tasks with more dependents should score higher.
        """
        tasks = [
            {'id': 1, 'title': 'Task 1', 'dependencies': []},
            {'id': 2, 'title': 'Task 2', 'dependencies': [1]},
            {'id': 3, 'title': 'Task 3', 'dependencies': [1]},
        ]
        
        blocking_score = self.scorer.calculate_dependency_score(1, tasks)
        non_blocking_score = self.scorer.calculate_dependency_score(2, tasks)
        
        self.assertGreater(blocking_score, non_blocking_score,
                          "Blocking tasks should have higher dependency scores")

    def test_circular_dependency_detection(self):
        """
        Test detection of circular dependencies.
        Should identify tasks involved in circular dependency chains.
        """
        tasks_with_cycle = [
            {'id': 1, 'title': 'Task 1', 'dependencies': [2]},
            {'id': 2, 'title': 'Task 2', 'dependencies': [3]},
            {'id': 3, 'title': 'Task 3', 'dependencies': [1]},
        ]
        
        circular = self.scorer.detect_circular_dependencies(tasks_with_cycle)
        
        self.assertGreater(len(circular), 0, "Should detect circular dependencies")
        self.assertTrue(any(task_id in circular for task_id in [1, 2, 3]),
                       "Should identify tasks in the cycle")

    def test_no_circular_dependency(self):
        """
        Test circular dependency detection with valid dependency chain.
        Should return empty list for tasks without circular dependencies.
        """
        tasks_no_cycle = [
            {'id': 1, 'title': 'Task 1', 'dependencies': []},
            {'id': 2, 'title': 'Task 2', 'dependencies': [1]},
            {'id': 3, 'title': 'Task 3', 'dependencies': [2]},
        ]
        
        circular = self.scorer.detect_circular_dependencies(tasks_no_cycle)
        
        self.assertEqual(len(circular), 0, "Should not detect circular dependencies")

    def test_score_calculation_complete(self):
        """
        Test complete score calculation for a task.
        Should return score, components, and explanation.
        """
        task = {
            'id': 1,
            'title': 'Fix bug',
            'due_date': (self.today + timedelta(days=2)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        result = self.scorer.calculate_score(task)
        
        self.assertIn('score', result)
        self.assertIn('components', result)
        self.assertIn('explanation', result)
        self.assertIsInstance(result['score'], (int, float))
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)

    def test_multiple_task_scoring_and_sorting(self):
        """
        Test scoring and sorting of multiple tasks.
        Tasks should be sorted by priority score in descending order.
        """
        tasks = [
            {
                'title': 'Low priority',
                'due_date': (self.today + timedelta(days=30)).strftime('%Y-%m-%d'),
                'estimated_hours': 10,
                'importance': 3,
                'dependencies': []
            },
            {
                'title': 'High priority',
                'due_date': self.today.strftime('%Y-%m-%d'),
                'estimated_hours': 1,
                'importance': 10,
                'dependencies': []
            },
            {
                'title': 'Medium priority',
                'due_date': (self.today + timedelta(days=7)).strftime('%Y-%m-%d'),
                'estimated_hours': 4,
                'importance': 6,
                'dependencies': []
            }
        ]
        
        scored_tasks = self.scorer.score_tasks(tasks)
        
        # Should have same number of tasks
        self.assertEqual(len(scored_tasks), len(tasks))
        
        # Should be sorted by priority_score (descending)
        for i in range(len(scored_tasks) - 1):
            self.assertGreaterEqual(scored_tasks[i]['priority_score'], 
                                   scored_tasks[i + 1]['priority_score'],
                                   "Tasks should be sorted by score descending")
        
        # High priority task should be first
        self.assertEqual(scored_tasks[0]['title'], 'High priority')

    def test_strategy_fastest_wins(self):
        """
        Test 'fastest_wins' strategy.
        Should prioritize low-effort tasks more heavily.
        """
        tasks = [
            {
                'title': 'Quick task',
                'due_date': (self.today + timedelta(days=10)).strftime('%Y-%m-%d'),
                'estimated_hours': 0.5,
                'importance': 5,
                'dependencies': []
            },
            {
                'title': 'Long important task',
                'due_date': (self.today + timedelta(days=10)).strftime('%Y-%m-%d'),
                'estimated_hours': 20,
                'importance': 9,
                'dependencies': []
            }
        ]
        
        fast_scorer = TaskScorer(strategy='fastest_wins')
        scored = fast_scorer.score_tasks(tasks)
        
        # Quick task should rank higher with 'fastest_wins' strategy
        self.assertEqual(scored[0]['title'], 'Quick task',
                        "'fastest_wins' should prioritize low-effort tasks")

    def test_strategy_high_impact(self):
        """
        Test 'high_impact' strategy.
        Should prioritize importance over other factors.
        """
        tasks = [
            {
                'title': 'Low importance quick',
                'due_date': self.today.strftime('%Y-%m-%d'),
                'estimated_hours': 0.5,
                'importance': 3,
                'dependencies': []
            },
            {
                'title': 'High importance later',
                'due_date': (self.today + timedelta(days=20)).strftime('%Y-%m-%d'),
                'estimated_hours': 10,
                'importance': 10,
                'dependencies': []
            }
        ]
        
        impact_scorer = TaskScorer(strategy='high_impact')
        scored = impact_scorer.score_tasks(tasks)
        
        # High importance task should rank higher
        self.assertEqual(scored[0]['title'], 'High importance later',
                        "'high_impact' should prioritize importance")

    def test_get_top_suggestions(self):
        """
        Test getting top N task suggestions.
        Should return requested number of tasks with rank and enhanced explanations.
        """
        tasks = [
            {'title': f'Task {i}', 
             'due_date': (self.today + timedelta(days=i)).strftime('%Y-%m-%d'),
             'estimated_hours': i,
             'importance': 10 - i,
             'dependencies': []}
            for i in range(1, 6)
        ]
        
        suggestions = self.scorer.get_top_suggestions(tasks, count=3)
        
        self.assertEqual(len(suggestions), 3, "Should return requested number of suggestions")
        self.assertEqual(suggestions[0]['rank'], 1, "First suggestion should have rank 1")
        self.assertIn('suggestion_reason', suggestions[0], 
                     "Suggestions should have suggestion_reason field")

    def test_empty_task_list(self):
        """
        Test handling of empty task list.
        Should return empty list without errors.
        """
        scored = self.scorer.score_tasks([])
        self.assertEqual(len(scored), 0, "Empty input should return empty list")

    def test_missing_task_fields(self):
        """
        Test handling of tasks with missing optional fields.
        Should use defaults and not crash.
        """
        task = {
            'title': 'Minimal task',
            # Missing due_date, estimated_hours, importance, dependencies
        }
        
        # Should not raise exception
        try:
            result = self.scorer.calculate_score(task)
            self.assertIn('score', result)
        except Exception as e:
            self.fail(f"Should handle missing fields gracefully: {e}")