from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any

from app.api import deps
from app.db.database import get_db
from app.db.models.all_models import User, SystemSetting

router = APIRouter()

class BlockchainToggleRequest(BaseModel):
    enabled: bool

@router.get("/settings/blockchain", response_model=dict)
def get_blockchain_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get the current global status of the Web3 integration."""
    if current_user.role.name != "SuperAdmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SuperAdmin access required.")
        
    setting = db.query(SystemSetting).filter_by(setting_key="blockchain_enabled").first()
    is_enabled = setting.setting_value.lower() == "true" if setting else False
    
    return {
        "blockchain_enabled": is_enabled
    }

@router.post("/settings/blockchain/toggle", response_model=dict)
def toggle_blockchain_status(
    request: BlockchainToggleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Toggle the Web3 integration globally."""
    if current_user.role.name != "SuperAdmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SuperAdmin access required.")
        
    setting = db.query(SystemSetting).filter_by(setting_key="blockchain_enabled").first()
    
    if setting:
        setting.setting_value = "true" if request.enabled else "false"
    else:
        setting = SystemSetting(
            setting_key="blockchain_enabled",
            setting_value="true" if request.enabled else "false",
            description="Global toggle for Web3 testnet integration"
        )
        db.add(setting)
        
    db.commit()
    
    return {
        "status": "success",
        "blockchain_enabled": request.enabled,
        "message": f"Blockchain integration turned {'ON' if request.enabled else 'OFF'} globally."
    }
