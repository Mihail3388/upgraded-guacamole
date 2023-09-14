import pygame
import sys
import random
import sqlite3


class Character:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def move(self, direction):
        if direction == "LEFT":
            self.x -= self.speed
        elif direction == "RIGHT":
            self.x += self.speed
        elif direction == "UP":
            self.y -= self.speed
        elif direction == "DOWN":
            self.y += self.speed

    def draw(self, window):
        pygame.draw.rect(window, (0, 0, 255), (self.x, self.y, self.width, self.height))


class GameObject:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = random.randint(0, WINDOW_HEIGHT - self.height)

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))


class Database:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER)'''
        )

        self.conn.commit()

    def save_score(self, username, score):
        self.cursor.execute("INSERT INTO highscores (username, score) VALUES (?, ?)", (username, score))
        self.conn.commit()

    def print_highscores(self, limit=5):
        self.cursor.execute("SELECT username, score FROM highscores ORDER BY score DESC LIMIT ?", (limit,))
        highscores = self.cursor.fetchall()

        print(f"Топ {limit} игроков:")
        for username, score in highscores:
            print(f"Игрок {username}: {score} очков")

    def close(self):
        self.conn.close()


class Game:
    def __init__(self, username, database):
        self.username = username
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f'Управление персонажем: {username}')
        self.score = 0
        self.score_font = pygame.font.Font(None, 24)
        self.database = database

    def game_loop(self):
        MAX_SCORE = 5
        character = Character(250, 250, 30, 30, 0.1)
        green_object = GameObject(20, 20, (0, 255, 0))
        red_object = GameObject(20, 20, (255, 0, 0))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                character.move("LEFT")
            elif keys[pygame.K_RIGHT]:
                character.move("RIGHT")
            elif keys[pygame.K_UP]:
                character.move("UP")
            elif keys[pygame.K_DOWN]:
                character.move("DOWN")

            self.window.fill((255, 255, 255))

            display_score = self.score_font.render(f'Очки: {self.score}', True, (0, 0, 0))
            self.window.blit(display_score, (10, 10))

            green_object.draw(self.window)
            character.draw(self.window)
            red_object.draw(self.window)

            if self.collision(character, green_object):
                self.score += 1
                green_object.x = random.randint(0, WINDOW_WIDTH - green_object.width)
                green_object.y = random.randint(0, WINDOW_HEIGHT - green_object.height)

            if self.collision(character, red_object):
                print(f"{self.username}, вы проиграли! Ваш счет: {self.score}")
                return False

            if self.score >= MAX_SCORE:
                print(f"Поздравляем, {self.username}! Вы выиграли! Ваш счет: {self.score}")
                return True

            pygame.display.update()

    def collision(self, character, obj):
        return (
            character.x < obj.x + obj.width and
            character.x + character.width > obj.x and
            character.y < obj.y + obj.height and
            character.y + character.height > obj.y
        )


if __name__ == "__main__":
    pygame.init()

    username = input("Введите ваше имя: ")

    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 500

    database = Database("highscores.db")

    game = Game(username, database)
    try:
        game_ended = game.game_loop()
    finally:
        database.save_score(username, game.score)
        database.print_highscores()
        database.close()

        pygame.quit()
        sys.exit()
