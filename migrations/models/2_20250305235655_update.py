from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `recipe_user` 
        ADD UNIQUE INDEX `uid_recipe_user_user_id_ba92bf` 
        (`user_id`, `recipe_id`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `recipe_user` DROP INDEX `uid_recipe_user_user_id_ba92bf`;"""
