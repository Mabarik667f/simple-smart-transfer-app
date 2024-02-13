from .utils import main_menu

def get_main_context(request):
    return {'main_menu': main_menu}
