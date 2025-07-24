import uuid
from fastapi import FastAPI, status, Response, HTTPException, Depends, File, Form, UploadFile, APIRouter
import shutil, os, json
from fastapi.responses import JSONResponse
from.import schemas, models, database
from .database import engine, sessionLocal
from sqlalchemy.orm import Session
from typing import List,Optional
from .hashing import Hash
from passlib.context import CryptContext
from random import randint
from .otp_store import otp_memory
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from blog.database import get_db
from blog.auth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import time

app = FastAPI()
models.Base.metadata.create_all(engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
router = APIRouter()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


users_db = {}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# user

@app.post('/signup',tags=['user'])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400,detail="Email already registered")

    # hashed_pwd = pwd_context.hash(user.password)
    # new_user = models.User(name=user.name,email=user.email,country=user.country,password=Hash.bcrypt(user.password))
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "userId": new_user.id,"userName": new_user.name,"userEmail": new_user.email,"userPhone":new_user.phone}


@app.post('/phone',tags=['user'])
def phone(data: schemas.phoneInput, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == data.id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    user.phone = data.phone
    user.countryverify = data.countryverify
    db.commit()
    otp = str(randint(1000,9999))
    otp_memory[data.id] = otp
    print(f"OTP for {data.id} is {otp}")
    return {"message": "otp sent","user phone number": user.phone,"userCountry": user.countryverify}

@app.post('/profilePic',tags=['user'])
def profilePic(id : int = File(...),profilePic: UploadFile = File(...), db: Session = Depends(get_db)):
    
    save_dir = "uploads"
    os.makedirs(save_dir,exist_ok=True)
    file_location = f"{save_dir}/{profilePic.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(profilePic.file, buffer)

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    user.profilePic = profilePic.filename
    db.commit()
    return {"message": "add profilePic","ProfilePic": user.profilePic}


@app.put('/editProfile',tags=['user'])
def edit(info: schemas.ProfileEdit, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == info.id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    user.name = info.name +" " + info.surname
    user.email = info.email
    user.phone = info.phone
    db.commit()
    return {"message": "profile edited successful"}


@app.post('/login',tags=['user'])
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == data.email).first()
    if not db_user or db_user.password != data.password:
        raise HTTPException(status_code=400,detail="Invalid email or password")
    token = create_access_token({"sub": db_user.email})
    otp = str(randint(1000,9999))
    otp_memory[db_user.phone] = {"otp":otp,"timestamp": time.time()}
    print(f"OTP for {db_user.phone} is {otp}")
    return {"message": "Login successful","access_token":token, "token_type": "bearer", "user": db_user.id,"userName": db_user.name,"userEmail": db_user.email,"userContry":db_user.countryverify,"profilePic":db_user.profilePic,"phone":db_user.phone,"otp":otp}

@app.post("/verify-otp")
def verify_otp(phone: str = Form(...), otp: str = Form(...)):
    
    if phone not in otp_memory:
        raise HTTPException(status_code=404, detail="OTP not found")
    stored_data = otp_memory[phone]
    stored_otp = stored_data['otp']
    timestamp = stored_data['timestamp']
    current_time = time.time()
    
    if current_time - timestamp > 60:
        # del otp_memory[phone]
        raise HTTPException(status_code=400, detail="otp expired")
    
    if otp == stored_data["otp"]:
        del otp_memory[phone]
        return {"message":"OTP verified"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
@app.post("/reset-otp")
def reset_otp(phone: str = Form(...)):
    
    if phone not in otp_memory:
        raise HTTPException(status_code=404, detail="OTP not found")
    
    new_otp = str(randint(1000,9999))
    otp_memory[phone] = {
        'otp': new_otp,
        'timestamp':time.time()
    }
    return {"message":"OTP resent successfully","new_otp": new_otp}


@app.get("/allUser",response_model= List[schemas.alluser],tags=['user'])
def get_all_user(db: Session = Depends(get_db)):
    return db.query(models.User).all()




#Owner

@app.post('/OwnerWithCars',tags=['owner'])
async def create_ownerWithCars(
    #owner
    profilePic: UploadFile = File(...),name: str = Form(...),email: str = Form(...),contact: str = Form(...),
    licenseNo: str = Form(...),
    #car
    brandName: str = Form(...),carName: str = Form(...),price: int = Form(...),seats: int = Form(...),
    mileage: int = Form(...),city: str = Form(...),maxSpeed: int = Form(...),engineOut: int = Form(...),
    advance: str = Form(...),feature: str = Form(...),registrationNo: str = Form(...),color: str = Form(...),
    fuel: str = Form(...),detail: str = Form(...),

    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    save_dir = "uploads"
    os.makedirs(save_dir,exist_ok=True)
    file_location = f"{save_dir}/{profilePic.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(profilePic.file, buffer)

    db_owner = db.query(models.Owner).filter(models.Owner.email == email).first()
    if not db_owner:
        owner = models.Owner(profilePic = profilePic.filename,name = name,email = email,contact = contact,
                             licenseNo = licenseNo)
        db.add(owner)
        db.flush()
    else:
        owner = db_owner

    if len(images) != 3:
        raise HTTPException(status_code=400, detail="Exactly 3 images are required.")
    
    saved_image_names = []
    for image in images:
        file_location = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        saved_image_names.append(image.filename)

    new_car = models.Car(brandName = brandName,carName = carName,price = price,seats = seats,mileage = mileage,
                         city = city,maxSpeed = maxSpeed,engineOut = engineOut,advance = advance,
                         feature = feature,registrationNo = registrationNo,color = color,fuel = fuel,
                         detail = detail,image_urls = saved_image_names,owner_id =owner.id)
    db.add(new_car)
    db.commit()
    return {"message": "car uploaded successfully", "owner_id": owner.id}

@app.post('/card',tags=['owner'])
async def Card_Create(
    owner_email: str = Form(...),
    cash: Optional[str] = Form(None),
    card_name: Optional[str] = Form(None),
    card_email: Optional[str] = Form(None),
    cardNo: Optional[str] = Form(None),
    expiryDate: Optional[str] = Form(None),
    cvc: Optional[str] = Form(None),
    country: Optional[str] = Form(...),
    zipCode: Optional[int] = Form(...),
    db: Session = Depends(get_db)  
):
    owner = db.query(models.Owner).filter(models.Owner.email == owner_email).first()
    if not owner:
        raise HTTPException(status_code=404,detail="owner not found")
    
    if cash and any([card_name,cardNo,expiryDate,cvc]):
        raise HTTPException(status_code=400,detail="Only one payment method is allowed. Fill either cash or card details.")

    if not cash and not all([card_name,card_email,cardNo,expiryDate,cvc]):
        raise HTTPException(status_code=400,detail="Card details incomplete.")


    db_card = models.Card(
        cash = cash if cash else None,
        card_name = card_name if card_name else None,
        card_email = card_email if card_email else None,
        cardNo = cardNo if cardNo else None,
        expiryDate = expiryDate if expiryDate else None,
        cvc = cvc if cvc else None,
        country = country,
        zipCode = zipCode,
        owner_id = owner.id
    )
    db.add(db_card)
    db.commit()
    return {"message": "payment saved"}


@router.get('/OwnerWithCars',response_model=List[schemas.OwnerWithCars], tags=['owner'])
def get_all_owners_with_cars(db: Session = Depends(get_db)):
    owners = db.query(models.Owner).all()
    base_url = "https://7864-103-173-21-78.ngrok-free.app/uploads"
    result = []

    for owner in owners:
        cars = db.query(models.Car).filter(models.Car.owner_id == owner.id).all()
        owner_dict = {
            "ownerId": owner.id,
            "name": owner.name,
            "email": owner.email,
            "contact": owner.contact,
            "licenseNo": owner.licenseNo,
            "profilePic": f"{base_url}/{owner.profilePic}",
            "cars": []            
        }

        for car in cars:
            image_urls = [f"{base_url}/{img}" for img in car.image_urls]
            car_dict = {
                "carName": car.carName,
                "carBrand": car.carBrand,
                "price": car.price,
                "seats": car.seats,
                "mileage": car.mileage,
                "city": car.city,
                "maxSpeed": car.maxSpeed,
                "engineOut": car.engineOut,
                "advance": car.advance,
                "feature": car.feature,
                "color": car.color,
                "fuel": car.fuel,
                "detail": car.detail,
                "images": image_urls,
            }
            owner_dict["cars"].append(car_dict)
        result.append(owner_dict)

    return result

@app.get("/allowner",response_model= List[schemas.OwnerWithCars],tags=['owner'])
def get_all_owner_with_cars(db: Session = Depends(get_db)):
    return db.query(models.Owner).all()
