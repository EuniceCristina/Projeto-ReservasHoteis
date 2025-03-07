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


--Função calcular_valor_reserva(id_reserva)
CREATE FUNCTION calcular_valor_reserva(id_reserva INT)  
RETURNS FLOAT  
DETERMINISTIC  
BEGIN  
    DECLARE preco_diaria FLOAT;  
    DECLARE data_checkin DATE;  
    DECLARE data_checkout DATE;  
    DECLARE dias INT;  
    DECLARE total FLOAT;  

    SELECT q.preco, r.checkin, r.checkout  
    INTO preco_diaria, data_checkin, data_checkout  
    FROM reserva r  
    JOIN quarto q ON r.quarto_id = q.id  
    WHERE r.id = id_reserva;  

    SET dias = DATEDIFF(data_checkout, data_checkin);  

    SET total = preco_diaria * dias;  

    RETURN total;  
END $$

DELIMITER ;


--Trgger validar_checkin
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

-- Criar Trigger para registrar cada inserção, edição e exclusão de reserva

CREATE TABLE logs_reservas (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    reserva_id INT,
    acao ENUM('INSERT', 'UPDATE', 'DELETE'),
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50),
    detalhes TEXT
);

DELIMITER $$

CREATE TRIGGER log_reservas_insert
AFTER INSERT ON reserva
FOR EACH ROW
BEGIN
    INSERT INTO logs_reservas (reserva_id, acao, usuario, detalhes)
    VALUES (NEW.id, 'INSERT', CURRENT_USER(), CONCAT('Reserva criada: Check-in ', NEW.checkin, ', Check-out ', NEW.checkout, ', Total: ', NEW.total));
END $$

CREATE TRIGGER log_reservas_update
AFTER UPDATE ON reserva
FOR EACH ROW
BEGIN
    INSERT INTO logs_reservas (reserva_id, acao, usuario, detalhes)
    VALUES (NEW.id, 'UPDATE', CURRENT_USER(), CONCAT('Reserva alterada: Check-in ', NEW.checkin, ', Check-out ', NEW.checkout, ', Total: ', NEW.total));
END $$

CREATE TRIGGER log_reservas_delete
AFTER DELETE ON reserva
FOR EACH ROW
BEGIN
    INSERT INTO logs_reservas (reserva_id, acao, usuario, detalhes)
    VALUES (OLD.id, 'DELETE', CURRENT_USER(), CONCAT('Reserva removida: Check-in ', OLD.checkin, ', Check-out ', OLD.checkout, ', Total: ', OLD.total));
END $$

DELIMITER ;

--Procedimento armazenado validar_reserva(id_hospede, id_quarto, check_in, check_out). 

CREATE PROCEDURE validar_reserva(
    IN id_hospede INT,
    IN id_quarto INT,
    IN check_in DATE,
    IN check_out DATE
)
BEGIN
    DECLARE conflito INT;
    DECLARE apto INT;
    
    -- Verificar disponibilidade do quarto
    SELECT COUNT(*) INTO conflito 
    FROM reserva 
    WHERE quarto_id = id_quarto
    AND (
        (check_in BETWEEN checkin AND checkout) OR 
        (check_out BETWEEN checkin AND checkout) OR 
        (check_in <= checkin AND check_out >= checkout)
    );
    
    IF conflito > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: O quarto já está reservado para este período.';
    END IF;
    
    -- Verificar se o hóspede está apto a reservar (exemplo: status ativo)
    SELECT COUNT(*) INTO apto FROM hospede WHERE id = id_hospede;
    
    IF apto = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: Hóspede não encontrado ou não apto para reserva.';
    END IF;
END $$

DELIMITER ;