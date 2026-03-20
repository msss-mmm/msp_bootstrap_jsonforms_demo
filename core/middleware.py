class XForwardedPrefixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Nginx usually sends X-Forwarded-Prefix if configured
        prefix = request.META.get('HTTP_X_FORWARDED_PREFIX')
        if prefix:
            # SCRIPT_NAME is what Django uses to determine the "base" of the application
            # If the proxy is at /mes/, and it passes X-Forwarded-Prefix: /mes
            # then SCRIPT_NAME should be /mes
            request.environ['SCRIPT_NAME'] = prefix

            # Also adjust the path_info if the prefix is already in it
            # (depending on how nginx is configured to proxy_pass)
            path = request.path_info
            if path.startswith(prefix):
                request.path_info = path[len(prefix):]

        return self.get_response(request)
