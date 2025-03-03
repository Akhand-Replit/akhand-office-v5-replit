from .admin import render_admin_dashboard
from .company import render_company_dashboard
from .employee import render_employee_dashboard
from .messages import render_messages
from .tasks import render_tasks

__all__ = [
    'render_admin_dashboard',
    'render_company_dashboard',
    'render_employee_dashboard',
    'render_messages',
    'render_tasks'
]
