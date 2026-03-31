import io

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from app.database import get_db
from app.models.player_event import PlayerEvent, EventType
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/import", tags=["data-import"])


@router.post("/events")
async def import_events(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    """
    Import player events from CSV/Excel.
    Expected columns: tracking_link_id, player_external_id, event_type, amount, currency, event_date
    """
    content = await file.read()

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    required = {"tracking_link_id", "player_external_id", "event_type", "amount", "event_date"}
    missing = required - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    events = []
    errors = []
    for idx, row in df.iterrows():
        try:
            event = PlayerEvent(
                tracking_link_id=int(row["tracking_link_id"]),
                player_external_id=str(row["player_external_id"]),
                event_type=EventType(row["event_type"]),
                amount=float(row.get("amount", 0)),
                currency=str(row.get("currency", "USD")),
                event_date=pd.to_datetime(row["event_date"]),
            )
            events.append(event)
        except Exception as e:
            errors.append({"row": idx + 2, "error": str(e)})

    if events:
        db.add_all(events)
        await db.commit()

    return {
        "imported": len(events),
        "errors": len(errors),
        "error_details": errors[:20],
    }
