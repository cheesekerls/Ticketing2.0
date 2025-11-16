# utils.py (or at the top of views.py)
from .models import Counter

def get_current_counter(request):
    counter_id = request.session.get('counter_id')
    if not counter_id:
        return None
    try:
        return Counter.objects.get(counter_id=counter_id)
    except Counter.DoesNotExist:
        return None
