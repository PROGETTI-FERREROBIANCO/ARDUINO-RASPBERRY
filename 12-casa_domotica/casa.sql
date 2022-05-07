-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Creato il: Apr 30, 2022 alle 18:14
-- Versione del server: 10.4.22-MariaDB
-- Versione PHP: 8.1.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `casa`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `consumi`
--

CREATE TABLE `consumi` (
  `id` int(11) NOT NULL,
  `id_dispositivo` int(11) NOT NULL,
  `data_ora` datetime NOT NULL,
  `consumo` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Struttura della tabella `dispositivi`
--

CREATE TABLE `dispositivi` (
  `id` int(11) NOT NULL,
  `id_stanza` int(11) NOT NULL,
  `nome` varchar(32) NOT NULL,
  `descrizione` varchar(64) NOT NULL,
  `pin_output` int(11) NOT NULL,
  `tecnologia_utilizzata_lettura` varchar(64) NOT NULL,
  `valore_tecn_utilizzata_lettura` int(11) NOT NULL,
  `zero_dispositivo` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `dispositivi`
--

INSERT INTO `dispositivi` (`id`, `id_stanza`, `nome`, `descrizione`, `pin_output`, `tecnologia_utilizzata_lettura`, `valore_tecn_utilizzata_lettura`, `zero_dispositivo`) VALUES
(1, 1, 'Luce', 'Luce di Gabriele', 8, 'ANALOGICO', 5, 0),
(2, 2, 'Luce', 'Luce di Michela', 8, 'ANALOGICO', 5, 0),
(3, 3, 'Luce', 'Luce di Simone', 8, 'ANALOGICO', 5, 0),
(4, 4, 'Luce', 'Luce Corr. 1', 8, 'ANALOGICO', 5, 0),
(5, 5, 'Luce', 'Luce Corr. 2', 8, 'ANALOGICO', 5, 0),
(6, 6, 'Luce', 'Luce Bagno', 8, 'ANALOGICO', 5, 0);

-- --------------------------------------------------------

--
-- Struttura della tabella `log_accessi`
--

CREATE TABLE `log_accessi` (
  `id` int(11) NOT NULL,
  `username` varchar(64) NOT NULL,
  `data_ora_accesso` datetime NOT NULL,
  `esito` varchar(16) NOT NULL,
  `id_utente` int(11) DEFAULT NULL,
  `indirizzo_ip` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `log_comandi`
--

CREATE TABLE `log_comandi` (
  `id` int(11) NOT NULL,
  `id_utente` int(11) NOT NULL,
  `data_ora_comando` datetime NOT NULL,
  `descrizione` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struttura della tabella `stanze`
--

CREATE TABLE `stanze` (
  `id` int(11) NOT NULL,
  `nome` varchar(32) NOT NULL,
  `descrizione` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `stanze`
--

INSERT INTO `stanze` (`id`, `nome`, `descrizione`) VALUES
(1, 'Gabriele', 'Stanza di Gabriele'),
(2, 'Michela', 'Stanza di Michela'),
(3, 'Simone', 'Stanza di Simone'),
(4, 'Corr. 1', 'Corridoio delle stanze'),
(5, 'Corr. 2', 'Corridoio del bagno'),
(6, 'Bagno', 'Bagno delle stanze');

-- --------------------------------------------------------

--
-- Struttura della tabella `utenti`
--

CREATE TABLE `utenti` (
  `id` int(11) NOT NULL,
  `username` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  `grado_amministrazione` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `utenti`
--

INSERT INTO `utenti` (`id`, `username`, `password`, `grado_amministrazione`) VALUES
(1, 'admin', '...', 'amministratore'),
(2, 'Gabbi', '...', 'utente'),
(3, 'michela', '...', 'utente');

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `consumi`
--
ALTER TABLE `consumi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chiave_consumo_dispositivo` (`id_dispositivo`);

--
-- Indici per le tabelle `dispositivi`
--
ALTER TABLE `dispositivi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chiave_stanza_dispositivo` (`id_stanza`);

--
-- Indici per le tabelle `log_accessi`
--
ALTER TABLE `log_accessi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chiave_utente_accessi` (`id_utente`);

--
-- Indici per le tabelle `log_comandi`
--
ALTER TABLE `log_comandi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chiave_utente_comandi` (`id_utente`);

--
-- Indici per le tabelle `stanze`
--
ALTER TABLE `stanze`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `utenti`
--
ALTER TABLE `utenti`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `consumi`
--
ALTER TABLE `consumi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT per la tabella `dispositivi`
--
ALTER TABLE `dispositivi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT per la tabella `log_accessi`
--
ALTER TABLE `log_accessi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `log_comandi`
--
ALTER TABLE `log_comandi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `stanze`
--
ALTER TABLE `stanze`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT per la tabella `utenti`
--
ALTER TABLE `utenti`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `consumi`
--
ALTER TABLE `consumi`
  ADD CONSTRAINT `chiave_consumo_dispositivo` FOREIGN KEY (`id_dispositivo`) REFERENCES `dispositivi` (`id`) ON UPDATE CASCADE;

--
-- Limiti per la tabella `dispositivi`
--
ALTER TABLE `dispositivi`
  ADD CONSTRAINT `chiave_stanza_dispositivo` FOREIGN KEY (`id_stanza`) REFERENCES `stanze` (`id`) ON UPDATE CASCADE;

--
-- Limiti per la tabella `log_accessi`
--
ALTER TABLE `log_accessi`
  ADD CONSTRAINT `chiave_utente_accessi` FOREIGN KEY (`id_utente`) REFERENCES `utenti` (`id`) ON UPDATE CASCADE;

--
-- Limiti per la tabella `log_comandi`
--
ALTER TABLE `log_comandi`
  ADD CONSTRAINT `chiave_utente_comandi` FOREIGN KEY (`id_utente`) REFERENCES `utenti` (`id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
