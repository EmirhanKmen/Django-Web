"""
Sahaflar Platformu — Core Context Processors
Provides global template context variables.
"""
from django.conf import settings


def platform_context(request):
    """Inject platform-wide variables into all templates."""
    return {
        'PLATFORM_NAME': 'SAHAF',
        'PLATFORM_FULL_NAME': 'Sahaflar icin anket ve envanter platformu',
        'PLATFORM_VERSION': '1.0.0',
        'DEBUG': settings.DEBUG,
    }
