create database db_projetoHotel;
use db_projetoHotel;

create table hospede(
id int not null primary key auto_increment,
nome varchar(50),
cpf int,
telefone varchar(20),
email varchar(50)
);

create table quarto(
id int not null primary key auto_increment,
numero int,
tipo varchar(50),
preco float,
capacidade int, 
descricao text
);

create table reserva(
id int not null primary key auto_increment,
hos_id int,
checkin date,
ckeckout date,
total float,
FOREIGN KEY (hos_id) REFERENCES hospede(id));

