from django.conf import settings

from apps.catalog.cart import CART_RELATED_SESSION_KEYS, CART_SKIP_RELOAD_CLEAR_SESSION_KEY, clear_cart


class ClearCartOnReloadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.should_clear_cart(request):
            clear_cart(request)
        return self.get_response(request)

    def should_clear_cart(self, request):
        if request.method != "GET":
            return False

        if not any(key in request.session for key in CART_RELATED_SESSION_KEYS):
            return False

        if request.session.pop(CART_SKIP_RELOAD_CLEAR_SESSION_KEY, False):
            request.session.modified = True
            return False

        if self.is_non_public_path(request.path_info):
            return False

        sec_fetch_dest = request.headers.get("Sec-Fetch-Dest")
        if sec_fetch_dest and sec_fetch_dest != "document":
            return False

        accept = request.headers.get("Accept", "")
        if accept and "text/html" not in accept:
            return False

        cache_control = request.headers.get("Cache-Control", "").lower()
        pragma = request.headers.get("Pragma", "").lower()
        return (
            "max-age=0" in cache_control
            or "no-cache" in cache_control
            or "no-cache" in pragma
        )

    def is_non_public_path(self, path):
        excluded_prefixes = [
            settings.STATIC_URL,
            settings.MEDIA_URL,
            f"/{settings.ADMIN_URL.strip('/')}/",
            "/django-admin/",
        ]
        return any(path.startswith(prefix) for prefix in excluded_prefixes if prefix)
