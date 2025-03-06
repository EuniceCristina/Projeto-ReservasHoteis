create database db_projetoHotel;

use db_projetoHotel;


create table hospede(
id int not null primary key auto_increment,
nome varchar(50),
cpf varchar(50) ,
telefone varchar(20),
email varchar(50),
senha varchar(50),
tipo varchar(50)
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
quarto_id int not null,
checkin date,
checkout date,
total float,
situacao varchar(50),
FOREIGN KEY (hos_id) REFERENCES hospede(id),
FOREIGN KEY (quarto_id) REFERENCES quarto(id)
);

DELIMITER $$

CREATE TRIGGER validar_checkin
BEFORE INSERT ON reserva
FOR EACH ROW
BEGIN
    DECLARE conflito INT;
    SELECT COUNT(*) INTO conflito 
    FROM reserva 
    WHERE quarto_id = NEW.quarto_id
    AND (
        (NEW.checkin BETWEEN checkin AND checkout) OR 
        (NEW.checkout BETWEEN checkin AND checkout) OR 
        (NEW.checkin <= checkin AND NEW.checkout >= checkout)
    );

    IF conflito > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: O quarto já está reservado para este período.';
    END IF;
END $$

DELIMITER ;

CREATE FUNCTION calcular_valor_reserva(id_reserva INT)  
RETURNS FLOAT  
DETERMINISTIC  
BEGIN  
    DECLARE preco_diaria FLOAT;  
    DECLARE data_checkin DATE;  
    DECLARE data_checkout DATE;  
    DECLARE dias INT;  
    DECLARE total FLOAT;  

    -- Buscar os dados da reserva
    SELECT q.preco, r.checkin, r.checkout  
    INTO preco_diaria, data_checkin, data_checkout  
    FROM reserva r  
    JOIN quarto q ON r.quarto_id = q.id  
    WHERE r.id = id_reserva;  

    -- Calcular a quantidade de dias da reserva
    SET dias = DATEDIFF(data_checkout, data_checkin);  

    -- Calcular o total da reserva
    SET total = preco_diaria * dias;  

    RETURN total;  
END $$

DELIMITER ;



