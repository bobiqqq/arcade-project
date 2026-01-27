import arcade


class StartView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Dungeon Runner",
            self.window.width / 2,
            self.window.height / 2 + 60,
            arcade.color.WHITE,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "SPACE — start   ESC — quit",
            self.window.width / 2,
            self.window.height / 2 - 10,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )

    # Начало игрового цикла по нажатию пробела, на ESC - выход
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()
            return
        if key == arcade.key.SPACE:
            from main import DungeonRunner

            game_view = DungeonRunner()
            game_view.setup()
            self.window.show_view(game_view)


class BeetwenLevel(arcade.View):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.level.player.has_key = False # Обнуляем наличие ключа у игрока при переходе на новый уровень
        self.message = ""
        self.message_timer = 0.0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
    
    # Отображение текста о возможности улучшения при переходе на следующий уровень
    def on_draw(self): 
        self.clear()
        arcade.draw_text(
            "Выберите улучшение",
            self.window.width / 2,
            self.window.height / 2 + 60,
            arcade.color.WHITE,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "1,2,3 - выбор      ENTER - далее",
            self.window.width / 2,
            self.window.height / 2 - 20,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "1: Увеличить здоровье на 20 - 5 монет",
            self.window.width / 2,
            self.window.height / 2 - 50,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "2: Увеличить урон на 3 - 7 монет ",
            self.window.width / 2,
            self.window.height / 2 - 80,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "3: Увеличить скорость на 7% - 4 монеты",
            self.window.width / 2,
            self.window.height / 2 - 110,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        # Рисуем уведомление если оно есть
        if self.message:
            arcade.draw_text(
                self.message,
                self.window.width / 2,
                self.window.height / 2 + 90,
                arcade.color.RED,
                font_size=24,
                anchor_x="center",
                anchor_y="center",
            )

    # Выбор улучшения с проверкой на нехватку монет и переход на новый уровень
    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            if self.level.player.coins >= 5:
                self.level.player.hp += 20
                self.level.player.coins -= 5
                self.window.show_view(self.level)
            else:
                self.show_message(f"Не хватает {3 - self.level.player.coins} монет!", 2.0)
        elif key == arcade.key.KEY_2:
            if self.level.player.coins >= 7:
                self.level.player.damage += 3
                self.level.player.coins -= 7
                self.window.show_view(self.level)
            else:
                self.show_message(f"Не хватает {7 - self.level.player.coins} монет!", 2.0)
        elif key == arcade.key.KEY_3:
            if self.level.player.coins >= 4:
                self.level.player.speed *= 1.07
                self.level.player.coins -= 4
                self.level.player.speed = round(self.level.player.speed)
                self.window.show_view(self.level)
            else:
                self.show_message(f"Не хватает {4 - self.level.player.coins} монет!", 2.0)
        elif key == arcade.key.ENTER:
            self.window.show_view(self.level)

    # Таймер для отображения о нехватке монет
    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = ""
                self.message_timer = 0
    
    # Добавление текста и продолжительности уведомления
    def show_message(self, text, duration):
        self.message = text
        self.message_timer = duration


class GameOver(arcade.View):
    def __init__(self, player):
        super().__init__()
        self.player = player

        # Получаем статистику игрока для подсчета очков
        self.levels = self.player.stats["levels"]
        self.coins = self.player.stats["coins"]
        self.kills = self.player.stats["kills"]

        # Подсчет очков по супер сложной формуле
        self.score = self.levels * 100
        self.score += self.coins * 10
        self.score += self.kills * 50

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Игра закончена",
            self.window.width / 2,
            self.window.height / 2 + 60,
            arcade.color.WHITE,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Счет: {self.score}",
            self.window.width / 2,
            self.window.height / 2 - 15,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Убийства: {self.kills}",
            self.window.width / 2,
            self.window.height / 2 - 40,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Уровней пройдено: {self.levels}",
            self.window.width / 2,
            self.window.height / 2 - 65,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Монет собрано: {self.coins}",
            self.window.width / 2,
            self.window.height / 2 - 90,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
