create table if not exists files(
    id integer primary key autoincrement,
    name text not null unique,
    path text not null unique,
    size integer not null,
    hash text not null unique
)