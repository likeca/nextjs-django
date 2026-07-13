from .env_vars import env

STATICFILES_FINDERS = (                                 # For Django-Compressor
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter'
]
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
COMPRESS_JS_FILTERS = [     # Only compress javascript in production
    'compressor.filters.jsmin.JSMinFilter'
]

COMPRESS_OFFLINE_CONTEXT = {
    'RECAPTCHA_PUBLIC_KEY': env('RECAPTCHA_SITE_KEY'),
}
