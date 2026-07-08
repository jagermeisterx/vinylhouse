from django.contrib.auth.decorators import user_passes_test


def staff_required(view_func):
    decorated_view = user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url="login")
    return decorated_view(view_func)
