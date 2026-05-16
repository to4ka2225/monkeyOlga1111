import pygame
import random

pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        # екран
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Ухиляйся та збирай!")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)

        # --- ЗАВАНТАЖЕННЯ СКІНІВ ---
        self.current_skin_index = 0
        self.skins_imgs = []

        # МІСЦЕ ДЛЯ ФОТО СКІНІВ
        # Скін 1 (основний)
        skin1 = pygame.image.load("image/monkey2.png")
        self.skins_imgs.append(self.scale_image(skin1, 100))

        # Скін 2
        skin2 = pygame.image.load("image/monkey_skin2.png")
        self.skins_imgs.append(self.scale_image(skin2, 100))

        # Скін 3
        skin3 = pygame.image.load("image/monkey_skin3.png")
        self.skins_imgs.append(self.scale_image(skin3, 100))

        # --- ЗАВАНТАЖЕННЯ АНІМАЦІЇ ПЕРЕМОГИ ---
        self.win_animation_frames = []
        # Завантажуємо 27 кадрів з папки animation (aaanim1.png - aaanim27.png)
        for i in range(1, 28):
            frame_img = pygame.image.load(f"animation/aaanim{i}.png")
            # Робимо розмір 120 (трішки більше ніж у грі, де розмір 100)
            self.win_animation_frames.append(self.scale_image(frame_img, 120))

        self.current_win_frame = 0.0
        # Швидкість зміни кадрів: 27 кадрів за 3 секунди при 60 FPS
        # 27 кадрів / (3 сек * 60 FPS) = 27 / 180 = 0.15 кадра за один такт гри
        self.win_anim_speed = 0.15

        # --- ЗАВАНТАЖЕННЯ ІНШИХ ОБ'ЄКТІВ ---
        self.enemy_img = pygame.image.load("image/img_1.png")
        self.banana_img = pygame.image.load("image/img.png")
        self.background = pygame.image.load("image/background.png")
        self.menu_background = pygame.image.load("image/menu.png")
        self.settings_icon = pygame.image.load("image/settings.png")

        # Масштабування
        self.enemy_img = self.scale_image(self.enemy_img, 100)
        self.banana_img = self.scale_image(self.banana_img, 100)
        self.settings_icon = pygame.transform.scale(self.settings_icon, (50, 50))
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        self.menu_background = pygame.transform.scale(self.menu_background, (self.WIDTH, self.HEIGHT))

        # Музика гри за замовчуванням
        self.volume = 0.5

        # Стан гри
        self.running = True
        self.in_menu = True
        self.show_settings = False

        # Кнопки та повзунок
        self.start_button = pygame.Rect(self.WIDTH // 2 - 150, self.HEIGHT // 2 - 50, 300, 100)
        self.settings_button = pygame.Rect(self.WIDTH - 70, 20, 50, 50)
        self.slider_rect = pygame.Rect(self.WIDTH // 2 - 100, self.HEIGHT // 2 - 80, 200, 10)
        self.slider_handle = pygame.Rect(self.WIDTH // 2 - 5, self.HEIGHT // 2 - 90, 20, 30)
        self.dragging_slider = False

        # Кнопка рестарту в кінці гри
        self.restart_button = pygame.Rect(self.WIDTH // 2 - 150, self.HEIGHT // 2 + 30, 300, 70)

        # Прямокутники для вибору скінів
        self.skin_rects = []
        for i in range(3):
            rect = pygame.Rect(self.WIDTH // 2 - 170 + (i * 120), self.HEIGHT // 2 + 50, 100, 100)
            self.skin_rects.append(rect)

        self.enemy_speed = 5
        self.coin_speed = 4
        self.player_speed = 8

        self.reset_game()

    def scale_image(self, img, target_width):
        ratio = target_width / img.get_width()
        target_height = int(img.get_height() * ratio)
        return pygame.transform.scale(img, (target_width, target_height))

    def reset_game(self):
        self.player = pygame.Rect(self.WIDTH // 2, self.HEIGHT - 100, 80, 80)
        self.enemies = []
        self.coins = []
        self.score = 0
        self.hits = 0
        self.game_over = False
        self.win = False
        self.current_win_frame = 0.0

        # Запуск фонової музики при старті або перезапуску
        pygame.mixer.music.load("sound/fongame.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.settings_button.collidepoint(event.pos):
                    self.show_settings = not self.show_settings

                if self.in_menu and not self.show_settings:
                    if self.start_button.collidepoint(event.pos):
                        self.in_menu = False

                if self.show_settings:
                    # Клік по повзунку
                    if self.slider_handle.collidepoint(event.pos):
                        self.dragging_slider = True
                    # Клік по скінах
                    for i, rect in enumerate(self.skin_rects):
                        if rect.collidepoint(event.pos):
                            self.current_skin_index = i

                # Клік на кнопку рестарту під час фіналу
                if self.game_over or self.win:
                    if self.restart_button.collidepoint(event.pos):
                        self.reset_game()

            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = False

            if event.type == pygame.MOUSEMOTION and self.dragging_slider:
                new_x = max(self.slider_rect.left, min(event.pos[0], self.slider_rect.right))
                self.slider_handle.centerx = new_x
                self.volume = (new_x - self.slider_rect.left) / self.slider_rect.width
                pygame.mixer.music.set_volume(self.volume)

    def draw_settings_window(self):
        win_w, win_h = 500, 400
        win_rect = pygame.Rect(self.WIDTH // 2 - win_w // 2, self.HEIGHT // 2 - win_h // 2, win_w, win_h)

        pygame.draw.rect(self.screen, (255, 255, 255), win_rect)
        pygame.draw.rect(self.screen, (144, 238, 144), win_rect, 5)

        # Секція гучності
        vol_text = self.small_font.render(f"ГУЧНІСТЬ МУЗИКИ: {int(self.volume * 100)}%", True, (0, 0, 0))
        self.screen.blit(vol_text, (win_rect.x + 50, win_rect.y + 40))
        pygame.draw.rect(self.screen, (200, 200, 200), self.slider_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.slider_handle)

        # Секція скінів
        skin_label = self.small_font.render("ОБЕРИ ПЕРСОНАЖА:", True, (0, 0, 0))
        self.screen.blit(skin_label, (win_rect.x + 50, win_rect.y + 150))

        for i, rect in enumerate(self.skin_rects):
            if i == self.current_skin_index:
                pygame.draw.rect(self.screen, (255, 215, 0), rect.inflate(10, 10), 4)

            self.screen.blit(self.skins_imgs[i], rect.topleft)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_menu(self):
        self.screen.blit(self.menu_background, (0, 0))
        if not self.show_settings:
            pygame.draw.rect(self.screen, (255, 255, 255), self.start_button)
            start_text = self.font.render("START", True, (0, 0, 0))
            text_rect = start_text.get_rect(center=self.start_button.center)
            self.screen.blit(start_text, text_rect)

        self.screen.blit(self.settings_icon, (self.settings_button.x, self.settings_button.y))
        if self.show_settings:
            self.draw_settings_window()

    def draw_game(self):
        self.screen.blit(self.background, (0, 0))
        if not self.game_over and not self.win:
            self.screen.blit(self.skins_imgs[self.current_skin_index], (self.player.x, self.player.y))

            for enemy in self.enemies: self.screen.blit(self.enemy_img, (enemy.x, enemy.y))
            for coin in self.coins: self.screen.blit(self.banana_img, (coin.x, coin.y))

            score_text = self.font.render(f"Зібрано: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (20, 20))
            hits_text = self.font.render(f"Помилки: {self.hits}/5", True, (255, 100, 100))
            self.screen.blit(hits_text, (20, 60))

        # Екран завершення гри
        if self.game_over or self.win:
            if self.game_over:
                msg = "ТИ ПРОГРАВ!"
            else:
                msg = "ТИ ВИГРАВ!"

            # Розрахунок позиції плашки з текстом
            msg_text = self.font.render(msg, True, (0, 0, 0))
            msg_rect = msg_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
            bg_rect = msg_rect.inflate(40, 20)

            # ЯКЩО ПЕРЕМОГА — виводимо зациклену анімацію над написом "ТИ ВИГРАВ!"
            if self.win:
                current_frame_img = self.win_animation_frames[int(self.current_win_frame)]
                # Центруємо картинку мавпочки горизонтально, а вертикально ставимо над білою плашкою bg_rect
                anim_x = self.WIDTH // 2 - current_frame_img.get_width() // 2
                anim_y = bg_rect.top - current_frame_img.get_height() - 15
                self.screen.blit(current_frame_img, (anim_x, anim_y))

            # Малюємо білу рамку для тексту повідомлення
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)  # Біле тло
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, 4)  # Чорний контур
            self.screen.blit(msg_text, msg_rect)

            # Малюємо білу кнопку "Рестарт" з чорним контуром
            pygame.draw.rect(self.screen, (255, 255, 255), self.restart_button)  # Біле тло
            pygame.draw.rect(self.screen, (0, 0, 0), self.restart_button, 4)  # Чорний контур

            btn_text = self.font.render("РЕСТАРТ", True, (0, 0, 0))
            btn_rect = btn_text.get_rect(center=self.restart_button.center)
            self.screen.blit(btn_text, btn_rect)

    def player_movement(self):
        keys = pygame.key.get_pressed()
        if not self.game_over and not self.win:
            if keys[pygame.K_LEFT] and self.player.x > 0:
                self.player.x -= self.player_speed
            if keys[pygame.K_RIGHT] and self.player.x < self.WIDTH - 100:
                self.player.x += self.player_speed

    def spawn_objects(self):
        if random.randint(1, 28) == 1:
            self.enemies.append(pygame.Rect(random.randint(0, self.WIDTH - 60), 0, 60, 60))
        if random.randint(1, 50) == 1:
            self.coins.append(pygame.Rect(random.randint(0, self.WIDTH - 50), 0, 50, 50))

    def update(self):
        if not self.game_over and not self.win:
            self.spawn_objects()
            for enemy in self.enemies[:]:
                enemy.y += self.enemy_speed
                if enemy.y > self.HEIGHT:
                    self.enemies.remove(enemy)
                elif self.player.colliderect(enemy):
                    self.enemies.remove(enemy)
                    self.hits += 1
            for coin in self.coins[:]:
                coin.y += self.coin_speed
                if coin.y > self.HEIGHT:
                    self.coins.remove(coin)
                elif self.player.colliderect(coin):
                    self.coins.remove(coin)
                    self.score += 1
            self.check_conditions()

        # Оновлення кадрів анімації у випадку перемоги (зациклено)
        if self.win:
            self.current_win_frame += self.win_anim_speed
            if self.current_win_frame >= len(self.win_animation_frames):
                self.current_win_frame = 0.0

    def check_conditions(self):
        if self.score >= 10 and not self.win:
            self.win = True
            pygame.mixer.music.load("sound/win.mp3")
            pygame.mixer.music.play(1)

        if self.hits >= 5 and not self.game_over:
            self.game_over = True
            pygame.mixer.music.load("sound/lose.mp3")
            pygame.mixer.music.play(1)

    def run(self):
        while self.running:
            self.handle_events()
            if self.in_menu:
                self.draw_menu()
            else:
                self.player_movement()
                self.update()
                self.draw_game()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


game = Game()
game.run()