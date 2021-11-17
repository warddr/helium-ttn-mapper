CREATE TABLE `heliumhotspots` (
  `id` varchar(65) NOT NULL,
  `name` varchar(50) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `access_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `heliumtracker` (
  `id` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `dev_eui` varchar(20) NOT NULL,
  `fcnt` int(11) NOT NULL,
  `frequency` float NOT NULL,
  `hotspot` varchar(65) NOT NULL,
  `rssi` int(11) NOT NULL,
  `snr` int(11) NOT NULL,
  `spreading` varchar(20) NOT NULL,
  `payload` varchar(50) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `sats` tinyint(4) NOT NULL,
  `distance` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
