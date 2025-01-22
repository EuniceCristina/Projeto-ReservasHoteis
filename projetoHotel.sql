create database db_projetoHotel;
use db_projetoHotel;

create table tb_hospede(
hos_id int not null primary key auto_increment,
hos_nome varchar(50),
hos_cpf int,
hos_telefone varchar(20),
hos_email varchar(50)
);

create table tb_quarto(
qua_id int not null primary key auto_increment,
qua_numero int,
qua_tipo varchar(50),
qua_preco float,
qua_capacidade int, 
qua_descricao text
);

create table tb_reserva(
res_id int not null primary key auto_increment,
res_hos_id int,
res_checkin date,
res_ckeckout date,
res_tota float,
FOREIGN KEY (res_hos_id) REFERENCES tb_hospede(hos_id));

