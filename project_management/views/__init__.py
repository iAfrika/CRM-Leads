from .project_views import (
    project_list,
    project_detail,
    project_create,
    project_update,
    project_delete,
    project_finances,
)

from .dashboard_views import (
    project_dashboard,
    project_analytics,
)

from .document_views import (
    document_create,
    document_update,
    document_delete,
    document_download,
)

from .milestone_views import (
    milestone_create,
    milestone_update,
    milestone_delete,
    milestone_toggle,
    milestone_update_percentage,
)

from .note_views import (
    note_create,
    note_update,
    note_delete,
    note_toggle_pin,
)

from .finance_views import (
    finance_create,
    finance_update,
    finance_delete,
    finance_get,
) 