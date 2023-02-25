USE Certificates;

INSERT INTO Certificates (Domain) VALUES
('github.com'),
('slack.com');

BULK INSERT Certificates (Domain)
FROM 'FQDN.csv'
WITH (
    FORMAT = 'CSV',
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 1
);