import pygame
import random

pygame.init()
pygame.mixer.init()

# екран
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ухиляйся та збирай!")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# ігрок
player_img = pygame.image.load("image/monkey2.png")

# правильні пропорції
target_width = 100
ratio = target_width / player_img.get_width()
target_height = int(player_img.get_height() * ratio)
player_img = pygame.transform.scale(player_img, (target_width, target_height))

# камінь
enemy_img = pygame.image.load("image/img_1.png")  # картинку
# правильні пропорції
target_width = 100
ratio = target_width / enemy_img.get_width()
target_height = int(enemy_img.get_height() * ratio)
enemy_img = pygame.transform.scale(enemy_img, (target_width, target_height))

# банани
banana_img = pygame.image.load("image/img.png")  # картинку
# правильні пропорції
target_width = 100
ratio = target_width / banana_img.get_width()
target_height = int(banana_img.get_height() * ratio)
banana_img = pygame.transform.scale(banana_img, (target_width, target_height))

# Фон
background = pygame.image.load("image/background.png")  # фон
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# пісні
pygame.mixer.music.load("sound/fongame.mp3")  # пісні
pygame.mixer.music.play(-1)  # безкінечно


def reset_game():
    return {
        "player": pygame.Rect(WIDTH//2, HEIGHT-100, 80, 80),
        "enemies": [],
        "coins": [],
        "score": 0,
        "hits": 0,
        "game_over": False,
        "win": False
    }


game = reset_game()

enemy_speed = 5
coin_speed = 4
player_speed = 8

running = True

while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    #  РЕСТАРТ
    if game["game_over"] and keys[pygame.K_w]:
        game = reset_game()

    if not game["game_over"] and not game["win"]:
        if keys[pygame.K_LEFT] and game["player"].x > 0:
            game["player"].x -= player_speed
        if keys[pygame.K_RIGHT] and game["player"].x < WIDTH - 80:
            game["player"].x += player_speed

        # реже спавн
        if random.randint(1, 28) == 1:
            game["enemies"].append(pygame.Rect(random.randint(0, WIDTH-60), 0, 60, 60))

        if random.randint(1, 50) == 1:
            game["coins"].append(pygame.Rect(random.randint(0, WIDTH-50), 0, 50, 50))

        # вороги
        for enemy in game["enemies"][:]:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:
                game["enemies"].remove(enemy)
            if game["player"].colliderect(enemy):
                game["enemies"].remove(enemy)
                game["hits"] += 1

        # монети
        for coin in game["coins"][:]:
            coin.y += coin_speed
            if coin.y > HEIGHT:
                game["coins"].remove(coin)
            if game["player"].colliderect(coin):
                game["coins"].remove(coin)
                game["score"] += 1

        # умови
        if game["score"] >= 10:
            game["win"] = True
        if game["hits"] >= 5:
            game["game_over"] = True

        # персонажі є тільки під час гри
        screen.blit(player_img, (game["player"].x, game["player"].y))

        for enemy in game["enemies"]:
            screen.blit(enemy_img, (enemy.x, enemy.y))

        for coin in game["coins"]:
            screen.blit(banana_img, (coin.x, coin.y))

        score_text = font.render(f"Зібрано: {game['score']}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        hits_text = font.render(f"Помилки: {game['hits']}/5", True, (255, 100, 100))
        screen.blit(hits_text, (20, 60))

    # програш
    if game["game_over"]:
        text = font.render("Ти програв! натисни W для рестарту", True, (255, 255, 255))
        screen.blit(text, (200, HEIGHT//2))

    # виграш
    if game["win"]:
        text = font.render("Ти виграв!", True, (255, 255, 0))
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()