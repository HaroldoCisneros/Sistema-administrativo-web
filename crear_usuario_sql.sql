-- =============================================================================
-- crear_usuario_sql.sql
-- Usuario de SQL Server para el Sistema Administrativo.
-- Ejecutar en SQL Server Management Studio con un usuario administrador.
--
-- Antes de ejecutar:
--   1. Cambie CAMBIAR_CLAVE por una clave segura (la misma que va en config.xml).
--   2. En el paso 4, cambie NOMBRE_BASE_PROFIT por la base de Profit de la
--      empresa. Si hay varias empresas, repita el bloque del paso 4 por cada una.
-- =============================================================================

-- 1) Base propia del sistema (usuarios, sesiones, empresas...)
IF DB_ID(N'SIGHEC') IS NULL
    CREATE DATABASE [SIGHEC];
GO

-- 2) Login del sistema
IF SUSER_ID(N'sighec') IS NULL
    CREATE LOGIN [sighec] WITH PASSWORD = N'CAMBIAR_CLAVE', CHECK_POLICY = ON;
GO

-- 3) En su propia base: control total (Django crea ahí sus tablas con "migrate")
USE [SIGHEC];
IF USER_ID(N'sighec') IS NULL CREATE USER [sighec] FOR LOGIN [sighec];
ALTER ROLE db_owner ADD MEMBER [sighec];
GO

-- 4) En la base de Profit de CADA empresa: SOLO LECTURA (por ahora)
--    + ejecutar el procedimiento de tasas de cambio.
--    (Repetir este bloque cambiando el nombre de la base por cada empresa.)
USE [NOMBRE_BASE_PROFIT];
IF USER_ID(N'sighec') IS NULL CREATE USER [sighec] FOR LOGIN [sighec];
ALTER ROLE db_datareader ADD MEMBER [sighec];
GRANT EXECUTE ON [dbo].[pp_valor_moneda] TO [sighec];
GO

-- 5) En MasterProfit: solo leer la tabla de usuarios (para el inicio de sesión)
USE [MasterProfit];
IF USER_ID(N'sighec') IS NULL CREATE USER [sighec] FOR LOGIN [sighec];
GRANT SELECT ON [dbo].[employee] TO [sighec];
GO
