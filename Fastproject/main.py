from datetime import date, timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import extract, or_
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts REST API")

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def search_contacts(
    query: str = Query(None, description="Search by name, last name or email"),
    db: Session = Depends(get_db)
):
    contacts = db.query(models.Contact)
    if query:
        contacts = contacts.filter(
            or_(
                models.Contact.first_name.ilike(f"%{query}%"),
                models.Contact.last_name.ilike(f"%{query}%"),
                models.Contact.email.ilike(f"%{query}%")
            )
        )
    return contacts.all()

@app.get("/contacts/birthdays/", response_model=List[schemas.ContactResponse])
def get_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    upcoming_contacts = []
    
    for i in range(7):
        target_date = today + timedelta(days=i)
        contacts = db.query(models.Contact).filter(
            extract('month', models.Contact.birthday) == target_date.month,
            extract('day', models.Contact.birthday) == target_date.day
        ).all()
        upcoming_contacts.extend(contacts)
    return upcoming_contacts

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, contact_update: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in contact_update.model_dump().items():
        setattr(db_contact, key, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return None