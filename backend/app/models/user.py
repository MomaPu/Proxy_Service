from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import secrets


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    activation_key = Column(String, unique=True, nullable=True)
    activation_key_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связь с виртуальной машиной
    current_vm = relationship("VirtualMachine", foreign_keys="VirtualMachine.current_user_id", backref="user")

    def generate_activation_key(self):
        self.activation_key = secrets.token_urlsafe(32)
        from datetime import datetime, timedelta
        self.activation_key_expires = datetime.utcnow() + timedelta(hours=24)
        return self.activation_key