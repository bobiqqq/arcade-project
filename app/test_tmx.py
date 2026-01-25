import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Dungeon Runner"
TILE_SCALING = 1.0
PLAYER_MOVEMENT_SPEED = 5
CAMERA_LERP = 0.1


class DungeonRunner(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.world_camera = arcade.camera.Camera2D()
        self.world_camera.zoom = 0.7
        self.gui_camera = arcade.camera.Camera2D()

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.key_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()
        self.exit_list = arcade.SpriteList()

        map_path = os.path.join("levels", "level_01.tmx")
        self.tile_map = arcade.load_tilemap(map_path, scaling=TILE_SCALING)
        
        self.floor_list = self.tile_map.sprite_lists["floor"]
        self.wall_list = self.tile_map.sprite_lists["walls"]
        self.collision_list = self.tile_map.sprite_lists["collision"]
        self.exit_list = self.tile_map.sprite_lists["exit"]

        object_layer = self.tile_map.object_lists["Object Layer 1"]
        if object_layer:
            for obj in object_layer:
                x, y = obj.shape[0], obj.shape[1]

                if obj.name == "player_spawn":
                    self.player = arcade.Sprite(
                        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
                        scale=0.8
                    )
                    self.player.center_x = x
                    self.player.center_y = y
                    self.player_list.append(self.player)

                elif obj.name == "enemy":
                    enemy = arcade.Sprite(":resources:images/enemies/slimeBlue.png", scale=0.7)
                    enemy.center_x = x
                    enemy.center_y = y
                    self.enemy_list.append(enemy)

                elif obj.name == "coin":
                    coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.5)
                    coin.center_x = x
                    coin.center_y = y
                    self.coin_list.append(coin)

                elif obj.name == "key":
                    key = arcade.Sprite(":resources:images/items/keyYellow.png", scale=0.6)
                    key.center_x = x
                    key.center_y = y
                    self.key_list.append(key)

                elif obj.name == "bomb":
                    bomb = arcade.Sprite(":resources:images/tiles/bomb.png", scale=0.5)
                    bomb.center_x = x
                    bomb.center_y = y
                    self.bomb_list.append(bomb)

        if self.player and self.collision_list:
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.collision_list)
        
        self.world_camera.position = (self.player.center_x, self.player.center_y)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.floor_list.draw()
        self.wall_list.draw()
        self.enemy_list.draw()
        self.coin_list.draw()
        self.key_list.draw()
        self.bomb_list.draw()
        self.player_list.draw()
        self.exit_list.draw()

    def on_update(self, delta_time):
        if self.physics_engine:
            self.physics_engine.update()

        position = self.player.center_x, self.player.center_y

        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            CAMERA_LERP,
        )


    def on_key_press(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.player.change_y = PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.player.change_y = -PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        
        if self.player.change_x != 0 and self.player.change_y != 0:
            self.player.change_x *= 0.7071
            self.player.change_x *= 0.7071


    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S, arcade.key.UP, arcade.key.DOWN):
            self.player.change_y = 0
        if key in (arcade.key.A, arcade.key.D, arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0


def main():
    window = DungeonRunner()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()