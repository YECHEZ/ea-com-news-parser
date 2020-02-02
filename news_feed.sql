-- phpMyAdmin SQL Dump
-- version 4.8.2
-- https://www.phpmyadmin.net/

CREATE TABLE `news_feed` (
  `post_id` int(11) NOT NULL,
  `post_title` varchar(300) DEFAULT NULL,
  `post_edit_title` varchar(300) DEFAULT NULL,
  `post_short_description` text,
  `post_description` text,
  `post_game` varchar(100) DEFAULT NULL,
  `post_date` varchar(100) DEFAULT NULL,
  `post_media_url` varchar(300) DEFAULT NULL,
  `post_url` varchar(300) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_posted` tinyint(1) NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Индексы таблицы `news_feed`
--
ALTER TABLE `news_feed`
  ADD PRIMARY KEY (`post_id`);

--
-- AUTO_INCREMENT для таблицы `news_feed`
--
ALTER TABLE `news_feed`
  MODIFY `post_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
COMMIT;