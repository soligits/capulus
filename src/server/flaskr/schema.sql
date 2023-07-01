drop table if exists user;
drop table if exists msg;
drop table if exists gp;
drop table if exists gp_users;
drop table if exists msg_pv;
drop table if exists msg_gp;

-- Create user table
create table user(
    id integer primary key autoincrement,
    username text unique not null,
    password text not null,
    created timestamp default current_timestamp
);

-- Create public_keys table
create table user_public_keys(
    id integer primary key autoincrement,
    user_id integer not null,
    public_key text not null,
    created timestamp default current_timestamp,
    foreign key(user_id) references user(id)
);


-- Create msg table
create table msg(
    id integer primary key autoincrement,
    sender_id integer not null,
    sender_signature text not null,
    content text not null,
    created timestamp default current_timestamp,
    foreign key(sender_id) references user(id)
);

-- Create gp table
create table gp(
    id integer primary key autoincrement,
    admin_id integer not null,
    name text unique not null,
    created timestamp default current_timestamp,
    foreign key(admin_id) references user(id)
);

-- Create gp_users table
create table gp_users(
    gp_id integer not null,
    user_id integer not null,
    foreign key(gp_id) references gp(id),
    foreign key(user_id) references user(id)
);

-- Create msg_user table
create table msg_pv(
    msg_id integer not null,
    receiver_id integer not null,
    foreign key(msg_id) references msg(id),
    foreign key(receiver_id) references user(id)
);

-- Create msg_gp table
create table msg_gp(
    msg_id integer not null,
    gp_id integer not null,
    foreign key(msg_id) references msg(id),
    foreign key(gp_id) references gp(id)
);
