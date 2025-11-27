from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    TaskAnalyzeRequestSerializer,
    SuggestRequestSerializer
)
from .scoring import TaskScorer


@api_view(['POST'])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    
    Accept a list of tasks and return them sorted by priority score.
    Each task includes its calculated score.
    
    Request body:
    {
        "tasks": [
            {
                "title": "Fix login bug",
                "due_date": "2025-11-30",
                "estimated_hours": 3,
                "importance": 8,
                "dependencies": []
            },
            ...
        ],
        "strategy": "smart_balance"  // optional
    }
    
    Response:
    {
        "tasks": [
            {
                "id": 0,
                "title": "Fix login bug",
                "due_date": "2025-11-30",
                "estimated_hours": 3,
                "importance": 8,
                "dependencies": [],
                "priority_score": 85.5,
                "score_components": {
                    "urgency": 90.0,
                    "importance": 80.0,
                    "effort": 75.0,
                    "dependencies": 30.0
                },
                "explanation": "Due very soon (5 days) • High importance rating"
            },
            ...
        ],
        "strategy": "smart_balance",
        "total_tasks": 5
    }
    """
    serializer = TaskAnalyzeRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    tasks = validated_data['tasks']
    strategy = validated_data.get('strategy', 'smart_balance')
    
    # Handle empty task list
    if not tasks:
        return Response(
            {'error': 'No tasks provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialize scorer with strategy
        scorer = TaskScorer(strategy=strategy)
        
        # Score and sort tasks
        scored_tasks = scorer.score_tasks(tasks)
        
        return Response({
            'tasks': scored_tasks,
            'strategy': strategy,
            'total_tasks': len(scored_tasks)
        })
    
    except Exception as e:
        return Response(
            {'error': 'Error processing tasks', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def suggest_tasks(request):
    """
    POST /api/tasks/suggest/
    
    Return the top N tasks the user should work on today,
    with explanations for why each was chosen.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance",  // optional
        "count": 3  // optional, default 3
    }
    
    Response:
    {
        "suggestions": [
            {
                "rank": 1,
                "title": "Fix critical bug",
                "due_date": "2025-11-26",
                "priority_score": 95.5,
                "suggestion_reason": "Rank #1: OVERDUE by 2 days • High importance rating",
                "explanation": "OVERDUE by 2 days • High importance rating",
                ...
            },
            ...
        ],
        "strategy": "smart_balance",
        "requested_count": 3,
        "returned_count": 3
    }
    """
    serializer = SuggestRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    tasks = validated_data['tasks']
    strategy = validated_data.get('strategy', 'smart_balance')
    count = validated_data.get('count', 3)
    
    # Handle empty task list
    if not tasks:
        return Response(
            {'error': 'No tasks provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialize scorer with strategy
        scorer = TaskScorer(strategy=strategy)
        
        # Get top suggestions
        suggestions = scorer.get_top_suggestions(tasks, count)
        
        return Response({
            'suggestions': suggestions,
            'strategy': strategy,
            'requested_count': count,
            'returned_count': len(suggestions)
        })
    
    except Exception as e:
        return Response(
            {'error': 'Error generating suggestions', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )