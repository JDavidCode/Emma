CREATE DATABASE IF NOT EXISTS emma;
USE emma;
DROP TABLE IF EXISTS `chatdata`;
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
) ENGINE = InnoDB AUTO_INCREMENT = 52 DEFAULT CHARSET = latin1;
--
-- Dumping data for table `functions`
--
LOCK TABLES `functions` WRITE;
INSERT INTO `functions`
VALUES (1, 'sys_v_bp','server_shutdown','None',' ','rest',1),
	 (2, 'sys_v_tm','start_thread','*args',' ','activate thread',1),
	 (3, 'sys_v_tm','stop_thread','*args',' ','stop thread',1),
	 (4, 'sys_v_tm','restart_thread','*args',' ','reload thread',1),
	 (5, 'sys_v_bp','module_reloader','*args','','charge module',2),
	 (20, 'task_os','open_app','args','1','open app',1),
	 (21, 'task_os','volume_management','*args',' ','loudness',1),
	 (40, 'task_msc','weather','args','1','weather',0),
	 (41, 'task_msc','date_clock','args','2','day is',0),	
	 (42, 'task_msc','day_parts','None','','part of the day',0),
	 (43, 'task_msc','date_clock','args','3','time',0),
	 (60, 'task_web','youtube_player','*args',' ','lets play',1),
	 (61, 'task_web','google_search','*args',' ','search about',1),
	 (62, 'task_web','open_website','*args',' ','open website',1),
	 (63, 'task_web','open_local_site','None',' ','open web console',1);
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
) ENGINE = InnoDB AUTO_INCREMENT = 3 DEFAULT CHARSET = latin1;
--
-- Dumping data for table `users`
--
LOCK TABLES `users` WRITE;
INSERT INTO `users`
VALUES (
    1,
    '3',
    'Juan',
    'davidanayaacosta@gmail.com',
    'a1040492386',
    18,
    'Male',
    'en',
    _binary
  ) UNLOCK TABLES;