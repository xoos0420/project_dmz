CREATE DATABASE DMZ;
use DMZ;

DROP Table dmz.new_word;

CREATE TABLE `dmz`.`new_word` (
  `number` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
  `word` varchar(30) NOT NULL,
  `mean` VARCHAR(400) NOT NULL,
  `similar` varchar(255) NOT NULL
  );
  
select * from new_word;

