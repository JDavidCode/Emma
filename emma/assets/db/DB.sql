CREATE DATABASE IF NOT EXISTS amy;

USE amy;

DROP TABLE IF EXISTS `chatdata`;

CREATE TABLE `chatdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `class` text NOT NULL,
  `input` text,
  `ans` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `chatdata`
--

LOCK TABLES `chatdata` WRITE;
INSERT INTO `chatdata` VALUES (1,'greetings','hello','hello'),(2,'greetings','hey','hi'),(3,'greetings','whats up','hey'),(4,'greetings','are you here','hows it going'),(5,'afirmations','','yes'),(6,'afirmations','','sure'),(7,'afirmations','','okey'),(8,'afirmations','','done'),(9,'negations','','not'),(10,'negations','','dont'),(11,'negations','','never');
UNLOCK TABLES;


--
-- Table structure for table `functions`
--

DROP TABLE IF EXISTS `functions`;

CREATE TABLE `functions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module` text NOT NULL,
  `function_name` text NOT NULL,
  `args_key` text NOT NULL,
  `arguments` text NOT NULL,
  `caller` text NOT NULL,
  `required_lvl` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `functions`
--

LOCK TABLES `functions` WRITE;
INSERT INTO `functions` VALUES (1,'bp','server_shutdown','None',' ','rest',1),(2,'talk._TTS','engine_voice_config','None',' ','configure your voice',1),(3,'bp','module_reloader','*args','','charge module',2),(4,'task.OsModule','volume_management','*args','','loudness',1),(5,'thread','start_thread','*args',' ','activate thread',1),(6,'thread','stop_thread','*args',' ','stop thread',1),(7,'thread','restart_thread','*args',' ','reload thread',1),(8,'task.MiscellaneousModule','weather','args','1','weather',0),(9,'task.MiscellaneousModule','date_clock','args','2','day is',0),(10,'task.MiscellaneousModule','day_parts','None','','part of the day',0),(11,'task.MiscellaneousModule','date_clock','args','3','time',0),(12,'task.WebModule','youtube_player','*args',' ','lets play',1),(13,'task.WebModule','google_search','*args',' ','search about',1),(14,'task.WebModule','open_website','*args',' ','open website',1),(15,'task.WebModule','open_local_site','None',' ','open web console',1),(16,'task.OsModule','open_app','args','1','open app',1);
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lvl` text NOT NULL,
  `name` text NOT NULL,
  `email` text NOT NULL,
  `password` text NOT NULL,
  `age` int NOT NULL,
  `genre` text NOT NULL,
  `lang` text NOT NULL,
  `data` mediumblob NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;



--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES (1,'3','Juan','davidanayaacosta@gmail.com','a1040492386',18,'Male','en',_binary )
UNLOCK TABLES;

