from .database import Base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer,primary_key = True, index = True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    country = Column(String)
    password = Column(String)
    phone = Column(String, nullable=True)
    countryverify = Column(String, nullable=True)
    verified = Column(String, default="False")
    profilePic = Column(String, nullable=True)


class Owner(Base):
    __tablename__ = 'owners'

    id = Column(Integer,primary_key = True, index = True)
    profilePic = Column(String)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    contact = Column(String, nullable=True)
    licenseNo = Column(String)

    card = relationship("Card", back_populates="owner", uselist=False)
    cars = relationship("Car", back_populates="owner")
    

class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer,primary_key = True, index = True)
    owner_id = Column(Integer,ForeignKey("owners.id"))
    carName = Column(String)
    price = Column(Integer)
    seats = Column(Integer)
    mileage = Column(Integer)
    city = Column(String)
    maxSpeed = Column(Integer)
    engineOut = Column(Integer)
    advance = Column(String)
    feature = Column(String)
    brandName = Column(String)
    registrationNo = Column(String)
    color = Column(String)
    fuel = Column(String)
    detail = Column(String)
    image_urls = Column(JSON)

    owner = relationship("Owner", back_populates="cars")



class Card(Base):
    __tablename__ = 'cards'
    card_id = Column(Integer,primary_key=True,index=True)
    cash = Column(String, nullable=True)
    card_name = Column(String, nullable=True)
    card_email = Column(String, nullable=True)
    cardNo = Column(String, nullable=True)
    expiryDate = Column(String, nullable=True)
    cvc = Column(String, nullable=True)
    country = Column(String, nullable=True)
    zipCode = Column(Integer, nullable=True)

    owner_id = Column(Integer,ForeignKey("owners.id"))
    owner = relationship("Owner", back_populates="card")
    
    
    
    