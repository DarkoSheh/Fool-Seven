# folder4/main_module.py

from browser import document, window

# Импортируем базовые вещи
from folder1 import base_module
# чтобы не путаться, импортируем целиком base_module — так мы можем явно обращаться 
# к base_module.player_name и быть уверенными, что меняем ту же переменную.

from folder1.base_module import (
    switch_view, open_screen, back_to_menu,
    patched_set_action_message, patched_clear_action,
    create_deck, rank_index
)

# Импортируем функции из модуля AI (2 игрока)
from folder2.ai_module import (
    start_aifull_game, restart_aifull
)

# Импортируем функции из модуля для нескольких ИИ (3-4 игрока)
from folder3.multi_module import (
    start_aifull_multi, restart_aifull_multi
)

########################################################
#       Основные функции управления (init, start_new_game, ...)
########################################################

def on_game_type_change(ev):
    check_game_type()

 radio_list = document.select("[name='game_type']")
    chosen = "ai"  # значение по умолчанию
    for r in radio_list:
        if r.checked:
            chosen = r.value
            break

    ai_block = document["ai-count-block"]
    multi_block = document["multi-count-block"]

    if chosen == "ai":
        # Показать блок ИИ-игроков
        ai_block.style.display = "block"
        # Спрятать мультиплеерный блок
        multi_block.style.display = "none"
    else:
        ai_block.style.display = "none"
        multi_block.style.display = "block"


def on_game_type_change(ev):
    """
    Вызывается при переключении радиокнопки
    """
    check_game_type()


def init():
    """
    Привязка обработчика к каждой радиокнопке
    + первичная проверка (чтобы при загрузке уже всё верно отображалось).
    """
    # Ставим обработчик "on_game_type_change" на каждую радиокнопку name='game_type'
    for r in document.select("[name='game_type']"):
        r.bind("change", on_game_type_change)

    # Сделаем первичную настройку отображения
    check_game_type()


# Вызываем init(), чтобы всё заработало после загрузки
init()


def save_player_name():
    # Меняем player_name в самом base_module
    inp = document["player_name_input"].value
    if inp.strip():
        base_module.player_name = inp.strip()
    back_to_menu()

window.save_player_name = save_player_name

def start_new_game():
    mode_value = document["select_mode"].value
    jokers_checked = document["cb_jokers"].checked
    sixplus_checked = document["cb_6plus"].checked

    radio_list = document.select("[name='game_type']")
    game_type = "ai"
    for r in radio_list:
        if r.checked:
            game_type = r.value
            break

    if game_type == "ai":
        ai_count_str = document["ai_players_count"].value
        try:
            ai_count = int(ai_count_str)
        except:
            ai_count = 2
        if ai_count < 2:
            ai_count = 2
        if ai_count > 4:
            ai_count = 4

        # Запуск игры с ИИ
        if ai_count == 2:
            start_aifull_game(sixplus_checked, jokers_checked)
        else:
            start_aifull_multi(sixplus_checked, jokers_checked, ai_count)

    else:
        # Мультиплеер (просто показываем экран "game-screen", 
        #  как было в исходном коде)
        multi_count_str = document["multi_players_count"].value
        try:
            multi_count = int(multi_count_str)
        except:
            multi_count = 4
        if multi_count < 2:
            multi_count = 2
        if multi_count > 10:
            multi_count = 10

        rlist = document.select("[name='room_type']")
        rt = "link"
        for rr in rlist:
            if rr.checked:
                rt = rr.value
                break

        document["chosen_mode"].textContent = mode_value
        document["chosen_jokers"].textContent = "Да" if jokers_checked else "Нет"
        document["chosen_6plus"].textContent = "Да" if sixplus_checked else "Нет"
        document["chosen_players"].textContent = str(multi_count)
        document["chosen_type"].textContent = "Мультиплеер"
        if rt == "link":
            rtxt = "По ссылке"
        else:
            rtxt = "Открытая"
        document["chosen_room"].textContent = rtxt

        switch_view("game-screen")
            pass

from browser import window
window.open_screen = open_screen
window.back_to_menu = back_to_menu
window.restart_aifull = restart_aifull
window.restart_aifull_multi = restart_aifull_multi
window.save_player_name = save_player_name
window.start_new_game = start_new_game
