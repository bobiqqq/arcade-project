import arcade
import os
from bullet import Bullet
from constants import *
from hero import Hero
from enemy import *
import random
from pyglet.graphics import Batch
from views import *

class DungeonRunner(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        self.base_dir = os.path.dirname(__file__)

        # Настройка камеры
        self.world_camera = arcade.camera.Camera2D()
        self.world_camera.zoom = 0.7 * (SCREEN_HEIGHT // 600)
        self.gui_camera = arcade.camera.Camera2D() 

    # Подготовка объекта уровня. Передаём путь к карте и объект игрока для сохранения значений атрибутов
    def setup(self, level_path="levels/level_01.tmx", hero=None):
        if not os.path.isabs(level_path):
            level_path = os.path.join(self.base_dir, level_path)
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.key_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.level_list = [
            os.path.join(self.base_dir, "levels", "level_01.tmx"),
            os.path.join(self.base_dir, "levels", "level_02.tmx"),
        ]

        self.tile_map = arcade.load_tilemap(level_path, scaling=TILE_SCALING) # Загрузка карты

        # Загрузка тайлов из карты
        self.floor_list = self.tile_map.sprite_lists["floor"]
        self.wall_list = self.tile_map.sprite_lists["walls"]
        self.collision_list = self.tile_map.sprite_lists["collision"]
        self.exit_list = self.tile_map.sprite_lists["exit"]

        self.keys_pressed = set()

        # Создание объектов по координатам из карты
        object_layer = self.tile_map.object_lists["Object Layer 1"]
        if object_layer:
            for obj in object_layer:
                x, y = obj.shape[0], obj.shape[1]
                if obj.name == "player_spawn":
                    self.player = Hero() if hero is None else hero # при первом запуске создаём игрока
                    self.player.center_x = x
                    self.player.center_y = y
                    self.player_list.append(self.player)
                elif obj.name == "enemy":
                    enemy = random.choice([ShooterEnemy(x, y), SlimeEnemy(x, y)])
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

        # "Усложняем" игру в зависимости от количества пройденных уровней
        if self.player is not None and self.player.stats["levels"] != 0:
            for enemy in self.enemy_list:
                buff = 1 + (self.player.stats["levels"] / 10)
                enemy.hp *= buff
                enemy.damage *= buff
                enemy.damage = round(enemy.damage, 1)
                

        if self.player and self.collision_list:
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.collision_list) # Добавляем движок физики для игрока и списка коллизий

        self.world_camera.position = (self.player.center_x, self.player.center_y) # Устанавливаем камеру в позицию игрока

    # Отрисовываем игровые элементы
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
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.gui_camera.use()

        arcade.draw_text(
            f"HP: {self.player.hp} | Coins: {self.player.coins}",
            10, self.window.height - 30,
            arcade.color.WHITE, 18
        )

    def on_update(self, delta_time):
        if self.physics_engine:
            self.physics_engine.update()
        self.player.update(delta_time, self.keys_pressed) 
        self.player_list.update_animation()
        self.bullet_list.update(delta_time, self.collision_list)
        
        # Проверка разных взаимодействий
        self.enemy_bullet_list.update(delta_time, self.collision_list)
        self.check_pickups()
        self.check_exit()
        self.check_bullets_hit_enemies()
        self.check_damage()

        # Обновляем логику интеллекта у врагов
        for enemy in self.enemy_list:
            enemy.update_ai(self.player, self.collision_list, delta_time, self)
        
        # Следование камеры за игроком
        position = self.player.center_x, self.player.center_y
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            CAMERA_LERP,
        )

        # Обновление времени неуязвимости игрока при получении урона
        if self.player.damaged_end > 0:
            self.player.damaged_end -= delta_time

    # Проверка на взаимодействие с монетками и ключом
    def check_pickups(self):
        for coin in arcade.check_for_collision_with_list(self.player, self.coin_list):
            coin.remove_from_sprite_lists()
            self.player.coins += 1
            self.player.stats["coins"] += 1
        for key in arcade.check_for_collision_with_list(self.player, self.key_list):
            key.remove_from_sprite_lists()
            self.player.has_key = True

    # Логика получения урона игроком от врагов, бомб и пуль
    def check_damage(self):
        for enemy in arcade.check_for_collision_with_list(self.player, self.enemy_list):
            self.player.get_damage(enemy.damage) # Наносим урон игроку
            self.check_game_over() # Проверяем жив ли игрок
        for bomb in arcade.check_for_collision_with_list(self.player, self.bomb_list):
            self.player.get_damage(25)
            self.check_game_over()
            bomb.remove_from_sprite_lists()
            break
        for bullet in arcade.check_for_collision_with_list(self.player, self.enemy_bullet_list):
            self.player.get_damage(bullet.damage)
            self.check_game_over()
            bullet.remove_from_sprite_lists()


    def check_game_over(self):
        if self.player.hp <= 0:
            self.window.show_view(GameOver(self.player)) # Заканчиваем игру если игрок умирает

    # Проверка на имение пользователем ключа -> соприкосновения с дверью перехода на следующий уровень
    def check_exit(self):
        if not self.player.has_key:
            return # Не исполняем ничего пока нет ключа
        """
        При переходе на следующий уровень прибавляем соответствующее значение в статистику, 
        создаём объект нового уровня, передавая в него случайную карту из файлов и объект игрока,
        потом передаем созданный уровень в меню перехода
        """
        if arcade.check_for_collision_with_list(self.player, self.exit_list):
            self.player.stats["levels"] += 1
            new_level = DungeonRunner()
            new_level.setup(level_path=random.choice(self.level_list), hero=self.player)
            self.window.show_view(BeetwenLevel(new_level))
            return  

    # Проверяем пули на попадение в врагов
    def check_bullets_hit_enemies(self):
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if not hit_list:
                continue # Пропускаем пулю если она не попадает в врага
            bullet.remove_from_sprite_lists()
            for enemy in hit_list:
                enemy.get_damage(bullet.damage) # наносим урон врагу, если он погибает - убираем из спрайтов и добавляем соответствующее значение в статистику 
                if enemy.hp <= 0:
                    enemy.remove_from_sprite_lists()
                    self.player.stats["kills"] += 1

    # Создаём пулю при нажатии на мышку
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_pos = self.world_camera.unproject((x, y)) # Координаты на экране и в мире немного разные: обращаем в одну систему
            target_x, target_y = world_pos[0], world_pos[1] 
            bullet = Bullet(
                self.player.center_x,
                self.player.center_y,
                target_x,
                target_y,
                speed=BULLET_SPEED,
                damage=self.player.damage,
                lifetime=BULLET_LIFETIME,
            )
            self.bullet_list.append(bullet)
            

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)