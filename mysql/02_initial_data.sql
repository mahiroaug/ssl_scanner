USE Certificates;

INSERT INTO Certificates (Domain) VALUES
('github.com'),
('slack.com');


LOAD DATA INFILE '/var/lib/mysql-files/FQDN.csv'
INTO TABLE Certificates
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
(Domain);

UPDATE Certificates SET Domain = REPLACE(Domain, '\r', '');