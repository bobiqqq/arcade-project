def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "DungeonRunner")
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()