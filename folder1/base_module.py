# folder1/base_module.py

from browser import document, window, timer
import random

########################################################
#          Базовые функции, глобальные переменные
########################################################

# Глобальные переменные (пример)
player_name = "Игрок"
_card_queue = []
_busy = False

def switch_view(show_id):
    screens = [
        "menu-screen","newgame-screen","achievements-screen","rules-screen",
        "settings-screen","game-screen","aifull-screen","aifull-multi-screen",
        "profile-screen"
    ]
    for s in screens:
        document[s].style.display = "none"
    document[show_id].style.display = "block"

def back_to_menu():
    if "trump-card" in document:
        document["trump-card"].style.display = "none"
    if "trump-card-multi" in document:
        document["trump-card-multi"].style.display = "none"
    if "discard-pile" in document:
        document["discard-pile"].style.display = "none"
        document["discard-pile"].clear()
    if "discard-pile-multi" in document:
        document["discard-pile-multi"].style.display = "none"
        document["discard-pile-multi"].clear()
    switch_view("menu-screen")

def open_screen(name):
    switch_view(name+"-screen")

def rank_index(rank):
    order = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    return order.index(rank) if rank in order else -1

def can_defend(card_def, card_atk, trump_suit):
    rd, sd, jd = card_def
    ra, sa, ja = card_atk
    if jd:
        # Джокер, если у атакующей карты тоже джокер - нельзя бить.
        if ja:
            return False
        return True
    if ja:
        return False

    is_trump_def = (sd == trump_suit)
    is_trump_atk = (sa == trump_suit)

    if is_trump_def and not is_trump_atk:
        return True
    if not is_trump_def and is_trump_atk:
        return False

    if sd == sa:
        return rank_index(rd)>rank_index(ra)
    return False

def draw_until_6(hand, deck):
    while len(hand)<6 and len(deck)>0:
        hand.append(deck.pop(0))
    return hand

def create_deck(only_6plus, with_jokers):
    suits=["♠","♥","♦","♣","⭐","🌙","⚜"]
    ranks_all=[str(n) for n in range(2,11)] + ["J","Q","K","A"]
    if only_6plus:
        ranks_all=[r for r in ranks_all if r not in ["2","3","4","5"]]
    d=[]
    for s in suits:
        for r in ranks_all:
            d.append((r,s,False))
    if with_jokers:
        d.append(("Joker-3","JokerSuit",True))
        d.append(("Joker-4","JokerSuit",True))
    return d

def _old_set_action_message(screen_id, txt):
    # Заменяем "AI[1]" => "Селестия" и т.д.
    if screen_id=="aifull":
        txt=txt.replace("ИИ","Селестия")
    txt=txt.replace("AI[1]","Селестия").replace("AI[2]","Люмин").replace("AI[3]","Итер")
    txt=txt.replace("AI[0]", player_name).replace("ИИ[0]", player_name)
    txt=txt.replace("Игрок",player_name)

    document[screen_id+"-action"].innerHTML=txt

def patched_set_action_message(screen_id, txt):
    global _card_queue, _busy
    _old_set_action_message(screen_id, txt)
    # Добавляем в очередь, чтобы потом "медленно" показалось
    _card_queue.append(('message', screen_id, txt))
    if not _busy:
        _busy = True
        timer.set_timeout(delayed_show_next,2000)

def patched_clear_action(screen_id):
    document[screen_id+"-action"].innerHTML=""

def discard_cards_bito(screen_id, cards):
    if screen_id=="aifull":
        pile_id="discard-pile"
        field_id="aifull-visual-cards"
    else:
        pile_id="discard-pile-multi"
        field_id="aifull-multi-visual-cards"
    if pile_id in document:
        document[field_id].clear()
        pile=document[pile_id]
        pile.clear()
        pile.style.display="flex"
        new_div=document.createElement("div")
        new_div.classList.add("card-back")
        pile.appendChild(new_div)

def delayed_show_next():
    """
    Из очереди берём по одному событию (либо 'card', либо 'message') и показываем
    с задержкой 2 секунды.
    """
    from folder1.base_module import _card_queue, _busy  # пример, когда мы обращаемся к глобалам
    global _card_queue, _busy

    if not _card_queue:
        _busy = False
        return
    _busy = True
    item = _card_queue.pop(0)
    kind = item[0]
    if kind=='card':
        card, parent_id=item[1], item[2]
        cont=document[parent_id]
        new_div=document.createElement("div")
        new_div.classList.add("card-item")
        new_div.style.display="inline-block"
        rank,suit,jk=card
        card_text="Joker" if jk else f"{rank}{suit}"
        new_div.innerHTML=card_text
        cont.appendChild(new_div)
    elif kind=='message':
        scr, txt=item[1], item[2]
        _old_set_action_message(scr, txt)

    timer.set_timeout(delayed_show_next,2000)

def clear_visual_cards(parent_id):
    container = document[parent_id]
    container.clear()

def get_ai_name(ai_idx):
    if ai_idx==1: return "Селестия"
    elif ai_idx==2: return "Люмин"
    elif ai_idx==3: return "Итер"
    return f"AI[{ai_idx}]"

# Прятать логи для красоты
def _hide_text_logs():
    if "aifull-log" in document:
        document["aifull-log"].style.display="none"
    if "aifull-multi-log" in document:
        document["aifull-multi-log"].style.display="none"

_hide_text_logs()

# В самом конце привяжем пару методов к window, чтобы из JS вызывать
window.open_screen = open_screen
window.back_to_menu = back_to_menu
