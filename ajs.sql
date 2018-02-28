-- phpMyAdmin SQL Dump
-- version 4.4.14
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Feb 23, 2018 at 04:35 AM
-- Server version: 5.6.26
-- PHP Version: 5.6.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ajs`
--

-- --------------------------------------------------------

--
-- Table structure for table `aj_table`
--

CREATE TABLE IF NOT EXISTS `aj_table` (
  `tid` int(11) NOT NULL,
  `name` varchar(250) NOT NULL,
  `flag` enum('true','false') NOT NULL DEFAULT 'true'
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `bill` (
  `bid` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `payment_mode` enum('cash','card','credit') NOT NULL,
  `discount` int(11) NOT NULL DEFAULT '0',
  `amount` int(11) DEFAULT '0'
) ENGINE=InnoDB AUTO_INCREMENT=2315 DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `bill_kot` (
  `bid` int(11) NOT NULL,
  `kid` int(11) NOT NULL,
  `flag` enum('true','false') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `category` (
  `cid` int(11) NOT NULL,
  `name` varchar(250) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `item` (
  `iid` int(11) NOT NULL,
  `name` varchar(250) NOT NULL,
  `description` text,
  `cost` int(11) NOT NULL,
  `flag` enum('true','false') NOT NULL DEFAULT 'true',
  `cat` varchar(100) DEFAULT '-'
) ENGINE=InnoDB AUTO_INCREMENT=388 DEFAULT CHARSET=latin1;

able structure for table `item_category`
--

CREATE TABLE IF NOT EXISTS `item_category` (
  `iid` int(11) NOT NULL,
  `cid` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `kot` (
  `kid` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag` enum('true','false') NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=3830 DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `sub_item` (
  `sid` int(11) NOT NULL,
  `name` varchar(250) NOT NULL,
  `flag` enum('true','false') NOT NULL DEFAULT 'true'
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `sub_item_category` (
  `sid` int(11) NOT NULL,
  `cid` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


ALTER TABLE `aj_table`
  ADD PRIMARY KEY (`tid`),
  ADD UNIQUE KEY `name` (`name`);

ALTER TABLE `bill`
  ADD PRIMARY KEY (`bid`),
  ADD UNIQUE KEY `timestamp` (`timestamp`);


ALTER TABLE `bill_kot`
  ADD PRIMARY KEY (`bid`,`kid`),
  ADD KEY `kid` (`kid`);


ALTER TABLE `category`
  ADD PRIMARY KEY (`cid`),
  ADD UNIQUE KEY `name` (`name`);

ALTER TABLE `item`
  ADD PRIMARY KEY (`iid`),
  ADD UNIQUE KEY `name` (`name`);

ALTER TABLE `item_category`
  ADD PRIMARY KEY (`iid`,`cid`),
  ADD KEY `iid` (`iid`),
  ADD KEY `cid` (`cid`);


ALTER TABLE `kot`
  ADD PRIMARY KEY (`kid`);


ALTER TABLE `orders`
  ADD PRIMARY KEY (`tid`,`iid`,`kid`,`rank`),
  ADD KEY `iid` (`iid`),
  ADD KEY `kid` (`kid`),
  ADD KEY `tid` (`tid`),
  ADD KEY `rank` (`rank`);


ALTER TABLE `sub_item`
  ADD PRIMARY KEY (`sid`);


ALTER TABLE `sub_item_category`
  ADD PRIMARY KEY (`sid`,`cid`),
  ADD KEY `sid` (`sid`),
  ADD KEY `cid` (`cid`);


ALTER TABLE `aj_table`
  MODIFY `tid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=109;

ALTER TABLE `bill`
  MODIFY `bid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2315;

ALTER TABLE `category`
  MODIFY `cid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=13;

ALTER TABLE `item`
  MODIFY `iid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=388;

ALTER TABLE `kot`
  MODIFY `kid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=3830;

ALTER TABLE `sub_item`
  MODIFY `sid` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=44;

ALTER TABLE `bill_kot`
  ADD CONSTRAINT `bill_kot_ibfk_1` FOREIGN KEY (`bid`) REFERENCES `bill` (`bid`),
  ADD CONSTRAINT `bill_kot_ibfk_2` FOREIGN KEY (`kid`) REFERENCES `kot` (`kid`);


ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`tid`) REFERENCES `aj_table` (`tid`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`iid`) REFERENCES `item` (`iid`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`kid`) REFERENCES `kot` (`kid`);

ALTER TABLE `sub_item_category`
  ADD CONSTRAINT `sub_item_category_ibfk_1` FOREIGN KEY (`cid`) REFERENCES `category` (`cid`),
  ADD CONSTRAINT `sub_item_category_ibfk_2` FOREIGN KEY (`sid`) REFERENCES `sub_item` (`sid`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
