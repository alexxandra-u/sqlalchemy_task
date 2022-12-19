import time

from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import math
from random import randrange

engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)
# engine = create_engine("sqlite://", echo=True, future=True)

Base = declarative_base()
metadata = MetaData()

class Person(Base):
    __tablename__ = 'Person'
    UserID = Column(Integer, name='user_id', primary_key=True)
    Nickname = Column(String)
    Level = Column(Integer)
    HP = Column(Float)
    CurHP = Column(Integer)
    Money = Column(Integer)
    Attack = Column(Integer)
    MagicAttack = Column(Integer)
    XP = Column(Integer)
    Armour = Column(Integer)
    MagicArmour = Column(Integer)
    LocationID = Column(Integer)


class Mobs(Base):
    __tablename__ = 'Mobs'
    MobID = Column(Integer, name='mob_id', primary_key=True)
    HP = Column(Float)
    XP = Column(Integer)
    ReqLevel = Column(Integer)
    AttackType = Column(String)
    Attack = Column(Integer)
    Armour = Column(Integer)
    MagicArmour = Column(Integer)


class Locations(Base):
    __tablename__ = 'Locations'
    LocationID = Column(Integer, name='location_id', primary_key=True)
    XCoord = Column(Float)
    YCoord = Column(Float)
    LocationType = Column(String)


class Items(Base):
    __tablename__ = 'Items'
    ItemID = Column(Integer, name='item_id', primary_key=True)
    Cost = Column(Float)
    CostToSale = Column(Float)
    ItemType = Column(String)
    HP = Column(Float)
    Mana = Column(Integer)
    Attack = Column(Integer)
    MagicAttack = Column(Integer)
    Armour = Column(Integer)
    MagicArmour = Column(Integer)
    ReqLevel = Column(Integer)


class WhereToBuy(Base):
    __tablename__ = "WhereToBuy"
    ItemID = Column(Integer, name='ItemId', primary_key=True)
    City = Column(Integer)


class Belongings(Base):
    __tablename__ = "Belongings"
    UserID = Column(Integer, name='belongings_id', primary_key=True)
    ItemID = Column(Integer)
    Quantity = Column(Integer)
    IsWearing = Column(Boolean)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, future=True, expire_on_commit=False)
session = Session()

#сделали игрока (пока одного)
Sansa = Person(UserID=1, Nickname="Sansa Stark", Level=1, HP=10, CurHP=10, Money=100, Attack=1, MagicAttack=1, XP=100,
                Armour=1, MagicArmour=1, LocationID=1)
session.add(Sansa)

#сделали несколько монстров
mob_1 = Mobs(MobID=1, HP=100, XP=100, ReqLevel=1, AttackType="physical", Attack=1, Armour=1, MagicArmour=0)
mob_2 = Mobs(MobID=2, HP=200, XP=200, ReqLevel=2, AttackType="physical", Attack=2, Armour=2, MagicArmour=0)
mob_3 = Mobs(MobID=3, HP=300, XP=300, ReqLevel=3, AttackType="magical", Attack=3, Armour=0, MagicArmour=3)
session.add(mob_1)
session.add(mob_2)
session.add(mob_3)

#сделали несколько локаций
loc_1 = Locations(LocationID=1, XCoord=0, YCoord=0, LocationType="city")
loc_2 = Locations(LocationID=2, XCoord=0, YCoord=10, LocationType="cave")
loc_3 = Locations(LocationID=3, XCoord=6, YCoord=0, LocationType="cave")
session.add(loc_1)
session.add(loc_2)
session.add(loc_3)

#сделали несколько предметов
item_1 = Items(ItemID=1, Cost=10, CostToSale=10, ItemType="Sword", HP=10, Mana=10, Attack=10, MagicAttack=0, Armour=0, MagicArmour=0, ReqLevel=1)
item_2 = Items(ItemID=2, Cost=20, CostToSale=20, ItemType="Archery", HP=30, Mana=30, Attack=30, MagicAttack=10, Armour=5, MagicArmour=5, ReqLevel=3)
item_3 = Items(ItemID=3, Cost=30, CostToSale=30, ItemType="Blunt", HP=10, Mana=10, Attack=10, MagicAttack=0, Armour=0, MagicArmour=0, ReqLevel=2)
session.add(item_1)
session.add(item_2)
session.add(item_3)

#у нас пока только 1 город, так что купить все можно только там
wtb1 = WhereToBuy(ItemID=1, City=1)
wtb2 = WhereToBuy(ItemID=2, City=1)
wtb3 = WhereToBuy(ItemID=3, City=1)
session.add(wtb1)
session.add(wtb2)
session.add(wtb3)

session.commit()

#напишем несколько функций

def go_to_location(person, location):
    pers_loc = session.query(Locations).filter_by(LocationID = person.LocationID).first()
    x = pers_loc.XCoord
    y = pers_loc.YCoord
    x1 = location.XCoord
    y1 = location.YCoord
    distance = math.sqrt(((x1-x) * (x1-x)) + ((y1-y) * (y1-y)))
    if distance <= 10:
        person.LocationID = location.LocationID
        if location.LocationType == "city":
            person.CurHP = person.HP
        else:
            suitable_monsters = session.query(Mobs).filter_by(ReqLevel=person.Level)
            i = randrange(suitable_monsters.count())
            monster = suitable_monsters[i]
    else:
       print("This location is too far")


def use_item(person, item):
    has_item = session.query(Belongings).filter_by(UserID=person.UserID, ItemID=item.ItemID).count()
    if has_item > 0:
        person.CurHP += item.HP
        person.Attack = item.Attack
        person.MagicAttack = item.MagicAttack
        elem = session.query(Belongings).filter_by(UserID=person.UserID, ItemID=item.ItemID).first()
        elem.IsWearing = True
    else:
        print("You don't have such an item")

def buy_item(person, item):
    pers_loc = session.query(Locations).filter_by(LocationID=person.LocationID).first()
    where_can_buy = session.query(WhereToBuy).filter_by(ItemID=item.ItemID).first()
    if person.Money >= item.CostToSale and pers_loc.LocationType == 'city' and where_can_buy.City == person.LocationID:
        has_item = session.query(Belongings).filter_by(UserID=person.UserID, ItemID=item.ItemID)
        if has_item.count() > 0:
            has_item.first().Quantity += 1
        else:
            belonging = Belongings(UserID=person.UserID, ItemID=item.ItemID, Quantity=1, IsWearing=False)
            session.add(belonging)
            session.commit()
        print("Item is successfully bought")
    else:
        print("You don't have enough money or this item can't be bought in the place where you are")

def create_person():
    user_id = session.query(Person).count() + 1
    nick = input("Введите nickname для вашего персонажа: ")
    new_player = Person(UserID=user_id, Nickname=nick, Level=1, HP=10, CurHP=10, Money=100, Attack=1, MagicAttack=1, XP=100,
                Armour=1, MagicArmour=1, LocationID=1)
    session.add(new_player)
    print("Welcome our new player "+ nick)


#проверим можем ли мы отправить персонажа в локацию
go_to_location(Sansa, loc_2)
print("Sansa's location ID is now: ", Sansa.LocationID)
# ура, получилось. теперь вернемся обратно
go_to_location(Sansa, loc_1)

#проверим можем ли использовать Item, которого у нас нет
use_item(Sansa, item_1)

#опа, не смогли. теперь купим этот item
buy_item(Sansa, item_1)
use_item(Sansa, item_1)

#попробуем создать нового персонажа (нужно будет ввести nickname из консоли)
create_person()
