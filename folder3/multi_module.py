# folder3/multi_module.py

from browser import document, timer
import random

from folder1.base_module import (
    player_name, patched_set_action_message, patched_clear_action,
    can_defend, rank_index, draw_until_6, create_deck,
    discard_cards_bito, delayed_show_next, clear_visual_cards,
    switch_view, back_to_menu, get_ai_name, _card_queue, _busy
)

n_players=3
hands=[]
deck_multi=[]
trump_multi=""
cur_attacker=0
log_multi=[]
allow_click_multi=False
eliminated=[]
ranks_done=0
total_players_count=0

def determine_first_attacker_multi():
    best=None
    best_idx=None
    for i,hand_ in enumerate(hands):
        if eliminated[i]:
            continue
        trump_cards=[c for c in hand_ if c[1]==trump_multi]
        if trump_cards:
            rmins=[rank_index(x[0]) for x in trump_cards]
            m=min(rmins)
        else:
            m=999
        if best is None or m<best:
            best=m
            best_idx=i
    if best_idx is None or best==999:
        return 0
    return best_idx

def game_over_multi(winner, winner_idx):
    global allow_click_multi,hands,ranks_done
    place=ranks_done+1
    ranks_done+=1
    eliminated[winner_idx]=True
    if winner=="player":
        if place==1:
            patched_set_action_message("aifull-multi",f"ПОБЕДИТЕЛЬ: {player_name.upper()} (1 место)!")
            for i in range(len(hands)):
                hands[i]=[]
            allow_click_multi=False
        else:
            patched_set_action_message("aifull-multi",f"{player_name} занял {place} место!")
            for i in range(len(hands)):
                hands[i]=[]
            allow_click_multi=False
    else:
        nm=get_ai_name(winner_idx)
        patched_set_action_message("aifull-multi",f"{nm} занял {place} место!")
        hands[winner_idx]=[]
        if place==total_players_count-0:
            allow_click_multi=False
        else:
            pass
    document["aifull-multi-visual-cards"].clear()

def check_win_conditions_multi():
    global n_players,ranks_done
    arr=[i for i,h in enumerate(hands) if len(h)>0 and not eliminated[i]]
    if len(arr)==1:
        last_idx=arr[0]
        place=ranks_done+1
        ranks_done+=1
        if last_idx==0:
            patched_set_action_message("aifull-multi",f"{player_name} остался последним, он проиграл!")
            for i in range(n_players):
                hands[i]=[]
            allow_click_multi=False
        else:
            nm=get_ai_name(last_idx)
            patched_set_action_message("aifull-multi",f"{nm} проиграл последним!")
            for i in range(n_players):
                hands[i]=[]
            allow_click_multi=False

def start_aifull_multi(only_6plus, with_jokers, total):
    start_aifull_multi_game(only_6plus, with_jokers, total)

def start_aifull_multi_game(only_6plus,with_jokers,total_players):
    global n_players,hands,deck_multi,trump_multi,cur_attacker,log_multi,allow_click_multi
    global eliminated,ranks_done,total_players_count

    n_players=total_players
    total_players_count=n_players
    eliminated=[False]*n_players
    ranks_done=0

    deck_multi=create_deck(only_6plus,with_jokers)
    random.shuffle(deck_multi)
    hands=[]
    off=0
    for i in range(n_players):
        h=deck_multi[off:off+6]
        off+=6
        hands.append(h)
    deck_multi=deck_multi[off:]

    suits=["♠","♥","♦","♣","⭐","🌙","⚜"]
    trump_multi=random.choice(suits)
    cur_attacker=determine_first_attacker_multi()
    log_multi=[f"Начинаем (1чел + {n_players-1} ИИ)."]

    document["trump-card-multi"].innerHTML=f"<div style='font-size:1.5rem;'>{trump_multi}</div>"
    document["trump-card-multi"].style.display="flex"
    clear_visual_cards("aifull-multi-visual-cards")
    document["discard-pile-multi"].clear()
    document["discard-pile-multi"].style.display="none"
    allow_click_multi=(cur_attacker==0)

    if cur_attacker==0:
        patched_set_action_message("aifull-multi", f"{player_name} ходит первым!")
    else:
        patched_set_action_message("aifull-multi", f"{get_ai_name(cur_attacker)} ходит первым!")
        timer.set_timeout(lambda: ai_multi_attack(cur_attacker),2000)

    update_aifull_multi_ui()
    switch_view("aifull-multi-screen")

def update_aifull_multi_ui():
    global log_multi,cur_attacker,hands
    document["aifull-multi-log"].innerHTML="<pre>"+"\n".join(log_multi)+"</pre>"
    turn_text=(f"{get_ai_name(cur_attacker)}" if cur_attacker!=0 else player_name)
    document["multi-turn"].textContent=turn_text
    ul=document["user-multi-cards"]
    ul.clear()
    for i,c in enumerate(hands[0]):
        li=document.createElement("li")
        li.classList.add("card-item")
        li.innerHTML=str(c)
        def on_click(ev, idx=i):
            handle_multi_card_click(idx)
        li.bind("click", on_click)
        ul.appendChild(li)
    check_win_conditions_multi()

def handle_multi_card_click(idx):
    global allow_click_multi,hands,cur_attacker,deck_multi,log_multi,trump_multi,n_players,eliminated
    if not allow_click_multi:return
    if idx<0 or idx>=len(hands[0]):return
    patched_clear_action("aifull-multi")
    defender=(cur_attacker+1)%n_players
    while eliminated[defender] and defender!=cur_attacker:
        defender=(defender+1)%n_players
    selected_card=hands[0][idx]
    patched_set_action_message("aifull-multi",f"{player_name} атакует {get_ai_name(defender)}!")
    _card_queue.append(('card', selected_card, "aifull-multi-visual-cards"))
    if not _busy:
        delayed_show_next()
    hands[0].pop(idx)
    def_card=None
    def_idx=None
    for i,c in enumerate(hands[defender]):
        if can_defend(c,selected_card,trump_multi):
            def_card=c
            def_idx=i
            break
    if def_card:
        _card_queue.append(('card', def_card, "aifull-multi-visual-cards"))
        if not _busy:
            delayed_show_next()
        log_multi.append(f"{get_ai_name(defender)} отбился!")
        cur_attacker=defender
        hands[defender].pop(def_idx)
        patched_set_action_message("aifull-multi",f"{get_ai_name(defender)} отбился!")
        discard_cards_bito("aifull-multi",[selected_card,def_card])
        do_multi_draw()
        patched_set_action_message("aifull-multi", f"{get_ai_name(cur_attacker)} атакует!")
        timer.set_timeout(lambda: ai_multi_attack(cur_attacker),2000)
    else:
        log_multi.append(f"{get_ai_name(defender)} не отбился, берёт карту.")
        patched_set_action_message("aifull-multi", f"{get_ai_name(defender)} не отбился, берёт карты")
        document["aifull-multi-visual-cards"].clear()
        hands[defender].append(selected_card)
        do_multi_draw()
        nxt=(defender+1)%n_players
        while eliminated[nxt] and nxt!=defender:
            nxt=(nxt+1)%n_players
        cur_attacker=nxt
        if cur_attacker==0:
            allow_click_multi=True
            log_multi.append(f"{player_name} ходит (после неудачной защиты {get_ai_name(defender)}).")
            patched_set_action_message("aifull-multi", f"Ход переходит к {player_name}. {player_name} атакует!")
        else:
            patched_set_action_message("aifull-multi", f"Ход переходит к {get_ai_name(cur_attacker)}. {get_ai_name(cur_attacker)} атакует!")
            timer.set_timeout(lambda: ai_multi_attack(cur_attacker),2000)
    update_aifull_multi_ui()

def ai_multi_attack(att_idx):
    global hands,deck_multi,log_multi,allow_click_multi,cur_attacker,n_players,trump_multi,eliminated
    if eliminated[att_idx]:return
    if len(hands[att_idx])==0:return
    df=(att_idx+1)%n_players
    while eliminated[df] and df!=att_idx:
        df=(df+1)%n_players
    patched_set_action_message("aifull-multi", f"{get_ai_name(att_idx)} атакует {get_ai_name(df)}!")
    atk_card=hands[att_idx][0]
    _card_queue.append(('card', atk_card, "aifull-multi-visual-cards"))
    if not _busy:
        delayed_show_next()

    if df==0:
        allow_click_multi=True
    else:
        def_i=None
        for i,c in enumerate(hands[df]):
            if can_defend(c,atk_card,trump_multi):
                def_i=i
                break
        if def_i is not None:
            def_card=hands[df][def_i]
            _card_queue.append(('card', def_card, "aifull-multi-visual-cards"))
            if not _busy:
                delayed_show_next()
            log_multi.append(f"{get_ai_name(df)} отбился!")
            cur_attacker=df
            hands[df].pop(def_i)
            hands[att_idx].pop(0)
            patched_set_action_message("aifull-multi", f"{get_ai_name(df)} отбился!")
            discard_cards_bito("aifull-multi",[atk_card,def_card])
        else:
            log_multi.append(f"{get_ai_name(df)} не отбился, берёт карту.")
            patched_set_action_message("aifull-multi", f"{get_ai_name(df)} не отбился, берёт карты")
            document["aifull-multi-visual-cards"].clear()
            hands[df].append(atk_card)
            hands[att_idx].pop(0)
            nxt=(df+1)%n_players
            while eliminated[nxt] and nxt!=df:
                nxt=(nxt+1)%n_players
            cur_attacker=nxt

        do_multi_draw()
        if cur_attacker!=df:
            if len(hands[cur_attacker])>0 and not eliminated[cur_attacker]:
                patched_set_action_message("aifull-multi", f"Ход переходит к {get_ai_name(cur_attacker)}. {get_ai_name(cur_attacker)} атакует!")
                timer.set_timeout(lambda: ai_multi_attack(cur_attacker),2000)
        else:
            if cur_attacker==0:
                allow_click_multi=True
                log_multi.append("Теперь ваш ход.")
                patched_set_action_message("aifull-multi", f"Ход переходит к {player_name}. Ваш ход!")
            else:
                patched_set_action_message("aifull-multi",f"Ход переходит к {get_ai_name(cur_attacker)}. {get_ai_name(cur_attacker)} атакует!")
                timer.set_timeout(lambda: ai_multi_attack(cur_attacker),2000)
    update_aifull_multi_ui()

def do_multi_draw():
    global hands,deck_multi,cur_attacker,n_players,eliminated
    order=[cur_attacker]
    for i in range(n_players):
        if i!=cur_attacker and not eliminated[i]:
            order.append(i)
    for idx in order:
        hands[idx]=draw_until_6(hands[idx],deck_multi)

def restart_aifull_multi():
    jokers_checked=document["cb_jokers"].checked
    sixplus_checked=document["cb_6plus"].checked
    ai_str=document["ai_players_count"].value
    try:
        ai_num=int(ai_str)
    except:
        ai_num=3
    if ai_num<3:ai_num=3
    if ai_num>4:ai_num=4
    start_aifull_multi_game(sixplus_checked,jokers_checked,ai_num)

window.restart_aifull_multi = restart_aifull_multi
