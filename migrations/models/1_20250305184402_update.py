from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `recipe_user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `recipe_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_recipe_u_recipe_20aeeb28` FOREIGN KEY (`recipe_id`) 
    REFERENCES `recipe` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_recipe_u_user_36659ae5` FOREIGN KEY (`user_id`) 
    REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `recipe_user`;"""
