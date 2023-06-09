-- MySQL Script generated by MySQL Workbench
-- Tue Jun 27 18:40:41 2023
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema db_sistema
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema db_sistema
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `db_sistema` DEFAULT CHARACTER SET utf8 ;
USE `db_sistema` ;

-- -----------------------------------------------------
-- Table `db_sistema`.`cohortes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`cohortes` (
  `cohorte_id` INT NOT NULL AUTO_INCREMENT,
  `cohorte_inicio` INT(4) NOT NULL,
  `cohorte_fin` INT(4) NOT NULL,
  PRIMARY KEY (`cohorte_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`alumnos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`alumnos` (
  `matricula` INT NOT NULL,
  `alumno_nombre` VARCHAR(80) NOT NULL,
  `cohorte_id` INT NOT NULL,
  PRIMARY KEY (`matricula`),
  INDEX `fk_alumnos_cohortes_idx` (`cohorte_id` ASC) VISIBLE,
  CONSTRAINT `fk_alumnos_cohortes`
    FOREIGN KEY (`cohorte_id`)
    REFERENCES `db_sistema`.`cohortes` (`cohorte_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`semestre`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`semestre` (
  `semestre` INT NOT NULL,
  PRIMARY KEY (`semestre`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`materias`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`materias` (
  `materia_codigo` VARCHAR(10) NOT NULL,
  `materia_descripcion` VARCHAR(45) NOT NULL,
  `semestre` INT NOT NULL,
  PRIMARY KEY (`materia_codigo`),
  INDEX `fk_materias_semestre1_idx` (`semestre` ASC) VISIBLE,
  CONSTRAINT `fk_materias_semestre1`
    FOREIGN KEY (`semestre`)
    REFERENCES `db_sistema`.`semestre` (`semestre`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`historial`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`historial` (
  `historia_id` INT NOT NULL AUTO_INCREMENT,
  `matricula` INT NOT NULL,
  `materia_codigo` VARCHAR(10) NOT NULL,
  `nota` INT(1) NOT NULL,
  `oportunidad` INT(4) NOT NULL,
  `fecha_examen` DATE NOT NULL,
  PRIMARY KEY (`historia_id`, `matricula`, `materia_codigo`),
  INDEX `fk_alumnos_has_materias_materias1_idx` (`materia_codigo` ASC) VISIBLE,
  INDEX `fk_alumnos_has_materias_alumnos1_idx` (`matricula` ASC) VISIBLE,
  CONSTRAINT `fk_alumnos_has_materias_alumnos1`
    FOREIGN KEY (`matricula`)
    REFERENCES `db_sistema`.`alumnos` (`matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_alumnos_has_materias_materias1`
    FOREIGN KEY (`materia_codigo`)
    REFERENCES `db_sistema`.`materias` (`materia_codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`estados`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`estados` (
  `estado_id` INT NOT NULL AUTO_INCREMENT,
  `estado_descript` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`estado_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`cantidad_inscripciones`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`cantidad_inscripciones` (
  `cohorte_id` INT NOT NULL,
  `semestre` INT NOT NULL,
  `cantidad` INT NOT NULL,
  PRIMARY KEY (`cohorte_id`, `semestre`),
  INDEX `fk_cohortes_has_semestre_semestre1_idx` (`semestre` ASC) VISIBLE,
  INDEX `fk_cohortes_has_semestre_cohortes1_idx` (`cohorte_id` ASC) VISIBLE,
  CONSTRAINT `fk_cohortes_has_semestre_cohortes1`
    FOREIGN KEY (`cohorte_id`)
    REFERENCES `db_sistema`.`cohortes` (`cohorte_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_cohortes_has_semestre_semestre1`
    FOREIGN KEY (`semestre`)
    REFERENCES `db_sistema`.`semestre` (`semestre`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `db_sistema`.`estados_alumnos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `db_sistema`.`estados_alumnos` (
  `matricula` INT NOT NULL,
  `semestre` INT NOT NULL,
  `estado_id` INT NOT NULL,
  PRIMARY KEY (`matricula`, `semestre`),
  INDEX `fk_alumnos_has_semestre_semestre1_idx` (`semestre` ASC) VISIBLE,
  INDEX `fk_alumnos_has_semestre_alumnos1_idx` (`matricula` ASC) VISIBLE,
  INDEX `fk_estados_alumnos_estados1_idx` (`estado_id` ASC) VISIBLE,
  CONSTRAINT `fk_alumnos_has_semestre_alumnos1`
    FOREIGN KEY (`matricula`)
    REFERENCES `db_sistema`.`alumnos` (`matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_alumnos_has_semestre_semestre1`
    FOREIGN KEY (`semestre`)
    REFERENCES `db_sistema`.`semestre` (`semestre`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_estados_alumnos_estados1`
    FOREIGN KEY (`estado_id`)
    REFERENCES `db_sistema`.`estados` (`estado_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
