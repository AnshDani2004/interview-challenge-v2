from fastapi import APIRouter, UploadFile, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import csv
from app.models import Business, Symptom
from app.database import SessionLocal
from typing import Optional

# Router initialization
router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Status endpoint
@router.get('/status')
async def get_status():
    try:
        return {"Health": "OK"}
    except Exception as e:
        return {'Error': str(e)}

@router.post('/import-csv/', summary="Import CSV")
async def import_csv(file: UploadFile, db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        csv_data = contents.decode('utf-8').splitlines()
        reader = csv.reader(csv_data)

        next(reader)  # Skip header row

        for row in reader:
            business_id = int(row[0].strip())
            business_name = row[1].strip()
            symptom_code = row[2].strip()
            symptom_name = row[3].strip()
            symptom_diagnostic = row[4].strip().lower()  # Normalize for consistency

            # Check if the business exists by ID
            business = db.query(Business).filter(Business.id == business_id).first()
            if not business:
                # Create a new business record if it doesn't exist
                business = Business(id=business_id, name=business_name)
                db.add(business)
                db.commit()

            # Check if the symptom already exists
            symptom = db.query(Symptom).filter(
                Symptom.code == symptom_code,
                Symptom.business_id == business.id
            ).first()

            if not symptom:
                symptom = Symptom(
                    code=symptom_code,
                    name=symptom_name,
                    diagnostic=symptom_diagnostic,
                    business_id=business.id
                )
                db.add(symptom)

        db.commit()
        return {"message": "CSV imported successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get('/data', summary="Get Business and Symptom Data")
async def get_data(
    business_id: Optional[int] = Query(None, description="Filter by Business ID"),
    diagnostic: Optional[str] = Query(None, description="Filter by Symptom Diagnostic (true/false)"),
    db: Session = Depends(get_db)
):
    try:
        # Build the query
        query = db.query(
            Business.id.label("Business ID"),
            Business.name.label("Business Name"),
            Symptom.code.label("Symptom Code"),
            Symptom.name.label("Symptom Name"),
            Symptom.diagnostic.label("Symptom Diagnostic")
        ).join(Symptom)

        # Apply Filters
        if business_id:
            query = query.filter(Business.id == business_id)
        if diagnostic:
            query = query.filter(Symptom.diagnostic == diagnostic.lower())  # Normalize diagnostic filter

        # Execute the query
        results = query.all()

        # Transform the results into the desired format
        results_list = [
            {
                "Business ID": row[0],  # Corresponds to Business.id.label("Business ID")
                "Business Name": row[1],  # Corresponds to Business.name.label("Business Name")
                "Symptom Code": row[2],  # Corresponds to Symptom.code.label("Symptom Code")
                "Symptom Name": row[3],  # Corresponds to Symptom.name.label("Symptom Name")
                "Symptom Diagnostic": row[4]  # Corresponds to Symptom.diagnostic.label("Symptom Diagnostic")
            }
            for row in results
        ]

        # Return the formatted response
        return {"data": results_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
