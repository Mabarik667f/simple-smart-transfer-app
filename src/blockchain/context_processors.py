main_menu = [{'title': 'Главная', 'url_name': 'home'},
             {'title': 'Профиль', 'url_name': 'profile'},]


profile_menu = [{'title': 'Перевести', 'url_name': 'transfer'},
                ]

def get_main_context(request):
    return {'main_menu': main_menu, 'profile_menu': profile_menu}

