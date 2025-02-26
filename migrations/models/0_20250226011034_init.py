from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `email` VARCHAR(255),
    `full_name` VARCHAR(255)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `hash` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `hashed_password` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_hash_user_63358389` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `recipe` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` LONGTEXT NOT NULL,
    `ingredients` JSON NOT NULL,
    `preparation` LONGTEXT,
    `duration` LONGTEXT,
    `schedule_at` DATE NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_recipe_user_253db62e` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
