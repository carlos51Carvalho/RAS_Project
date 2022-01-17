import time
from rasbet.models import *
from rasbet import db
from datetime import datetime


def stateChanger():
    events = Event.query.all()
    for e in events:
        if e.start_date < datetime.now() and e.state == "0":
            e.state = "1"
        elif e.end_date < datetime.now():
            odds = Odd.query.filter_by(event_id=e.id).all()
            betodds = []

            for o in odds:
                betodds += BetOdd.query.filter_by(odd_id=o.id).all()

            status = ""
            for bo in betodds:
                bet = Bet.query.filter_by(id=bo.bet_id).first()

                if e.state == "1":
                    change = True
                    win = True

                    print(bet)

                    this_bet_odds = BetOdd.query.filter_by(bet_id=bet.id).all()
                    
                    this_odds = []
                    for tbo in this_bet_odds:
                        this_odds += Odd.query.filter_by(id=tbo.odd_id).all()
                    for to in this_odds:
                        if to.event_id != e.id:
                            if Event.query.filter_by(id=to.event_id).first().state != "2":
                                change = False
                        if to.result != None:
                            if to.result == False:
                                win = False

                    if change and win:
                        bet.state = "Ganha"

                        mov = Movement(value=bet.value*bet.odd,
                                       type="Aposta Ganha",
                                       date=datetime.now())
                        db.session.add(mov)

                        wallet = Wallet.query.filter_by(
                            user_id=bet.user_id, currency_id=bet.currency_id).first()

                        wm = WalletMovement(movement_id=mov.id,
                                            wallet_id=wallet.id)
                        db.session.add(wm)

                        wallet.balance += bet.value * bet.odd
                    elif change and not win:
                        bet.state = "Perdida"
                    status = "2"
                elif e.state == "3":
                    bet.state = "Cancelada"

                    mov = Movement(value=bet.value,
                                   type="Aposta Cancelada",
                                   date=datetime.now())
                    db.session.add(mov)

                    wallet = Wallet.query.filter_by(
                        user_id=bet.user_id, currency_id=bet.currency_id).first()

                    wm = WalletMovement(movement_id=mov.id,
                                        wallet_id=wallet.id)
                    db.session.add(wm)

                    wallet.balance += bet.value

                    status = "4"
            e.state = status

    db.session.commit()


def worker():
    while True:
        time.sleep(10)
        stateChanger()
