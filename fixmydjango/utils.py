import os


def get_templates_config(template_set, BASE_DIR, AVAILABLE_TEMPLATE_SETS):
    assert (
        template_set in AVAILABLE_TEMPLATE_SETS
    ), f"The template set '{template_set}' is not configured.'"
    return [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates', template_set)],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ]
            },
        }
    ]
