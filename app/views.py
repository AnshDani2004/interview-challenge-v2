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

# Import CSV endpoint
@router.post('/import-csv/', summary="Import CSV")
async def import_csv(file: UploadFile, db: Session = Depends(get_db)):
    """
    Import data from a CSV file into the database.
    """
    try:
        content = await file.read()
        data = content.decode('utf-8').splitlines()
        reader = csv.reader(data)

        # Skip the header row
        next(reader, None)

        for row in reader:
            # Extract data from the CSV row
            business_id, business_name, symptom_code, symptom_name, symptom_diagnostic = row

            # Check if the business already exists by name (to avoid foreign key constraint violation)
            business = db.query(Business).filter(Business.name == business_name).first()

            if not business:
                # If business does not exist, create a new record
                business = Business(id=business_id, name=business_name)
                db.add(business)
                db.commit()  # Commit after adding the business

            # Ensure the symptom exists or create it
            symptom = db.query(Symptom).filter(
                Symptom.code == symptom_code,
                Symptom.business_id == business_id
            ).first()

            if not symptom:
                symptom = Symptom(
                    code=symptom_code,
                    name=symptom_name,
                    diagnostic=symptom_diagnostic,  # Keep as string
                    business_id=business.id  # Ensure correct foreign key
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
    diagnostic: Optional[bool] = Query(None, description="Filter by Symptom Diagnostic"),
    db: Session = Depends(get_db)
):
    """
    Get data from the database based on optional filters for business_id and diagnostic.
    """
    try:
        # Query Business and Symptom Data
        query = db.query(
            Business.id.label("Business ID"), 
            Business.name.label("Business Name"), 
            Symptom.code.label("Symptom Code"), 
            Symptom.name.label("Symptom Name"), 
            Symptom.diagnostic.label("Symptom Diagnostic")
        ).join(Symptom)

        # Apply Filters if provided
        if business_id:
            query = query.filter(Business.id == business_id)
        if diagnostic is not None:  # Explicit check for None since it's a boolean
            # Convert the boolean to string for comparison with symptom.diagnostic
            query = query.filter(Symptom.diagnostic == str(diagnostic).lower())  # 'true' or 'false'

        # Execute the query
        results = query.all()

        # Convert the results to a list of dictionaries
        results_list = [
            {
                "Business ID": row[0],
                "Business Name": row[1],
                "Symptom Code": row[2],
                "Symptom Name": row[3],
                "Symptom Diagnostic": row[4]
            }
            for row in results
        ]

        # Return the results
        return {"data": results_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
