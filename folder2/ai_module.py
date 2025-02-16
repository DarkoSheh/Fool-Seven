# folder2/ai_module.py

from browser import document, timer
import random

# Импортируем то, что написано в base_module
from folder1.base_module import (
    player_name, patched_set_action_message, patched_clear_action,
    can_defend, rank_index, draw_until_6, create_deck,
    discard_cards_bito, delayed_show_next, clear_visual_cards,
    switch_view, back_to_menu, get_ai_name, _card_queue, _busy,
)

# Глобальные переменные, относящиеся к режиму 2 игроков
deck = []
AI_cards = []
user_cards = []
trump_suit = ""
current_attacker = "AI"
log_lines = []
allow_user_click = False

def determine_first_attacker_2p():
    global user_cards, AI_cards, trump_suit
    player_trumps = [card for card in user_cards if card[1] == trump_suit]
    ai_trumps = [card for card in AI_cards if card[1] == trump_suit]
    if player_trumps or ai_trumps:
        player_min = min([rank_index(card[0]) for card in player_trumps]) if player_trumps else None
        ai_min = min([rank_index(card[0]) for card in ai_trumps]) if ai_trumps else None
        if player_min is not None and ai_min is not None:
            if player_min < ai_min:
                return "player"
            else:
                return "AI"
        elif player_min is not None:
            return "player"
        elif ai_min is not None:
            return "AI"
    return "player"

def game_over_2p(winner):
    global user_cards, AI_cards, allow_user_click
    if winner=="player":
       patched_set_action_message("aifull", f"ПОБЕДИТЕЛЬ: {player_name.upper()}!")
    else:
       patched_set_action_message("aifull", "ПОБЕДИТЕЛЬ: СЕЛЕСТИЯ!")
    user_cards = []
    AI_cards = []
    document["aifull-visual-cards"].clear()
    allow_user_click = False

def check_win_conditions_2p():
    if len(user_cards) == 0:
         game_over_2p("player")
    elif len(AI_cards) == 0:
         game_over_2p("AI")

def start_aifull_game(only_6plus, with_jokers):
    global deck, AI_cards, user_cards, trump_suit, current_attacker, log_lines, allow_user_click
    deck = create_deck(only_6plus, with_jokers)
    random.shuffle(deck)
    AI_cards = deck[:6]
    user_cards = deck[6:12]
    del deck[:12]
    suits = ["♠","♥","♦","♣","⭐","🌙","⚜"]
    trump_suit = random.choice(suits)
    current_attacker = determine_first_attacker_2p()
    log_lines = [f"Начинаем партию (2 игрока)."]
    allow_user_click = False

    document["trump-card"].innerHTML = f"<div style='font-size:1.5rem;'>{trump_suit}</div>"
    document["trump-card"].style.display = "flex"
    clear_visual_cards("aifull-visual-cards")
    document["discard-pile"].clear()
    document["discard-pile"].style.display = "none"

    if current_attacker == "player":
        patched_set_action_message("aifull", f"{player_name} ходит первым!")
        allow_user_click = True
    else:
        patched_set_action_message("aifull", "Селестия ходит первым!")
        timer.set_timeout(ai_attack, 2000)

    switch_view("aifull-screen")
    update_aifull_ui()

def ai_attack():
    global AI_cards, allow_user_click
    if len(AI_cards)==0:
        return
    patched_set_action_message("aifull", "Селестия атакует Игрока!")
    atk_card = AI_cards[0]
    # Добавляем в очередь "визуальное отображение карты"
    _card_queue.append(('card', atk_card, "aifull-visual-cards"))
    # Если Brython ещё не занят, запускаем цепочку
    from folder1.base_module import _busy
    if not _busy:
        delayed_show_next()
    allow_user_click = True

def update_aifull_ui():
    document["aifull-log"].innerHTML = "<pre>" + "\n".join(log_lines) + "</pre>"
    turn_text = "Селестия" if current_attacker=="AI" else player_name
    document["current-turn"].textContent = turn_text

    ul = document["user-cards-list"]
    ul.clear()
    for i, c in enumerate(user_cards):
        li = document.createElement("li")
        li.classList.add("card-item")
        li.innerHTML = str(c)
        def on_click(ev, idx=i):
            handle_card_click(idx)
        li.bind("click", on_click)
        ul.appendChild(li)

    check_win_conditions_2p()

def handle_card_click(idx):
    global deck, AI_cards, user_cards, trump_suit, current_attacker, allow_user_click
    if not allow_user_click:
        return
    if idx<0 or idx>=len(user_cards):
        return
    c = user_cards[idx]
    if current_attacker=="AI":
        patched_clear_action("aifull")
        patched_set_action_message("aifull", f"{player_name} отбивается...")
        atk_card = AI_cards[0]
        _card_queue.append(('card', c, "aifull-visual-cards"))
        if not _busy:
            delayed_show_next()
        # проверяем защиту
        if can_defend(c, atk_card, trump_suit):
            patched_set_action_message("aifull", f"{player_name} отбился!")
            discard_cards_bito("aifull",[c,atk_card])
            AI_cards.pop(0)
            user_cards.pop(idx)
            current_attacker="player"
            patched_set_action_message("aifull", f"{player_name} атакует Селестию!")
        else:
            patched_set_action_message("aifull", f"{player_name} не отбился, берём карты")
            document["aifull-visual-cards"].clear()
            user_cards.append(atk_card)
            AI_cards.pop(0)
            patched_set_action_message("aifull", "Ход переходит к Селестии. Селестия атакует Игрока!")
        allow_user_click=False
        AI_cards=draw_until_6(AI_cards,deck)
        user_cards=draw_until_6(user_cards,deck)
        if current_attacker=="AI":
            timer.set_timeout(ai_attack,2000)
        else:
            allow_user_click=True
        update_aifull_ui()
    else:
        patched_clear_action("aifull")
        patched_set_action_message("aifull", f"{player_name} атакует Селестию!")
        _card_queue.append(('card', c, "aifull-visual-cards"))
        if not _busy:
            delayed_show_next()
        user_cards.pop(idx)
        def_idx=None
        for i,aicard in enumerate(AI_cards):
            if can_defend(aicard,c,trump_suit):
                def_idx=i
                break
        if def_idx is not None:
            def_card=AI_cards[def_idx]
            patched_set_action_message("aifull","Селестия отбивается...")
            _card_queue.append(('card', def_card, "aifull-visual-cards"))
            if not _busy:
                delayed_show_next()
            patched_set_action_message("aifull","Селестия отбился!")
            discard_cards_bito("aifull",[c,def_card])
            AI_cards.pop(def_idx)
            current_attacker="AI"
            allow_user_click=False
            patched_set_action_message("aifull","Селестия атакует Игрока!")
            timer.set_timeout(ai_attack,2000)
        else:
            patched_set_action_message("aifull","Селестия не отбился, берёт карты")
            document["aifull-visual-cards"].clear()
            AI_cards.append(c)
            patched_set_action_message("aifull","Ход переходит к Игроку. Игрок атакует Селестию!")
        AI_cards=draw_until_6(AI_cards,deck)
        user_cards=draw_until_6(user_cards,deck)
        update_aifull_ui()

def restart_aifull():
    jokers_checked=document["cb_jokers"].checked
    sixplus_checked=document["cb_6plus"].checked
    start_aifull_game(sixplus_checked,jokers_checked)

# Привязываем к window, чтобы HTML мог вызывать
window.restart_aifull = restart_aifull
