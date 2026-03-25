-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 25, 2026 at 06:51 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `savorshelf`
--

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `pantry_item_id` int(11) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `type` varchar(50) NOT NULL,
  `is_unread` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `pantry_item_id`, `title`, `message`, `type`, `is_unread`, `created_at`) VALUES
(26, 7, NULL, 'Expiring Soon', 'Lobster will expire in 3 day(s). Freshness: 42%', 'expiry_before', 1, '2026-03-12 09:00:05'),
(29, 7, NULL, 'Expiring Soon', 'Strawberry will expire in 3 day(s).', 'expiry_before', 1, '2026-03-13 09:00:36'),
(48, 1, NULL, 'Expiring Soon', 'Apple will expire in 1 day(s).', 'expiry_before', 0, '2026-03-15 18:00:28'),
(66, 1, NULL, 'Urgent: Item Expiring Today!', 'Apple expires today. Use it immediately!', 'critical_expiry', 0, '2026-03-16 09:00:42'),
(71, 1, NULL, 'Urgent: Item Expiring Today!', 'Chicken Wings expires today. Use it immediately!', 'critical_expiry', 0, '2026-03-17 09:30:55'),
(74, 2, NULL, 'Weekly Pantry Summary', 'Used: 0, Wasted: 0, In Pantry: 6, Use Soon: 1, Expired: 0, Fresh: 5', 'weekly_summary', 0, '2026-03-19 12:35:45'),
(75, 2, 94, 'Expiring Soon', 'Apple will expire in 2 day(s).', 'expiry_before', 0, '2026-03-20 12:59:14'),
(76, 2, 94, 'Urgent: Item Expiring Today!', 'Apple expires today. Use it immediately!', 'critical_expiry', 0, '2026-03-22 17:50:12'),
(77, 2, 114, 'Expiring Soon', 'Cranberry will expire in 2 day(s).', 'expiry_before', 0, '2026-03-23 10:56:17');

-- --------------------------------------------------------

--
-- Table structure for table `pantry_items`
--

CREATE TABLE `pantry_items` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `storage_type` varchar(50) DEFAULT NULL,
  `mfg_date` date DEFAULT NULL,
  `purchase_date` date DEFAULT NULL,
  `quantity` varchar(100) DEFAULT NULL,
  `expiry_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `image_path` varchar(500) DEFAULT NULL,
  `lot_number` varchar(100) DEFAULT 'N/A',
  `is_labeled` tinyint(1) DEFAULT 0,
  `status` enum('active','consumed','wasted') DEFAULT 'active',
  `updated_at` datetime DEFAULT NULL,
  `hidden_from_products` tinyint(1) DEFAULT 0,
  `pending_weekly_cleanup` tinyint(1) DEFAULT 0,
  `expired_hidden_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pantry_items`
--

INSERT INTO `pantry_items` (`id`, `user_id`, `item_name`, `category`, `storage_type`, `mfg_date`, `purchase_date`, `quantity`, `expiry_date`, `created_at`, `image_path`, `lot_number`, `is_labeled`, `status`, `updated_at`, `hidden_from_products`, `pending_weekly_cleanup`, `expired_hidden_at`, `deleted_at`) VALUES
(79, 7, 'Chicken Wings', 'Meat & Seafood', 'Room Temperature', NULL, '2026-03-11', '5', '2026-03-18', '2026-03-12 03:07:06', '/static/meat_and_seafood/chicken_wings.jpg', NULL, 0, 'wasted', '2026-03-19 10:18:15', 1, 1, '2026-03-19 10:18:15', NULL),
(81, 7, 'Butter - Salted', 'Dairy', 'Room Temperature', NULL, '2026-03-11', '4', '2026-03-18', '2026-03-12 03:08:09', '/static/dairy/butter_salted.jpg', NULL, 0, 'wasted', '2026-03-19 10:18:15', 1, 1, '2026-03-19 10:18:15', NULL),
(86, 8, 'Carrots', 'Vegetables', 'Freezer', NULL, '2026-03-14', '5kg', '2026-03-21', '2026-03-13 05:48:37', '/static/vegetables/carrots.jpg', NULL, 0, 'wasted', '2026-03-22 17:49:50', 1, 1, '2026-03-22 17:49:50', NULL),
(94, 2, 'Apple', 'Fruits', 'Room Temperature', NULL, '2026-03-12', '2kg', '2026-03-22', '2026-03-15 16:17:07', '/static/fruits/Apple.jpg', NULL, 0, 'wasted', '2026-03-23 08:37:49', 1, 1, '2026-03-23 08:37:49', NULL),
(102, 2, 'Croissant', 'Snack', 'Room Temperature', '2021-06-02', NULL, '8 Packs', '2026-06-01', '2026-03-16 03:32:58', '/uploads/products/user_2_1773631976_front.jpg', '02062021', 1, 'consumed', '2026-03-19 12:35:53', 1, 1, NULL, NULL),
(104, 2, 'Popcorn', 'Snack', 'Room Temperature', '2024-06-02', NULL, '2 Packs', '2026-06-01', '2026-03-16 05:06:43', '/uploads/products/user_2_1773637601_front.jpg', '02062021', 1, 'consumed', '2026-03-23 08:59:07', 1, 1, NULL, NULL),
(113, 2, 'Cashew', 'Nuts', 'Room Temperature', '2021-06-02', NULL, '500g', '2026-06-01', '2026-03-19 05:15:03', '/uploads/products/user_2_1773897301_front.jpg', '02062021', 1, 'consumed', '2026-03-23 08:59:05', 1, 1, NULL, NULL),
(114, 2, 'Cranberry', 'Fruits', 'Fridge', NULL, '2026-03-18', '200g', '2026-03-25', '2026-03-19 05:15:45', '/static/fruits/cranberry.jpg', NULL, 0, 'active', NULL, 0, 0, NULL, NULL),
(115, 2, 'Unsalted Butter', 'Dairy', 'Fridge', NULL, '2026-03-17', '250g', '2026-05-16', '2026-03-19 05:21:01', '/static/dairy/unsalted_butter.jpg', NULL, 0, 'active', NULL, 0, 0, NULL, NULL),
(116, 2, 'Blueberry', 'Fruits', 'Fridge', NULL, '2026-02-28', '1kg', '2026-03-10', '2026-03-19 07:18:58', '/static/fruits/blueberry.jpg', NULL, 0, 'wasted', '2026-03-19 12:48:58', 1, 1, '2026-03-19 12:48:58', NULL),
(117, 2, 'Blood Orange', 'Fruits', 'Room Temperature', NULL, '2026-01-02', '1kg', '2026-01-16', '2026-03-19 07:19:22', '/static/fruits/blood_orange.jpg', NULL, 0, 'wasted', '2026-03-19 12:49:22', 1, 1, '2026-03-19 12:49:22', NULL),
(118, 2, 'Gooseberry', 'Fruits', 'Room Temperature', NULL, '2026-01-01', '1kg', '2026-01-08', '2026-03-19 07:20:45', '/static/fruits/gooseberry.jpg', NULL, 0, 'wasted', '2026-03-19 12:50:45', 1, 1, '2026-03-19 12:50:45', NULL),
(119, 2, 'Gooseberry', 'Fruits', 'Room Temperature', NULL, '2026-02-14', '1kg', '2026-02-21', '2026-03-19 07:38:08', '/static/fruits/gooseberry.jpg', NULL, 0, 'wasted', '2026-03-19 13:08:57', 1, 1, '2026-03-19 13:08:57', NULL),
(120, 2, '245g', 'fgy', 'Room Temperature', '2026-03-19', NULL, '46b', '2026-03-28', '2026-03-19 08:43:41', '/uploads/products/user_2_1773909819_front.jpg', '467', 1, 'consumed', '2026-03-19 14:14:05', 1, 1, NULL, NULL),
(121, 2, 'Prawns', 'Meat & Seafood', 'Fridge', NULL, '2026-03-08', '500g', '2026-03-15', '2026-03-19 09:07:57', '/static/meat_and_seafood/prawns.jpg', NULL, 0, 'wasted', '2026-03-19 14:37:58', 1, 1, '2026-03-19 14:37:58', NULL),
(122, 2, 'Crab', 'Meat & Seafood', 'Fridge', NULL, '2026-03-18', '1', '2026-03-25', '2026-03-19 09:09:21', '/static/meat_and_seafood/crab.png', NULL, 0, 'consumed', '2026-03-24 20:19:58', 1, 1, '2026-03-24 20:19:58', NULL),
(123, 2, 'jk', NULL, 'Room Temperature', '2026-03-18', NULL, '48kg', '2099-03-19', '2026-03-19 09:11:05', '/uploads/products/user_2_1773911463_front.jpg', NULL, 1, 'consumed', '2026-03-23 08:59:09', 1, 1, NULL, NULL),
(124, 2, 'Anaheim Peppers', 'Vegetables', 'Room Temperature', NULL, '2026-03-10', '4', '2026-03-17', '2026-03-23 03:29:53', '/static/vegetables/anaheim_peppers.jpg', NULL, 0, 'consumed', '2026-03-23 09:00:04', 1, 1, NULL, NULL),
(125, 2, 'Chips', 'Snacks', 'Room Temperature', '2021-06-02', NULL, '2 packets', '2026-06-01', '2026-03-23 03:33:32', '/uploads/products/user_2_1774236810_front.jpg', '02062021', 1, 'active', NULL, 0, 0, NULL, NULL),
(126, 2, 'Juice', 'Drinks', 'Fridge', '2021-06-02', NULL, '1', '2026-06-01', '2026-03-23 15:43:11', '/uploads/products/user_2_1774280587_front.jpg', '080204', 1, 'consumed', '2026-03-24 08:37:56', 1, 1, '2026-03-24 08:37:56', NULL),
(127, 2, 'Strawberry', 'Fruits', 'Fridge', NULL, '2026-03-23', '1Packet', '2026-03-30', '2026-03-23 15:51:49', '/static/fruits/Strawberry.jpg', NULL, 0, 'active', NULL, 0, 0, NULL, NULL),
(128, 2, 'Fruits', 'Fruits', 'Fridge', NULL, '2026-03-24', '1 unit', '2026-03-31', '2026-03-24 05:50:07', '/static/fruits/fruits.jpg', NULL, 0, 'consumed', '2026-03-24 11:37:39', 1, 1, NULL, NULL),
(129, 2, 'bana', 'healthy', 'Room Temperature', '2021-06-02', NULL, '1', '2026-06-01', '2026-03-24 06:17:33', '/uploads/products/user_2_1774333051_front.jpg', '0929738', 1, 'consumed', '2026-03-24 13:48:10', 1, 1, '2026-03-24 13:48:10', NULL),
(130, 2, 'Apple', 'Fruits', 'Room Temperature', NULL, '2026-03-24', '2', '2026-03-31', '2026-03-24 07:40:51', '/static/fruits/Apple.jpg', NULL, 0, 'active', NULL, 0, 0, NULL, NULL),
(131, 2, 'Whole Milk', 'Dairy', 'Fridge', NULL, '2026-03-24', '1', '2026-03-31', '2026-03-24 08:16:56', '/static/dairy/whole_milk.jpg', NULL, 0, 'consumed', '2026-03-24 13:48:03', 1, 1, '2026-03-24 13:48:03', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `register`
--

CREATE TABLE `register` (
  `id` int(190) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `email` varchar(190) NOT NULL,
  `password` varchar(170) NOT NULL,
  `otp` varchar(50) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `register`
--

INSERT INTO `register` (`id`, `full_name`, `email`, `password`, `otp`, `otp_expiry`) VALUES
(1, 'Jayram', 'jayaramklv@gmail.com', 'scrypt:32768:8:1$dixDHslxdlte3bf4$b4b99bd647a7044f0373d9f2b8cc9e01321a516ecc5567fc8b4cb37faaac1e71de673dcba08f43e6840d854efb9a3bc289149c27be32111355bf71f854ed92a3', NULL, NULL),
(2, 'Keerthi Reddy', 'naramreddy.keerthi@gmail.com', 'scrypt:32768:8:1$X8ARwTNHc5YLL63R$135dab188d3ff0ce993d3118a9e94bc3a2c9bb224adb6145d72071b04d6828b704f667fe5241f0dbe09adfc43961dc6cc17310e2ea8c5c6b2394440512224c8f', '1043', '2026-03-24 13:54:22'),
(3, 'Vennela', 'gvennela1105@gmail.com', 'scrypt:32768:8:1$ip9PzF1MLPSlBwq5$b95146fd00b43c8e6ee5cf477b07188032d42411982b1811f9170e33beadb0f884db83318e06f2deff9a88febf411f2bceb70f7e41ea208546343b4290c98fb9', NULL, NULL),
(4, 'Sruthi', 'mannurusruthi@gmail.com', 'scrypt:32768:8:1$gItnADjFkiLD1j89$03b96ee0dd7b17a709e5c575760ec3fd94924c42d3b5b176ed423ce9f4c53a0582048d8a2c5560d32ba95663527f0a3c3f3e6db87f1fbd773297a5b89faaf303', NULL, NULL),
(7, 'Vyshu', 'vyshnavinarala12@gmail.com', 'scrypt:32768:8:1$aiXEOAu7WdOxkEFl$93779ca8b4c86eb87db20a0cae8ac186b21aa953b3f14f107414a64834ac40ab05337d1e82d51fbc7848af22b0d5cf374165df6451bf580ecc825c2c38f476e2', NULL, NULL),
(8, 'Chotu', 'kousikssvv34@gmail.com', 'scrypt:32768:8:1$Alvct8QMDmS4g0kq$a06c7cc9ebb7376a437a08ceff97a3d8fa59c75b6a7804ae5619e08f212b337dcfdf76f49445d7df7288911098b631b1739ab2e74dc888abe1fd849f67e2a3d9', NULL, NULL),
(9, 'Viraj Shambhu', 'sn3029769@gmail.com', 'scrypt:32768:8:1$jJTbyePVpy9jb001$b6f9eab7d018f7574d592e14e9d82000a03aaff23da98caded39416b027d6b999a812151685e9504716b1609e801ae6d68854a7fd636ba878dafe94ca54c20f4', NULL, NULL),
(10, 'Bhanu', 'nbhargavreddy@gmail.com', 'scrypt:32768:8:1$JiKTNGYnUTPmuGhN$9be1b7702cd3d3819f3a3f2e2940c3a3bbf04a5fb3052d29a212c2854034939914337c5a2875263dfde6521d7b44b8a82c71d5f5d25362cabca75d8f74726680', '7781', '2026-03-23 20:00:49'),
(11, 'Pavani', 'pavani@gmail.com', 'scrypt:32768:8:1$ey5BbhLUAktXLsH4$f819ae42bc0a8f33ee82466929ee1cf6536d1ea9345d2a257cb6019f529ea4efb3ba00fddbd526fabbad89669eb7460d2ddf9a625b6788be24bcb2c592210b03', NULL, NULL),
(12, 'KuKu', 'baby.keerthi26@gmail.com', 'scrypt:32768:8:1$5ml8N12huPRPpWVz$ad58f416f61acf9b6e844220d3510d98f0da5b37ba502b52e3bd5f9071b7653206b6a40b4b71581413b116f8f156c22d369476edd3893450d6f5d91b0c4467c3', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `shelf_lifespan`
--

CREATE TABLE `shelf_lifespan` (
  `item_name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `room_temperature` int(11) DEFAULT 0,
  `fridge` int(11) DEFAULT 0,
  `freezer` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `shelf_lifespan`
--

INSERT INTO `shelf_lifespan` (`item_name`, `category`, `room_temperature`, `fridge`, `freezer`) VALUES
('1% Milk', 'Dairy', 0, 7, 120),
('2% Milk', 'Dairy', 0, 7, 120),
('Acorn squash', 'Vegetables', 30, 14, 300),
('Allspice', 'Herbs & Seasonings', 1095, 1095, 1095),
('Amaranthus', 'Leafy Greens', 1, 7, 180),
('Anaheim peppers', 'Vegetables', 3, 7, 240),
('Anchovy', 'Meat & Seafood', 0, 2, 75),
('Anise', 'Herbs & Seasonings', 1095, 1095, 1095),
('Apple', 'Fruits', 7, 21, 240),
('Apricot', 'Fruits', 4, 5, 300),
('Artichoke', 'Vegetables', 2, 7, 240),
('Ash gourd', 'Vegetables', 30, 14, 300),
('Asparagus', 'Vegetables', 1, 5, 300),
('Avocado', 'Fruits', 6, 4, 135),
('Baby spinach', 'Leafy Greens', 1, 7, 180),
('Bacon', 'Meat & Seafood', 0, 7, 30),
('Banana', 'Fruits', 4, 6, 75),
('Basil', 'Herbs & Seasonings', 1, 7, 150),
('Bay Leaves', 'Herbs & Seasonings', 1095, 1095, 1095),
('Beef Ribs', 'Meat & Seafood', 0, 4, 270),
('Beef Roast', 'Meat & Seafood', 0, 4, 270),
('Beef Steak', 'Meat & Seafood', 0, 4, 270),
('Beet greens', 'Leafy Greens', 1, 7, 180),
('Beetroot', 'Vegetables', 2, 7, 240),
('Bison', 'Meat & Seafood', 0, 4, 270),
('Bitter gourd', 'Vegetables', 2, 7, 240),
('Black Pepper', 'Herbs & Seasonings', 1095, 1095, 1095),
('Blackberry', 'Fruits', 1, 5, 300),
('Blood Orange', 'Fruits', 7, 21, 240),
('Blue Cheese', 'Dairy', 0, 10, 180),
('Blueberry', 'Fruits', 1, 5, 300),
('Bok choy', 'Leafy Greens', 2, 10, 300),
('Bottle gourd', 'Vegetables', 2, 7, 240),
('Boysenberry', 'Fruits', 1, 5, 300),
('Brie Cheese', 'Dairy', 0, 10, 180),
('Brinjal', 'Vegetables', 2, 7, 240),
('Broad bean', 'Vegetables', 1, 5, 240),
('Broccoli', 'Vegetables', 2, 7, 300),
('Broccoli raab', 'Vegetables', 2, 7, 300),
('Broccolini', 'Vegetables', 2, 7, 300),
('Brown onion', 'Vegetables', 45, 30, 120),
('Brussels sprouts', 'Leafy Greens', 2, 10, 300),
('Butter lettuce', 'Leafy Greens', 1, 5, 0),
('Buttercup squash', 'Vegetables', 30, 14, 300),
('Buttermilk', 'Dairy', 0, 10, 60),
('Butternut squash', 'Vegetables', 30, 14, 300),
('Canary Melon', 'Fruits', 5, 5, 240),
('Cantaloupe', 'Fruits', 5, 5, 240),
('Capsicum', 'Vegetables', 3, 7, 240),
('Caraway seed', 'Herbs & Seasonings', 1095, 1095, 1095),
('Carrots', 'Vegetables', 3, 21, 300),
('Casaba Melon', 'Fruits', 5, 5, 240),
('Cassia Bark', 'Herbs & Seasonings', 1095, 1095, 1095),
('Catfish', 'Meat & Seafood', 0, 2, 75),
('Cauliflower', 'Vegetables', 2, 7, 300),
('Celeriac', 'Vegetables', 3, 21, 300),
('Celery', 'Leafy Greens', 2, 14, 300),
('Chamomile', 'Herbs & Seasonings', 2, 7, 180),
('Chard', 'Leafy Greens', 1, 7, 180),
('Cheddar Cheese', 'Dairy', 0, 21, 180),
('Cherimoya', 'Fruits', 3, 5, 240),
('Cherry', 'Fruits', 1, 7, 300),
('Chervil', 'Herbs & Seasonings', 1, 7, 150),
('Chicken Breast', 'Meat & Seafood', 0, 2, 270),
('Chicken Thighs', 'Meat & Seafood', 0, 2, 270),
('Chicken Wings', 'Meat & Seafood', 0, 2, 270),
('Chicory', 'Leafy Greens', 1, 5, 0),
('Chilli', 'Vegetables', 3, 7, 240),
('Chilli Pepper', 'Herbs & Seasonings', 1095, 1095, 1095),
('Chinese cabbage', 'Leafy Greens', 2, 10, 300),
('Chives', 'Herbs & Seasonings', 1, 7, 150),
('Christmas Melon', 'Fruits', 5, 5, 240),
('Cilantro', 'Herbs & Seasonings', 1, 7, 150),
('Cinnamon', 'Herbs & Seasonings', 1095, 1095, 1095),
('Clams', 'Meat & Seafood', 0, 5, 120),
('Clementine', 'Fruits', 7, 21, 240),
('Cluster bean', 'Vegetables', 1, 5, 240),
('Coconut', 'Fruits', 30, 7, 180),
('Cod', 'Meat & Seafood', 0, 2, 210),
('Collard greens', 'Leafy Greens', 1, 7, 180),
('Coriander Seeds', 'Herbs & Seasonings', 1095, 1095, 1095),
('Corn', 'Vegetables', 2, 7, 240),
('Cottage Cheese', 'Dairy', 0, 10, 90),
('Courgettes', 'Vegetables', 2, 7, 240),
('Cow pea', 'Vegetables', 1, 5, 240),
('Crab', 'Meat & Seafood', 0, 3, 120),
('Cranberry', 'Fruits', 1, 5, 300),
('Cream Cheese', 'Dairy', 0, 10, 60),
('Crenshaw Melon', 'Fruits', 5, 5, 240),
('Cress', 'Leafy Greens', 1, 7, 180),
('Crushed Red Pepper', 'Herbs & Seasonings', 1095, 1095, 1095),
('Cucumber', 'Vegetables', 2, 7, 240),
('Cumin Powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Currants', 'Fruits', 1, 5, 300),
('Curry leaves', 'Leafy Greens', 1, 7, 180),
('Curry Powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Daikon radish', 'Vegetables', 3, 21, 300),
('Dandelion greens', 'Leafy Greens', 1, 7, 180),
('Date', 'Fruits', 30, 180, 365),
('Dill', 'Herbs & Seasonings', 1, 7, 150),
('Dolichos bean', 'Vegetables', 1, 5, 240),
('Dragon Fruit', 'Fruits', 4, 5, 300),
('Drum stick', 'Vegetables', 2, 7, 240),
('Duck', 'Meat & Seafood', 0, 2, 365),
('Durian', 'Fruits', 3, 5, 240),
('Eggplant', 'Vegetables', 2, 7, 240),
('Elephant foot yam', 'Vegetables', 7, 14, 240),
('Endive lettuce', 'Leafy Greens', 1, 5, 0),
('Fenugreek', 'Herbs & Seasonings', 1095, 1095, 1095),
('Feta Cheese', 'Dairy', 0, 10, 180),
('Fig', 'Fruits', 1, 7, 300),
('French bean', 'Vegetables', 1, 5, 240),
('Fruit Yogurt', 'Dairy', 0, 10, 60),
('Garlic', 'Vegetables', 120, 30, 300),
('Garlic Powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Ghee', 'Dairy', 180, 365, 365),
('Ginger', 'Vegetables', 14, 30, 180),
('Ginger Powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Goose', 'Meat & Seafood', 0, 2, 365),
('Gooseberry', 'Fruits', 1, 5, 300),
('Gouda Cheese', 'Dairy', 0, 21, 180),
('Gourds', 'Vegetables', 2, 7, 240),
('Grapefruit', 'Fruits', 7, 21, 240),
('Grapes', 'Fruits', 1, 7, 300),
('Greek Yogurt', 'Dairy', 0, 10, 60),
('Green beans', 'Vegetables', 1, 5, 240),
('Green cabbage', 'Leafy Greens', 2, 10, 300),
('Green capsicum', 'Vegetables', 3, 7, 240),
('Green leaf lettuce', 'Leafy Greens', 1, 5, 0),
('Green onions', 'Vegetables', 2, 7, 240),
('Ground Beef', 'Meat & Seafood', 0, 2, 120),
('Ground Lamb', 'Meat & Seafood', 0, 2, 120),
('Ground Pork', 'Meat & Seafood', 0, 2, 120),
('Ground Turkey', 'Meat & Seafood', 0, 2, 120),
('Guava', 'Fruits', 4, 5, 300),
('Halibut', 'Meat & Seafood', 0, 2, 210),
('Halloumi', 'Dairy', 0, 10, 180),
('Ham', 'Meat & Seafood', 0, 5, 90),
('Heavy Cream', 'Dairy', 0, 4, 120),
('Honeydew Melon', 'Fruits', 5, 5, 240),
('Horned Melon', 'Fruits', 5, 5, 240),
('Iceberg lettuce', 'Leafy Greens', 1, 5, 0),
('Ivy gourd', 'Vegetables', 2, 7, 240),
('Jack Fruit', 'Fruits', 3, 5, 240),
('Jicama', 'Vegetables', 3, 21, 300),
('Jujube', 'Fruits', 3, 5, 240),
('Kale', 'Leafy Greens', 1, 7, 180),
('Kefir', 'Dairy', 0, 10, 60),
('Kiwi', 'Fruits', 4, 5, 300),
('Knol khol', 'Vegetables', 2, 7, 300),
('Kohlrabi', 'Vegetables', 2, 7, 300),
('Kumara', 'Vegetables', 14, 14, 330),
('Kumi kumi', 'Vegetables', 2, 7, 240),
('Kumquat', 'Fruits', 7, 21, 240),
('Lamb Chops', 'Meat & Seafood', 0, 4, 270),
('Lamb Leg', 'Meat & Seafood', 0, 4, 270),
('Lavender', 'Herbs & Seasonings', 2, 7, 180),
('Leeks', 'Vegetables', 2, 7, 240),
('Lemon', 'Fruits', 7, 21, 240),
('Lemongrass', 'Herbs & Seasonings', 1, 7, 150),
('Lettuce', 'Leafy Greens', 1, 5, 0),
('Light Cream', 'Dairy', 0, 4, 120),
('Lima bean', 'Vegetables', 1, 5, 240),
('Lime', 'Fruits', 7, 21, 240),
('Lobster', 'Meat & Seafood', 0, 3, 120),
('Loganberry', 'Fruits', 1, 5, 300),
('Longan', 'Fruits', 1, 7, 300),
('Loquat', 'Fruits', 3, 5, 240),
('Lychee', 'Fruits', 1, 7, 300),
('Mackerel', 'Meat & Seafood', 0, 2, 75),
('Mamoncillo', 'Fruits', 1, 7, 300),
('Mandarin', 'Fruits', 7, 21, 240),
('Mango', 'Fruits', 4, 6, 330),
('Mangosteen', 'Fruits', 3, 5, 240),
('Marjoram', 'Herbs & Seasonings', 2, 7, 180),
('Mascarpone', 'Dairy', 0, 10, 90),
('Minneola', 'Fruits', 7, 21, 240),
('Mint', 'Herbs & Seasonings', 1, 7, 150),
('Monterey Jack Cheese', 'Dairy', 0, 21, 180),
('Mozzarella Cheese', 'Dairy', 0, 10, 180),
('Mulberry', 'Fruits', 1, 5, 300),
('Mushrooms', 'Vegetables', 1, 5, 240),
('Musk Melon', 'Fruits', 5, 5, 240),
('Mussels', 'Meat & Seafood', 0, 5, 120),
('Mustard greens', 'Leafy Greens', 1, 7, 180),
('Mustard Seed Powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Nance', 'Fruits', 3, 5, 240),
('Napa cabbage', 'Leafy Greens', 2, 10, 300),
('Nectarine', 'Fruits', 4, 5, 300),
('Nutmeg', 'Herbs & Seasonings', 1095, 1095, 1095),
('Octopus', 'Meat & Seafood', 0, 3, 180),
('Okra', 'Vegetables', 2, 7, 240),
('Onion', 'Vegetables', 45, 30, 120),
('Onion powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Orange', 'Fruits', 7, 21, 240),
('Oregano', 'Herbs & Seasonings', 2, 7, 180),
('Paneer', 'Dairy', 0, 10, 180),
('Papaya', 'Fruits', 4, 5, 300),
('Paprika', 'Herbs & Seasonings', 1095, 1095, 1095),
('Parmesan Cheese', 'Dairy', 0, 30, 365),
('Parsley', 'Herbs & Seasonings', 1, 7, 150),
('Parsnips', 'Vegetables', 3, 21, 300),
('Passion Fruit', 'Fruits', 4, 5, 300),
('Patti pan squash', 'Vegetables', 2, 7, 240),
('Peach', 'Fruits', 2, 4, 330),
('Pear', 'Fruits', 3, 6, 330),
('Peas', 'Vegetables', 1, 5, 240),
('Persimmon', 'Fruits', 4, 5, 300),
('Pineapple', 'Fruits', 4, 5, 300),
('Plain Yogurt', 'Dairy', 0, 10, 60),
('Plum', 'Fruits', 4, 5, 300),
('Pointed gourd', 'Vegetables', 2, 7, 240),
('Pomegranate', 'Fruits', 7, 21, 240),
('Pommelo', 'Fruits', 7, 21, 240),
('Pork Chops', 'Meat & Seafood', 0, 4, 270),
('Pork Ribs', 'Meat & Seafood', 0, 4, 270),
('Pork Tenderloin', 'Meat & Seafood', 0, 4, 270),
('Potato', 'Vegetables', 14, 28, 300),
('Prawns', 'Meat & Seafood', 0, 3, 180),
('Prickly (cactus) Pear', 'Fruits', 4, 5, 300),
('Provolone Cheese', 'Dairy', 0, 21, 180),
('Puha', 'Leafy Greens', 1, 7, 180),
('Pulasan', 'Fruits', 1, 7, 300),
('Pumpkin', 'Vegetables', 30, 14, 300),
('Purple beans', 'Vegetables', 1, 5, 240),
('Purple carrots', 'Vegetables', 3, 21, 300),
('Purple cauliflower', 'Vegetables', 2, 7, 300),
('Purple kumara', 'Vegetables', 14, 14, 330),
('Quince', 'Fruits', 4, 5, 300),
('Radicchio', 'Leafy Greens', 1, 5, 0),
('Rambutan', 'Fruits', 1, 7, 300),
('Raspberry', 'Fruits', 1, 5, 300),
('Red cabbage', 'Leafy Greens', 2, 10, 300),
('Red Capsicum', 'Vegetables', 3, 7, 240),
('Red kumara', 'Vegetables', 14, 14, 330),
('Red leaf lettuce', 'Leafy Greens', 1, 5, 0),
('Red onions', 'Vegetables', 45, 30, 120),
('Red Radish', 'Vegetables', 3, 21, 300),
('Rhubarb', 'Leafy Greens', 2, 14, 300),
('Ricotta', 'Dairy', 0, 10, 90),
('Ridge gourd', 'Vegetables', 2, 7, 240),
('Romaine lettuce', 'Leafy Greens', 1, 5, 0),
('Romanesco', 'Vegetables', 2, 7, 300),
('Rosemary', 'Herbs & Seasonings', 2, 7, 180),
('Rutabaga', 'Vegetables', 3, 21, 300),
('Saffron', 'Herbs & Seasonings', 1095, 1095, 1095),
('Sage', 'Herbs & Seasonings', 2, 7, 180),
('Salad greens', 'Leafy Greens', 1, 5, 0),
('Salmon - Atlantic', 'Meat & Seafood', 0, 2, 75),
('Salmon - Wild', 'Meat & Seafood', 0, 2, 75),
('Salt', 'Herbs & Seasonings', 3650, 3650, 3650),
('Salted Butter', 'Dairy', 2, 90, 365),
('Sardines', 'Meat & Seafood', 0, 2, 75),
('Satsuma', 'Fruits', 7, 21, 240),
('Sausage', 'Meat & Seafood', 0, 2, 60),
('Savory', 'Herbs & Seasonings', 2, 7, 180),
('Savoy cabbage', 'Leafy Greens', 2, 10, 300),
('Scallops', 'Meat & Seafood', 0, 3, 120),
('Sea Bass', 'Meat & Seafood', 0, 2, 210),
('Shallots', 'Vegetables', 45, 30, 120),
('Shrimp', 'Meat & Seafood', 0, 3, 180),
('Silverbeet', 'Leafy Greens', 1, 7, 180),
('Skim Milk', 'Dairy', 0, 7, 120),
('Snake gourd', 'Vegetables', 2, 7, 240),
('Snap sugar peas', 'Vegetables', 1, 5, 240),
('Snapper', 'Meat & Seafood', 0, 2, 210),
('Snow peas', 'Vegetables', 1, 5, 240),
('Sour Cream', 'Dairy', 0, 14, 60),
('Soursop', 'Fruits', 3, 5, 240),
('Spaghetti squash', 'Vegetables', 30, 14, 300),
('Spinach', 'Leafy Greens', 1, 7, 180),
('Spine gourd', 'Vegetables', 2, 7, 240),
('Sponge gourd', 'Vegetables', 2, 7, 240),
('Squash', 'Vegetables', 2, 7, 240),
('Squid', 'Meat & Seafood', 0, 3, 180),
('Starfruit', 'Fruits', 4, 5, 300),
('Stevia', 'Herbs & Seasonings', 1, 7, 150),
('Strawberry', 'Fruits', 1, 5, 300),
('Swede', 'Vegetables', 3, 21, 300),
('Sweet corn', 'Vegetables', 2, 7, 240),
('Sweet peppers', 'Vegetables', 3, 7, 240),
('Sweet potato', 'Vegetables', 14, 14, 330),
('Swiss Cheese', 'Dairy', 0, 21, 180),
('Swordfish', 'Meat & Seafood', 0, 2, 210),
('Tamarillo', 'Fruits', 4, 5, 300),
('Tangelo', 'Fruits', 7, 21, 240),
('Tangerine', 'Fruits', 7, 21, 240),
('Tapioca', 'Vegetables', 7, 14, 240),
('Taro', 'Vegetables', 7, 14, 240),
('Tarragon', 'Herbs & Seasonings', 1, 7, 150),
('Thyme', 'Herbs & Seasonings', 2, 7, 180),
('Tilapia', 'Meat & Seafood', 0, 2, 210),
('Tomatillo', 'Vegetables', 4, 5, 240),
('Tomato', 'Vegetables', 4, 5, 240),
('Trout', 'Meat & Seafood', 0, 2, 75),
('Tuna', 'Meat & Seafood', 0, 2, 75),
('Turkey Breast', 'Meat & Seafood', 0, 2, 270),
('Turmeric Powder', 'Herbs & Seasonings', 1095, 1095, 1095),
('Turnip greens', 'Leafy Greens', 1, 7, 180),
('Turnips', 'Vegetables', 3, 21, 300),
('Ugli fruit', 'Fruits', 7, 21, 240),
('Unsalted Butter', 'Dairy', 1, 60, 180),
('Vanilla Yogurt', 'Dairy', 0, 10, 60),
('Veal', 'Meat & Seafood', 0, 4, 270),
('Venison', 'Meat & Seafood', 0, 4, 270),
('Water chestnuts', 'Vegetables', 2, 7, 240),
('Watercress', 'Leafy Greens', 1, 7, 180),
('Watermelon', 'Fruits', 7, 14, 240),
('Whipped Cream', 'Dairy', 0, 4, 120),
('Whitloof', 'Leafy Greens', 1, 5, 0),
('Whole Chicken', 'Meat & Seafood', 0, 2, 365),
('Whole Milk', 'Dairy', 0, 7, 120),
('Wing bean', 'Vegetables', 1, 5, 240),
('Winter Savory', 'Herbs & Seasonings', 2, 7, 180),
('Wongbok', 'Leafy Greens', 2, 10, 300),
('Yam', 'Vegetables', 7, 14, 240),
('Yellow carrots', 'Vegetables', 3, 21, 300),
('Zucchini', 'Vegetables', 2, 7, 240);

-- --------------------------------------------------------

--
-- Table structure for table `shelf_life_data`
--

CREATE TABLE `shelf_life_data` (
  `item_name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `room_temperature` int(11) DEFAULT 0,
  `fridge` int(11) DEFAULT 0,
  `frezzer` int(11) DEFAULT 0,
  `freezer` int(11) DEFAULT 30
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shelf_life_data`
--

INSERT INTO `shelf_life_data` (`item_name`, `category`, `room_temperature`, `fridge`, `frezzer`, `freezer`) VALUES
('Apple', NULL, 21, 30, 240, 240),
('Asparagus', NULL, 1, 4, 300, 240),
('Avocado', NULL, 3, 7, 180, 180),
('Bacon', NULL, 0, 7, 30, 30),
('Banana', NULL, 7, 5, 60, 60),
('Basil', NULL, 4, 4, 0, 30),
('Beef', NULL, 0, 3, 270, 270),
('Bell Pepper', NULL, 3, 7, 300, 240),
('Blueberry', NULL, 1, 10, 365, 365),
('Bread', NULL, 5, 7, 90, 90),
('Broccoli', NULL, 2, 5, 300, 300),
('Butter', NULL, 2, 90, 180, 270),
('Cabbage', NULL, 7, 21, 300, 300),
('Carrot', NULL, 7, 28, 300, 300),
('Cauliflower', NULL, 2, 7, 300, 300),
('Celery', NULL, 3, 14, 300, 300),
('Cheese (Hard)', NULL, 1, 60, 180, 180),
('Cheese (Soft)', NULL, 0, 7, 30, 90),
('Cherry', NULL, 2, 7, 0, 300),
('Chicken', NULL, 0, 2, 270, 270),
('Cilantro', NULL, 1, 7, 0, 30),
('Cooked Pasta', NULL, 0, 5, 180, 30),
('Cooked Rice', NULL, 0, 4, 180, 30),
('Corn', NULL, 1, 2, 300, 240),
('Cream', NULL, 0, 7, 0, 120),
('Cucumber', NULL, 5, 7, 0, 180),
('Deli Meat', NULL, 0, 3, 30, 30),
('Egg', NULL, 7, 30, 30, 30),
('Eggplant', NULL, 3, 5, 300, 180),
('Eggs', NULL, 1, 35, 0, 300),
('Fish', NULL, 0, 2, 180, 180),
('Flour', NULL, 180, 365, 730, 30),
('Garlic', NULL, 120, 30, 300, 300),
('Ginger', NULL, 21, 60, 180, 30),
('Grapefruit', NULL, 14, 21, 0, 180),
('Grapes', NULL, 2, 14, 300, 300),
('Green Beans', NULL, 2, 7, 0, 240),
('Ground Meat', NULL, 0, 2, 120, 30),
('Kiwi', NULL, 5, 14, 300, 300),
('Lemon', NULL, 14, 30, 180, 180),
('Lettuce', NULL, 1, 7, 0, 30),
('Mango', NULL, 5, 7, 180, 180),
('Milk', NULL, 0, 7, 30, 90),
('Mint', NULL, 1, 7, 0, 30),
('Mushroom', NULL, 1, 7, 0, 240),
('Onion', NULL, 60, 30, 300, 300),
('Orange', NULL, 14, 21, 180, 180),
('Parsley', NULL, 1, 7, 0, 30),
('Pasta (Dry)', NULL, 365, 730, 730, 30),
('Peach', NULL, 2, 5, 300, 300),
('Pear', NULL, 4, 7, 300, 300),
('Peas', NULL, 1, 5, 0, 240),
('Pineapple', NULL, 3, 5, 300, 180),
('Plum', NULL, 3, 5, 0, 300),
('Pomegranate', NULL, 14, 30, 0, 300),
('Pork', NULL, 0, 3, 180, 270),
('Potato', NULL, 60, 14, 300, 300),
('Raspberry', NULL, 1, 2, 365, 365),
('Rice (Dry)', NULL, 365, 730, 730, 30),
('Rosemary', NULL, 3, 14, 0, 30),
('Sausage', NULL, 0, 2, 60, 60),
('Shrimp', NULL, 0, 2, 0, 180),
('Spinach', NULL, 1, 4, 300, 240),
('Strawberry', NULL, 1, 3, 300, 300),
('Sweet Potato', NULL, 60, 14, 0, 300),
('Tomato', NULL, 7, 5, 90, 90),
('Tortillas', NULL, 14, 30, 0, 180),
('Watermelon', NULL, 7, 5, 300, 300),
('Yogurt', NULL, 0, 14, 30, 60),
('Zucchini', NULL, 3, 5, 300, 240);

-- --------------------------------------------------------

--
-- Table structure for table `user_alert_settings`
--

CREATE TABLE `user_alert_settings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `expiry_days_before` int(11) DEFAULT 3,
  `expiry_alert_time` time DEFAULT '09:00:00',
  `weekly_summary_enabled` tinyint(1) DEFAULT 1,
  `weekly_summary_day` varchar(20) DEFAULT 'Sunday',
  `weekly_summary_time` time DEFAULT '09:00:00',
  `critical_alert_enabled` tinyint(1) DEFAULT 1,
  `critical_alert_time` time DEFAULT '09:00:00',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_enabled` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_alert_settings`
--

INSERT INTO `user_alert_settings` (`id`, `user_id`, `expiry_days_before`, `expiry_alert_time`, `weekly_summary_enabled`, `weekly_summary_day`, `weekly_summary_time`, `critical_alert_enabled`, `critical_alert_time`, `created_at`, `updated_at`, `is_enabled`) VALUES
(1, 2, 2, '10:53:00', 1, 'Thursday', '10:53:00', 1, '10:53:00', '2026-03-09 14:27:50', '2026-03-19 13:09:15', 1),
(2, 1, 1, '18:00:00', 0, 'Sunday', '09:00:00', 1, '09:00:00', '2026-03-09 14:28:03', '2026-03-09 14:28:03', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_notifications_user_type_created` (`user_id`,`type`,`created_at`),
  ADD KEY `fk_notifications_pantry_item` (`pantry_item_id`);

--
-- Indexes for table `pantry_items`
--
ALTER TABLE `pantry_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_pantry_user_status_expiry` (`user_id`,`status`,`expiry_date`);

--
-- Indexes for table `register`
--
ALTER TABLE `register`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_register_email` (`email`);

--
-- Indexes for table `shelf_lifespan`
--
ALTER TABLE `shelf_lifespan`
  ADD PRIMARY KEY (`item_name`);

--
-- Indexes for table `shelf_life_data`
--
ALTER TABLE `shelf_life_data`
  ADD PRIMARY KEY (`item_name`);

--
-- Indexes for table `user_alert_settings`
--
ALTER TABLE `user_alert_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_alert_settings_user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=79;

--
-- AUTO_INCREMENT for table `pantry_items`
--
ALTER TABLE `pantry_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=132;

--
-- AUTO_INCREMENT for table `register`
--
ALTER TABLE `register`
  MODIFY `id` int(190) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `user_alert_settings`
--
ALTER TABLE `user_alert_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `fk_notifications_item` FOREIGN KEY (`pantry_item_id`) REFERENCES `pantry_items` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_notifications_pantry_item` FOREIGN KEY (`pantry_item_id`) REFERENCES `pantry_items` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `pantry_items`
--
ALTER TABLE `pantry_items`
  ADD CONSTRAINT `fk_pantry_items_user` FOREIGN KEY (`user_id`) REFERENCES `register` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `pantry_items_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_alert_settings`
--
ALTER TABLE `user_alert_settings`
  ADD CONSTRAINT `fk_user_alert_settings_user` FOREIGN KEY (`user_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
