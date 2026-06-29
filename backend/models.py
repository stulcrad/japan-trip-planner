from sqlalchemy import Column, Date, ForeignKey, Integer, Text, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class TripGroup(Base):
    __tablename__ = "trip_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id = Column(UUID(as_uuid=True), ForeignKey("trip_groups.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"
    __table_args__ = (UniqueConstraint("group_id", "date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("trip_groups.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(Text, nullable=False)
    summary = Column(Text)


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    day_id = Column(UUID(as_uuid=True), ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False)
    time = Column(Time)
    title = Column(Text, nullable=False)
    notes = Column(Text)
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    order_index = Column(Integer, nullable=False, server_default=text("0"))
