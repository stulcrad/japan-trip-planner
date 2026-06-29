-- Japan trip planner schema
-- Run this in the Supabase SQL Editor (Project > SQL Editor > New query) once per project.
-- Supabase Postgres ships with pgcrypto enabled, so gen_random_uuid() works out of the box.

create table users (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    created_at timestamptz not null default now()
);

-- Case-insensitive uniqueness: "find or create by name" on login relies on this.
create unique index users_name_lower_idx on users (lower(name));

create table trip_groups (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    description text,
    created_by uuid not null references users(id),
    start_date date,
    end_date date,
    created_at timestamptz not null default now()
);

create table group_members (
    group_id uuid not null references trip_groups(id) on delete cascade,
    user_id uuid not null references users(id) on delete cascade,
    joined_at timestamptz not null default now(),
    primary key (group_id, user_id) -- a user can only join a given group once
);

create table itinerary_days (
    id uuid primary key default gen_random_uuid(),
    group_id uuid not null references trip_groups(id) on delete cascade,
    date date not null,
    location text not null,
    summary text,
    unique (group_id, date) -- one row per calendar day per trip
);

create table itinerary_items (
    id uuid primary key default gen_random_uuid(),
    day_id uuid not null references itinerary_days(id) on delete cascade,
    time time,
    title text not null,
    notes text,
    added_by uuid references users(id) on delete set null,
    order_index int not null default 0
);

-- Speeds up "list days for a group" and "list items for a day", the two main read paths.
create index itinerary_days_group_id_date_idx on itinerary_days (group_id, date);
create index itinerary_items_day_id_order_idx on itinerary_items (day_id, order_index);
