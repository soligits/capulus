drop table if exists user;
drop table if exists gp;
drop table if exists gp_users;

create table user (
    id integer primary key autoincrement,
    username varchar(255) unique not null,
    password varchar(255) not null,
    public_key varchar(255)
);

create table gp (
    id integer primary key autoincrement,
    name varchar(255) unique not null,
    owner_id integer not null,
    foreign key (owner_id) references user(id)
);

create table gp_users (
    id integer primary key autoincrement,
    gp_id integer not null,
    user_id integer not null,
    user_role varchar(255) not null,
    foreign key (gp_id) references gp(id),
    foreign key (user_id) references user(id)
);
