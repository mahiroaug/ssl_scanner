CREATE DATABASE IF NOT EXISTS Certificates;
USE Certificates;

CREATE TABLE Certificates (
    ID INTEGER NOT NULL AUTO_INCREMENT,
    Domain VARCHAR(127) NOT NULL,
    Subject TEXT,
    Issuer TEXT,
    SigAlgorithm TEXT,
    Valid_From DATE,
    Valid_To DATE,
    Last_Check DATETIME,
    CertSerial TEXT,
    PRIMARY KEY (ID),
    UNIQUE (Domain)
);