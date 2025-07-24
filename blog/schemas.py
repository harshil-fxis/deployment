from pydantic import BaseModel
from typing import List, Optional


#user
class UserCreate(BaseModel):
    name: str
    email: str
    country: str
    password: str
    phone: str

class phoneUpdate(BaseModel):
    phone: int

class UserOut(BaseModel):
    name: str
    email: str

class phoneInput(BaseModel):
    id: int
    phone: str
    countryverify: str

class profileInput(BaseModel):
    id: int
    profilePic: str

class OTPVerify(BaseModel):
    id: int
    otp: str

class ProfileEdit(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    phone: str


class UserLogin(BaseModel):
    email: str
    password: str

class alluser(BaseModel):
    id : int
    name: str
    email: str
    password: str
    country: str
    phone: Optional[str] = None
    verified: Optional[str] = None
    countryverify: Optional[str] = None
    profilePic: Optional[str] = None

    class Config:
        from_attributes =True



#owner

class OwnerCreate(BaseModel):
    profilePic: str
    name: str
    email: str
    contact: str
    license: str
    
class CarCreate(BaseModel):   
    brandName: str
    color: str
    fuel: str
    detail: str

class CardCreate(BaseModel):
    cash: Optional[str]
    card_name: Optional[str]
    card_email: Optional[str]
    cardNo: Optional[str]
    expiryDate: Optional[str]
    cvc: Optional[str]
    country: str
    zipCode: int
    
    

class OwnerResponse(CarCreate):
    id: int
    image_urls: List[str]

    class Config:
        from_attributes =True


class CarOut(BaseModel):
    id: int
    carName: str
    brandName: str
    price: int
    seats: int
    mileage: int
    city: str
    maxSpeed: int
    engineOut : int
    advance: str
    feature: str
    brandName: str
    registrationNo: str
    color: str
    fuel: str
    detail: str
    image_urls: List[str]

    class Config:
        from_attributes =True

class OwnerWithCars(BaseModel):
    id: int
    profilePic: str
    name: str
    email: str
    contact: str
    licenseNo: str
    cars: List[CarOut]

    class Config:
        from_attributes =True


def validate_payment(self):
    if self.cash and self.card:
        raise ValueError("Either cash or card must be provided, not both.")
    if not self.cash and not self.card:
        raise ValueError("Either cash or card must be provided.")
    if self.card:
        required_fields = [self.card.name,self.card.cardNo, self.card.country, self.card.zipCode]
        if not all(required_fields):
            raise ValueError("All card fields must be filled.")
