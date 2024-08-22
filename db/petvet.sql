-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-08-2024 a las 22:57:55
-- Versión del servidor: 10.1.37-MariaDB
-- Versión de PHP: 7.2.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `petvet`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `admin`
--

CREATE TABLE `admin` (
  `id_admin` int(11) NOT NULL,
  `id_domicilio` int(11) NOT NULL,
  `id_citas` int(11) NOT NULL,
  `id_guarderia` int(11) NOT NULL,
  `id_adopcion` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `adopcion`
--

CREATE TABLE `adopcion` (
  `id_adopcion` int(11) NOT NULL,
  `nombre` varchar(50) COLLATE utf8_spanish_ci NOT NULL,
  `descripcion` varchar(120) COLLATE utf8_spanish_ci NOT NULL,
  `edad` int(2) NOT NULL,
  `sexo` varchar(15) COLLATE utf8_spanish_ci NOT NULL,
  `foto_mascota` blob NOT NULL,
  `peso` varchar(5) COLLATE utf8_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `adopcion`
--

INSERT INTO `adopcion` (`id_adopcion`, `nombre`, `descripcion`, `edad`, `sexo`, `foto_mascota`, `peso`) VALUES
(1, 'rocky', 'wetdsgfds', 4, 'hembra', 0x6c6f2e6a7067, ''),
(2, 'toby', 'perro bacano', 4, 'hembra', 0x70657266696c2e6a7067, ''),
(3, 'cali', 'es bueno', 2, 'macho', 0x6c6f2e6a7067, ''),
(4, 'sancocho', 'es bueno', 2, 'hembra', 0x70657266696c2e6a7067, '2'),
(5, 'rocky2', 'es rocky2', 2, 'hembra', 0x6c6f2e6a7067, '2');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `citas`
--

CREATE TABLE `citas` (
  `id_citas` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `tanda` varchar(15) COLLATE utf8_spanish_ci NOT NULL,
  `id_mascota` int(11) NOT NULL,
  `id_servicios` int(11) NOT NULL,
  `descripcion` varchar(200) COLLATE utf8_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `citas`
--

INSERT INTO `citas` (`id_citas`, `id_usuario`, `fecha`, `tanda`, `id_mascota`, `id_servicios`, `descripcion`) VALUES
(26, 1, '2024-08-09', 'Tarde', 2, 6, 'hhhhahdwferfqerf'),
(28, 1, '2024-08-16', 'Tarde', 2, 6, ' wdWD');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `domicilio`
--sql


CREATE TABLE `domicilio` (
  `id_adomicilio` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `direccion` varchar(200) COLLATE utf8_spanish_ci NOT NULL,
  `tanda` varchar(15) COLLATE utf8_spanish_ci NOT NULL,
  `id_mascota` int(11) NOT NULL,
  `id_vacuna` int(11) NOT NULL,
  `id_servicio` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `guarderia`
--

CREATE TABLE `guarderia` (
  `id_guarderia` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_servicios` int(11) NOT NULL,
  `desde` varchar(15) COLLATE utf8_spanish_ci NOT NULL,
  `hasta` varchar(15) COLLATE utf8_spanish_ci NOT NULL,
  `id_mascota` int(11) NOT NULL,
  `descripcion` varchar(200) COLLATE utf8_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `guarderia`
--

INSERT INTO `guarderia` (`id_guarderia`, `id_usuario`, `id_servicios`, `desde`, `hasta`, `id_mascota`, `descripcion`) VALUES
(1, 1, 5, '2024-08-08', '2024-09-05', 2, 'bcdbfuaebgre'),
(2, 1, 5, '2024-08-08', '2024-08-22', 3, 'bbbbbbbb'),
(3, 4, 5, '2024-08-02', '2024-08-01', 5, 'vvvvvvvvvvvv'),
(4, 4, 5, '2024-08-03', '2024-08-29', 5, 'cccccc');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mascota`
--

CREATE TABLE `mascota` (
  `id_mascota` int(11) NOT NULL,
  `tipoMascota` varchar(50) COLLATE utf8_spanish_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `mascota`
--

INSERT INTO `mascota` (`id_mascota`, `tipoMascota`) VALUES
(1, 'Perro'),
(2, 'Gato'),
(3, 'Roedor'),
(4, 'Ave'),
(5, 'Otro');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_admin` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `servicio`
--

CREATE TABLE `servicio` (
  `id_servicios` int(11) NOT NULL,
  `servicio` varchar(50) COLLATE utf8_spanish_ci NOT NULL,
  `precio` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `servicio`
--

INSERT INTO `servicio` (`id_servicios`, `servicio`, `precio`) VALUES
(1, 'Baño a domicilio ', 1500),
(2, 'Paseos a mascotas', 500),
(3, 'Corte de uñas ', 500),
(4, 'Revisiones físicas', 700),
(5, 'Hospedaje y cuidado de mascota', 0),
(6, 'Chequeo General', 0),
(7, 'Vacunación y Medicación', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `apellido` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `fecha_nacimiento` varchar(15) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `telefono` varchar(15) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `sexo` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `id_mascota` int(11) NOT NULL,
  `correo` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `contraseña` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `verificar_contraseña` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `foto_perfil` varchar(255) COLLATE utf8_spanish2_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish2_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `nombre`, `apellido`, `fecha_nacimiento`, `telefono`, `sexo`, `id_mascota`, `correo`, `contraseña`, `verificar_contraseña`, `foto_perfil`) VALUES
(1, 'Tiara', 'Peña', '2024-08-14', '8298427894', 'femenino', 1, 'tiara12p@gmail.com', '123', '', 'goku.jpg'),
(2, 'yohan', 'perez', '2024-08-30', '8294890987', 'masculino', 2, 'yohan@gamil.com', '12345', '', NULL),
(3, 'Camil', 'Cedeno', '2006-06-21', '8298427894', 'femenino', 4, 'camil@gmail.com', '123', '', NULL),
(4, 'laura', 'cabrera', '2024-08-01', '0987654321', 'femenino', 2, 'la@gamil.com', '12', '', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vacuna`
--

CREATE TABLE `vacuna` (
  `id_vacuna` int(11) NOT NULL,
  `vacuna` varchar(50) COLLATE utf8_spanish_ci NOT NULL,
  `precio` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Volcado de datos para la tabla `vacuna`
--

INSERT INTO `vacuna` (`id_vacuna`, `vacuna`, `precio`) VALUES
(1, 'Vacuna contra la rabia', 500),
(2, 'Vacuna contra el parvovirus', 500),
(3, 'Vacuna contra el moquillo ', 500),
(4, 'Vacuna refuerzo a polivalente', 600),
(5, 'Vacuna contra Lyme', 800);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id_admin`),
  ADD KEY `id_domicilio` (`id_domicilio`,`id_citas`,`id_guarderia`,`id_adopcion`),
  ADD KEY `id_citas` (`id_citas`),
  ADD KEY `id_adopcion` (`id_adopcion`),
  ADD KEY `id_guarderia` (`id_guarderia`);

--
-- Indices de la tabla `adopcion`
--
ALTER TABLE `adopcion`
  ADD PRIMARY KEY (`id_adopcion`);

--
-- Indices de la tabla `citas`
--
ALTER TABLE `citas`
  ADD PRIMARY KEY (`id_citas`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_mascota` (`id_mascota`),
  ADD KEY `id_tanda` (`id_servicios`);

--
-- Indices de la tabla `domicilio`
--
ALTER TABLE `domicilio`
  ADD PRIMARY KEY (`id_adomicilio`),
  ADD KEY `id_usuario` (`id_usuario`,`id_mascota`,`id_vacuna`,`id_servicio`),
  ADD KEY `id_vacuna` (`id_vacuna`),
  ADD KEY `id_servicio` (`id_servicio`),
  ADD KEY `id_mascota` (`id_mascota`);

--
-- Indices de la tabla `guarderia`
--
ALTER TABLE `guarderia`
  ADD PRIMARY KEY (`id_guarderia`),
  ADD KEY `id_usuario` (`id_usuario`,`id_servicios`,`id_mascota`),
  ADD KEY `id_servicio` (`id_servicios`),
  ADD KEY `id_mascota` (`id_mascota`);

--
-- Indices de la tabla `mascota`
--
ALTER TABLE `mascota`
  ADD PRIMARY KEY (`id_mascota`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id_rol`),
  ADD KEY `id_usuario` (`id_usuario`,`id_admin`),
  ADD KEY `id_admin` (`id_admin`);

--
-- Indices de la tabla `servicio`
--
ALTER TABLE `servicio`
  ADD PRIMARY KEY (`id_servicios`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`),
  ADD KEY `id_mascota` (`id_mascota`),
  ADD KEY `id_mascota_2` (`id_mascota`),
  ADD KEY `id_mascota_3` (`id_mascota`);

--
-- Indices de la tabla `vacuna`
--
ALTER TABLE `vacuna`
  ADD PRIMARY KEY (`id_vacuna`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `admin`
--
ALTER TABLE `admin`
  MODIFY `id_admin` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `adopcion`
--
ALTER TABLE `adopcion`
  MODIFY `id_adopcion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `citas`
--
ALTER TABLE `citas`
  MODIFY `id_citas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT de la tabla `domicilio`
--
ALTER TABLE `domicilio`
  MODIFY `id_adomicilio` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `guarderia`
--
ALTER TABLE `guarderia`
  MODIFY `id_guarderia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `mascota`
--
ALTER TABLE `mascota`
  MODIFY `id_mascota` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `rol`
--
ALTER TABLE `rol`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `servicio`
--
ALTER TABLE `servicio`
  MODIFY `id_servicios` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `vacuna`
--
ALTER TABLE `vacuna`
  MODIFY `id_vacuna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `admin`
--
ALTER TABLE `admin`
  ADD CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`id_citas`) REFERENCES `citas` (`id_citas`),
  ADD CONSTRAINT `admin_ibfk_2` FOREIGN KEY (`id_adopcion`) REFERENCES `adopcion` (`id_adopcion`),
  ADD CONSTRAINT `admin_ibfk_3` FOREIGN KEY (`id_guarderia`) REFERENCES `guarderia` (`id_guarderia`),
  ADD CONSTRAINT `admin_ibfk_4` FOREIGN KEY (`id_domicilio`) REFERENCES `domicilio` (`id_adomicilio`);

--
-- Filtros para la tabla `citas`
--
ALTER TABLE `citas`
  ADD CONSTRAINT `citas_ibfk_1` FOREIGN KEY (`id_servicios`) REFERENCES `servicio` (`id_servicios`),
  ADD CONSTRAINT `citas_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`),
  ADD CONSTRAINT `citas_ibfk_3` FOREIGN KEY (`id_mascota`) REFERENCES `mascota` (`id_mascota`);

--
-- Filtros para la tabla `domicilio`
--
ALTER TABLE `domicilio`
  ADD CONSTRAINT `domicilio_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`),
  ADD CONSTRAINT `domicilio_ibfk_2` FOREIGN KEY (`id_vacuna`) REFERENCES `vacuna` (`id_vacuna`),
  ADD CONSTRAINT `domicilio_ibfk_3` FOREIGN KEY (`id_mascota`) REFERENCES `mascota` (`id_mascota`),
  ADD CONSTRAINT `domicilio_ibfk_4` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicios`);

--
-- Filtros para la tabla `guarderia`
--
ALTER TABLE `guarderia`
  ADD CONSTRAINT `guarderia_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`),
  ADD CONSTRAINT `guarderia_ibfk_2` FOREIGN KEY (`id_servicios`) REFERENCES `servicio` (`id_servicios`),
  ADD CONSTRAINT `guarderia_ibfk_3` FOREIGN KEY (`id_mascota`) REFERENCES `mascota` (`id_mascota`);

--
-- Filtros para la tabla `rol`
--
ALTER TABLE `rol`
  ADD CONSTRAINT `rol_ibfk_1` FOREIGN KEY (`id_admin`) REFERENCES `admin` (`id_admin`),
  ADD CONSTRAINT `rol_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_mascota`) REFERENCES `mascota` (`id_mascota`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
