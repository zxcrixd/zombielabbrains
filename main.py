# -*- coding: utf-8 -*-
"""
ЗОМБИ-ЛАБОРАТОРИЯ 3D — Code Education Edition (CEE)
Псевдо-3D игра с обучением Python.
Управление: WASD — движение, стрелки — поворот, E — компьютер, Esc — меню.
"""

import pygame
import math
import sys
import time

# ---------- Константы ----------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
COLOR_BG = (30, 30, 30)
COLOR_PANEL = (50, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)
COLOR_YELLOW = (200, 200, 0)
COLOR_BLUE = (0, 100, 200)
COLOR_BLACK = (0, 0, 0)
COLOR_WALL = (100, 100, 100)
COLOR_WALL_BRICK = (160, 80, 60)
COLOR_WALL_CONCRETE = (90, 90, 110)
COLOR_FLOOR = (50, 50, 50)
COLOR_CEILING = (20, 20, 20)
COLOR_COMPUTER = (0, 200, 200)
COLOR_BUTTON = (80, 80, 80)
COLOR_BUTTON_HOVER = (110, 110, 110)

# ---------- Карта ----------
MAP_WIDTH = 16
MAP_HEIGHT = 16
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,2,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

PLAYER_START_X = 2.5
PLAYER_START_Y = 2.5
PLAYER_START_ANGLE = 0.0

# ---------- Класс кнопки ----------
class Button:
    def __init__(self, x, y, w, h, text, callback=None, color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 2, border_radius=5)
        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False

# ---------- Класс игрока ----------
class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 3.0
        self.rot_speed = 2.0

    def move_forward(self, dt, map_data):
        new_x = self.x + math.cos(self.angle) * self.speed * dt
        new_y = self.y + math.sin(self.angle) * self.speed * dt
        if not self.collides(new_x, new_y, map_data):
            self.x = new_x
            self.y = new_y

    def move_backward(self, dt, map_data):
        new_x = self.x - math.cos(self.angle) * self.speed * dt
        new_y = self.y - math.sin(self.angle) * self.speed * dt
        if not self.collides(new_x, new_y, map_data):
            self.x = new_x
            self.y = new_y

    def rotate(self, angle_delta):
        self.angle += angle_delta

    def collides(self, x, y, map_data):
        radius = 0.2
        for dx in [-radius, radius]:
            for dy in [-radius, radius]:
                check_x = int(x + dx)
                check_y = int(y + dy)
                if check_x < 0 or check_x >= MAP_WIDTH or check_y < 0 or check_y >= MAP_HEIGHT:
                    return True
                if map_data[check_y][check_x] in [1, 3, 4]:
                    return True
        return False

    def get_position(self):
        return self.x, self.y

    def get_angle(self):
        return self.angle

# ---------- Класс Raycaster ----------
class Raycaster:
    def __init__(self, screen, map_data, map_width, map_height):
        self.screen = screen
        self.map_data = map_data
        self.map_width = map_width
        self.map_height = map_height
        self.wall_colors = {1: COLOR_WALL, 3: COLOR_WALL_BRICK, 4: COLOR_WALL_CONCRETE}
        self.floor_color = COLOR_FLOOR
        self.ceiling_color = COLOR_CEILING

    def draw(self, player):
        width = SCREEN_WIDTH
        height = SCREEN_HEIGHT
        px, py = player.get_position()
        angle = player.get_angle()

        pygame.draw.rect(self.screen, self.ceiling_color, (0, 0, width, height // 2))
        pygame.draw.rect(self.screen, self.floor_color, (0, height // 2, width, height // 2))

        fov = math.pi / 3
        half_fov = fov / 2
        num_rays = width
        angle_step = fov / num_rays
        ray_angle = angle - half_fov

        for x in range(width):
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30

            map_x = int(px)
            map_y = int(py)

            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (px - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1 - px) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (py - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1 - py) * delta_dist_y

            hit = False
            side = 0
            wall_type = 1
            max_steps = 100
            steps = 0
            while not hit and steps < max_steps:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1
                if map_x < 0 or map_x >= self.map_width or map_y < 0 or map_y >= self.map_height:
                    hit = True
                elif self.map_data[map_y][map_x] in [1, 3, 4]:
                    hit = True
                    wall_type = self.map_data[map_y][map_x]
                steps += 1

            if side == 0:
                perp_dist = side_dist_x - delta_dist_x
            else:
                perp_dist = side_dist_y - delta_dist_y
            if perp_dist <= 0:
                perp_dist = 0.01

            line_height = int(height / perp_dist)

            shade = 1.0 / (1 + perp_dist * perp_dist * 0.1)
            if side == 1:
                shade *= 0.7
            base_color = self.wall_colors.get(wall_type, COLOR_WALL)
            color = (
                int(base_color[0] * shade),
                int(base_color[1] * shade),
                int(base_color[2] * shade)
            )

            draw_start = -line_height // 2 + height // 2
            draw_end = line_height // 2 + height // 2
            pygame.draw.line(self.screen, color, (x, draw_start), (x, draw_end))

            ray_angle += angle_step

        # Спрайты компьютеров (системный блок + монитор)
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 2:
                    sprite_x = x + 0.5
                    sprite_y = y + 0.5
                    dx = sprite_x - px
                    dy = sprite_y - py
                    sprite_angle = math.atan2(dy, dx)
                    angle_diff = sprite_angle - angle
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    while angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                    if abs(angle_diff) < half_fov:
                        dist = math.sqrt(dx**2 + dy**2)
                        sprite_size = int(height / dist)
                        screen_x = int((angle_diff / fov + 0.5) * width)
                        half_size = sprite_size // 2
                        top = height // 2 - half_size
                        bottom = height // 2 + half_size
                        left = screen_x - half_size // 2
                        right = screen_x + half_size // 2

                        # Корпус
                        corp_height = int(sprite_size * 0.55)
                        corp_top = bottom - corp_height
                        corp_rect = pygame.Rect(left, corp_top, right - left, corp_height)
                        pygame.draw.rect(self.screen, (90, 90, 110), corp_rect)
                        pygame.draw.rect(self.screen, COLOR_BLACK, corp_rect, 2)

                        if sprite_size > 40:
                            vent_width = max(2, (right - left) // 5)
                            vent_height = max(2, corp_height // 3)
                            vent_y = corp_top + 4
                            for i in range(3):
                                vent_x = left + 4 + i * (vent_width + 3)
                                pygame.draw.rect(self.screen, COLOR_BLACK,
                                                 (vent_x, vent_y, vent_width, vent_height))

                        # Монитор
                        monitor_height = int(sprite_size * 0.45)
                        monitor_rect = pygame.Rect(left, top, right - left, monitor_height)
                        pygame.draw.rect(self.screen, (70, 70, 80), monitor_rect)
                        pygame.draw.rect(self.screen, COLOR_BLACK, monitor_rect, 2)

                        screen_margin = max(2, int(sprite_size * 0.06))
                        screen_rect = pygame.Rect(left + screen_margin,
                                                  top + screen_margin,
                                                  (right - left) - 2 * screen_margin,
                                                  monitor_height - 2 * screen_margin)
                        pygame.draw.rect(self.screen, COLOR_BLACK, screen_rect)
                        pygame.draw.rect(self.screen, (0, 80, 0), screen_rect, 1)

                        if sprite_size > 60:
                            font_size = max(12, sprite_size // 6)
                            font = pygame.font.SysFont("monospace", font_size, bold=True)
                            text_surf = font.render("sudo rm -rf /", True, (0, 255, 0))
                            text_rect = text_surf.get_rect(center=screen_rect.center)
                            self.screen.blit(text_surf, text_rect)

# ---------- Класс миссии ----------
class Mission:
    def __init__(self, id, title, description, code_template, solution_check, hint, reward_brains):
        self.id = id
        self.title = title
        self.description = description
        self.code_template = code_template
        self.solution_check = solution_check
        self.hint = hint
        self.reward_brains = reward_brains
        self.completed = False

# ---------- Проверки кода ----------
def check_mission_1(code):
    return "create_zombie()" in code

def check_mission_2(code):
    return ("for" in code and "create_zombie" in code and "range" in code)

def check_mission_3(code):
    return ("def" in code and "create_zombie" in code)

def check_mission_4(code):
    return ("=" in code and "for" in code and "create_zombie" in code)

# ---------- Класс города ----------
class City:
    def __init__(self, name, population, defense, reward_brains):
        self.name = name
        self.population = population
        self.defense = defense
        self.reward_brains = reward_brains
        self.owner = "human"  # human / player

# ---------- Класс игры ----------
class Game:
    def __init__(self):
        pygame.init()
        # Настройки окна
        self.resolutions = [(960, 600), (1280, 720), (1600, 900)]
        self.current_resolution_index = 0
        self.fullscreen = False

        self.screen = pygame.display.set_mode(
            self.resolutions[self.current_resolution_index],
            pygame.FULLSCREEN if self.fullscreen else 0
        )
        pygame.display.set_caption("Зомби-лаборатория 3D — CEE")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 18)

        self.state = "intro"  # intro, menu, playing, settings, about
        self.mode = "game"    # game, coding, terminal
        self.terminal_screen = None  # main, learn, attack
        self.menu_buttons = []
        self.settings_buttons = []
        self.about_buttons = []
        self.intro_buttons = []
        self.terminal_buttons = []
        self.attack_buttons = []

        self.player = None
        self.raycaster = None
        self.brains = 0
        self.zombie_count = 0
        self.missions = []
        self.current_mission_index = 0
        self.cities = []
        self.selected_city = 0

        self.coding_input = ""
        self.coding_hint_shown = False
        self.last_input_time = 0

        self.message_text = ""
        self.message_timer = 0

        self.init_missions()
        self.init_cities()
        self.create_intro_buttons()
        self.create_menu()
        self.create_settings_buttons()
        self.create_about_buttons()

    def init_missions(self):
        self.missions = [
            Mission(1, "Создание первого зомби",
                    "Напишите код, который вызывает функцию create_zombie().\n"
                    "Подсказка: просто введите create_zombie() и нажмите Ctrl+Enter.",
                    "", check_mission_1, "Попробуйте написать: create_zombie()", 10),
            Mission(2, "Массовое производство",
                    "Используйте цикл for для создания 5 зомби.\n"
                    "Пример:\n"
                    "for i in range(5):\n"
                    "    create_zombie()",
                    "", check_mission_2, "Напишите цикл for с range(5) и вызовом create_zombie() внутри.", 20),
            Mission(3, "Функция-производитель",
                    "Определите функцию my_production(), которая вызывает create_zombie(),\n"
                    "а затем вызовите эту функцию.",
                    "", check_mission_3, "Используйте def для создания функции, внутри вызовите create_zombie(), затем вызовите функцию.", 30),
            Mission(4, "Автоматизация с переменной",
                    "Создайте переменную n = 3 и используйте цикл for с range(n),\n"
                    "чтобы создать n зомби.",
                    "", check_mission_4, "Присвойте переменной значение, затем используйте её в range().", 40),
        ]

    def init_cities(self):
        self.cities = [
            City("Москва", 500, 30, 50),
            City("Лондон", 400, 25, 40),
            City("Токио", 600, 40, 60),
            City("Нью-Йорк", 450, 28, 45),
            City("Берлин", 350, 20, 35),
            City("Париж", 380, 22, 38),
        ]

    def create_intro_buttons(self):
        self.intro_buttons = [
            Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, "START", self.start_game)
        ]

    def create_menu(self):
        self.menu_buttons = []
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        btn_w = 200
        btn_h = 50
        self.menu_buttons.append(Button(cx - btn_w//2, cy - 100, btn_w, btn_h, "Играть", self.start_game))
        self.menu_buttons.append(Button(cx - btn_w//2, cy - 40, btn_w, btn_h, "Настройки", self.open_settings))
        self.menu_buttons.append(Button(cx - btn_w//2, cy + 20, btn_w, btn_h, "About game", self.open_about))
        self.menu_buttons.append(Button(cx - btn_w//2, cy + 80, btn_w, btn_h, "Выход", self.quit_game))

    def create_settings_buttons(self):
        fullscreen_text = "Полноэкранный режим: " + ("Вкл" if self.fullscreen else "Выкл")
        res_text = f"Разрешение: {self.resolutions[self.current_resolution_index][0]}x{self.resolutions[self.current_resolution_index][1]}"
        self.settings_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 100, 200, 40, "Настройки", None),
            Button(SCREEN_WIDTH//2 - 100, 160, 200, 40, fullscreen_text, self.toggle_fullscreen),
            Button(SCREEN_WIDTH//2 - 100, 220, 200, 40, res_text, self.cycle_resolution),
            Button(SCREEN_WIDTH//2 - 100, 280, 200, 40, "Сложность: Нормально", None),
            Button(SCREEN_WIDTH//2 - 100, 340, 200, 40, "Громкость: 80%", None),
            Button(SCREEN_WIDTH//2 - 100, 400, 200, 40, "Назад", self.back_to_menu)
        ]

    def create_about_buttons(self):
        self.about_buttons = [
            Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 150, 200, 40, "Назад", self.back_to_menu)
        ]

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.apply_display_mode()
        self.create_settings_buttons()

    def cycle_resolution(self):
        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
        self.apply_display_mode()
        self.create_settings_buttons()

    def apply_display_mode(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                self.resolutions[self.current_resolution_index],
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                self.resolutions[self.current_resolution_index]
            )

    def start_game(self):
        self.player = Player(PLAYER_START_X, PLAYER_START_Y, PLAYER_START_ANGLE)
        self.raycaster = Raycaster(self.screen, MAP, MAP_WIDTH, MAP_HEIGHT)
        self.brains = 0
        self.zombie_count = 0
        self.current_mission_index = 0
        self.mode = "game"
        self.state = "playing"
        self.set_message("Найдите компьютер и нажмите E")

    def open_settings(self):
        self.state = "settings"

    def open_about(self):
        self.state = "about"

    def back_to_menu(self):
        self.state = "menu"
        self.create_menu()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def set_message(self, text, duration=3.0):
        self.message_text = text
        self.message_timer = duration

    def update_message(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_text = ""

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if self.state == "intro":
                for btn in self.intro_buttons:
                    btn.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.start_game()

            elif self.state == "menu":
                for btn in self.menu_buttons:
                    btn.handle_event(event)

            elif self.state == "settings":
                for btn in self.settings_buttons:
                    btn.handle_event(event)

            elif self.state == "about":
                for btn in self.about_buttons:
                    btn.handle_event(event)

            elif self.state == "playing":
                if self.mode == "game":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e:
                            if self.is_near_computer():
                                self.open_terminal()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "menu"
                            self.create_menu()
                elif self.mode == "coding":
                    self.handle_coding_events(event)
                elif self.mode == "terminal":
                    self.handle_terminal_events(event)

        # Движение
        if self.state == "playing" and self.mode == "game":
            keys = pygame.key.get_pressed()
            dt = self.clock.get_time() / 1000.0
            if keys[pygame.K_w]:
                self.player.move_forward(dt, MAP)
            if keys[pygame.K_s]:
                self.player.move_backward(dt, MAP)
            if keys[pygame.K_a]:
                self.player.rotate(-self.player.rot_speed * dt)
            if keys[pygame.K_d]:
                self.player.rotate(self.player.rot_speed * dt)
            if keys[pygame.K_LEFT]:
                self.player.rotate(-self.player.rot_speed * dt)
            if keys[pygame.K_RIGHT]:
                self.player.rotate(self.player.rot_speed * dt)

    def handle_coding_events(self, event):
        if event.type == pygame.KEYDOWN:
            self.last_input_time = time.time()
            self.coding_hint_shown = False
            if event.key == pygame.K_RETURN:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.submit_code()
                else:
                    self.coding_input += "\n"
            elif event.key == pygame.K_ESCAPE:
                self.close_coding_interface()
            elif event.key == pygame.K_BACKSPACE:
                self.coding_input = self.coding_input[:-1]
            else:
                if event.unicode and event.unicode.isprintable():
                    self.coding_input += event.unicode

    def handle_terminal_events(self, event):
        if self.terminal_screen == "main":
            for btn in self.terminal_buttons:
                btn.handle_event(event)
        elif self.terminal_screen == "learn":
            # Кнопки не нужны, сразу открываем кодинг
            pass
        elif self.terminal_screen == "attack":
            for btn in self.attack_buttons:
                btn.handle_event(event)
            # Обработка клавиш для выбора города
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_city = (self.selected_city - 1) % len(self.cities)
                    self.create_attack_buttons()
                elif event.key == pygame.K_DOWN:
                    self.selected_city = (self.selected_city + 1) % len(self.cities)
                    self.create_attack_buttons()

    def open_terminal(self):
        self.mode = "terminal"
        self.terminal_screen = "main"
        self.create_terminal_buttons()
        self.set_message("Выберите действие")

    def close_terminal(self):
        self.mode = "game"
        self.terminal_screen = None
        self.terminal_buttons = []
        self.attack_buttons = []

    def create_terminal_buttons(self):
        self.terminal_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 50, "Обучение Python", self.open_learning),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 50, "Атака городов", self.open_city_attack),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 50, "Выйти", self.close_terminal)
        ]

    def open_learning(self):
        self.close_terminal()
        if self.current_mission_index < len(self.missions):
            self.open_coding_interface()
        else:
            self.set_message("Все миссии выполнены!")

    def open_city_attack(self):
        self.terminal_screen = "attack"
        self.selected_city = 0
        self.create_attack_buttons()

    def create_attack_buttons(self):
        self.attack_buttons = []
        y = 150
        for i, city in enumerate(self.cities):
            text = f"{city.name} (Защита: {city.defense})"
            if i == self.selected_city:
                text = "> " + text
            btn = Button(SCREEN_WIDTH//2 - 200, y, 400, 30, text, lambda idx=i: self.select_city(idx))
            self.attack_buttons.append(btn)
            y += 40
        # Кнопка атаки
        self.attack_buttons.append(Button(SCREEN_WIDTH//2 - 100, y + 20, 200, 40, "Атаковать", self.attack_selected_city))
        # Кнопка назад
        self.attack_buttons.append(Button(SCREEN_WIDTH//2 - 100, y + 70, 200, 40, "Назад", self.back_to_terminal_main))

    def select_city(self, idx):
        self.selected_city = idx
        self.create_attack_buttons()

    def attack_selected_city(self):
        if self.zombie_count <= 0:
            self.set_message("Нет зомби для атаки!")
            return
        city = self.cities[self.selected_city]
        attack_power = self.zombie_count * 10
        if attack_power > city.defense:
            losses = int(self.zombie_count * (city.defense / attack_power))
            self.zombie_count -= losses
            self.brains += city.reward_brains
            city.owner = "player"
            self.set_message(f"Победа! {city.name} захвачен. Получено {city.reward_brains} мозгов.")
        else:
            self.zombie_count = int(self.zombie_count * 0.5)
            self.set_message(f"Поражение. Потеряно половина зомби.")
        self.create_attack_buttons()

    def back_to_terminal_main(self):
        self.terminal_screen = "main"
        self.create_terminal_buttons()

    def is_near_computer(self):
        if not self.player:
            return False
        px, py = self.player.get_position()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x = int(px + dx)
                check_y = int(py + dy)
                if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                    if MAP[check_y][check_x] == 2:
                        return True
        return False

    def open_coding_interface(self):
        self.mode = "coding"
        self.coding_input = ""
        self.coding_hint_shown = False
        self.last_input_time = time.time()
        self.set_message("Режим программирования. Введите код и нажмите Ctrl+Enter.")

    def close_coding_interface(self):
        self.mode = "game"
        self.coding_input = ""
        self.set_message("Вы вышли из режима программирования.")

    def submit_code(self):
        if self.current_mission_index >= len(self.missions):
            return
        mission = self.missions[self.current_mission_index]
        code = self.coding_input.strip()
        if mission.solution_check(code):
            try:
                global_env = {"__builtins__": {}, "create_zombie": self.create_zombie}
                exec(code, global_env, global_env)
                self.brains += mission.reward_brains
                mission.completed = True
                self.current_mission_index += 1
                self.set_message(f"Миссия выполнена! Получено {mission.reward_brains} мозгов.")
                self.mode = "game"
                self.coding_input = ""
            except Exception as e:
                self.set_message(f"Ошибка выполнения: {e}")
        else:
            self.set_message("Код не соответствует требованиям миссии.")

    def create_zombie(self):
        self.zombie_count += 1

    def check_inactivity(self):
        if self.state == "playing" and self.mode == "coding" and not self.coding_hint_shown:
            if time.time() - self.last_input_time > 60:
                mission = self.missions[self.current_mission_index]
                self.set_message(f"Подсказка: {mission.hint}")
                self.coding_hint_shown = True

    def update(self, dt):
        self.update_message(dt)
        self.check_inactivity()

    def draw(self):
        self.screen.fill(COLOR_BG)

        if self.state == "intro":
            self.draw_intro()
        elif self.state == "menu":
            self.draw_menu()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "about":
            self.draw_about()
        elif self.state == "playing":
            self.draw_game()

        if self.message_text:
            msg_surf = self.font.render(self.message_text, True, COLOR_YELLOW)
            self.screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, 50))

        pygame.display.flip()

    def draw_intro(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        intro_text = [
            "**ZOMBIES LABORATORY – OPENING SCENE**",
            "",
            "(Flickering fluorescent tubes buzz overhead. A glass tank gurgles thick green goo.",
            "Somewhere, a generator coughs like a dying cat.)",
            "",
            "Ah, welcome—*welcome*—to my temple of rejected genius. They called my theories “dangerous,”",
            "my methods “unethical,” my hygiene “concerning.” The university kicked me out with a trash bag",
            "and a restraining order. The scientific journals printed my name next to “cautionary tale.”",
            "But look around… *look* at this beautiful, leaky, rat-infested paradise! Every bubbling beaker,",
            "every sparking wire, every half-chewed clipboard—it’s all *mine*.",
            "",
            "You see, those ivory-tower fools thought they could bury my work. But death, my friend, is just a",
            "*starting point*. With a little DNA, a pinch of fresh tissue, and my patented “Oops-All-Necrosis”",
            "formula, I’ll build an army that doesn’t unionize, doesn’t complain about break rooms, and *never*",
            "misses a Monday.",
            "",
            "Your job? Hunt for samples. Brew stronger strains. Send my shambling darlings to infect every block,",
            "every city, every smug little town that once laughed at my grant proposals. The world will kneel—",
            "not to bombs or politics, but to *science*. *My* science.",
            "",
            "So… ready to get your hands dirty? The petri dishes are prepped, the mortuary fridge is humming,",
            "and the first test subject is *aching* to meet you.",
            "",
            "Click START. Unleash your first zombie. Let the world feel my—*our*—vindication."
        ]

        y = 30
        for line in intro_text:
            surf = self.small_font.render(line, True, COLOR_TEXT)
            self.screen.blit(surf, (50, y))
            y += 22

        for btn in self.intro_buttons:
            btn.draw(self.screen)

    def draw_menu(self):
        title = self.big_font.render("ЗОМБИ-ЛАБОРАТОРИЯ 3D", True, COLOR_RED)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        subtitle = self.small_font.render("Code Education Edition", True, COLOR_TEXT)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 120))
        for btn in self.menu_buttons:
            btn.draw(self.screen)

    def draw_settings(self):
        title = self.big_font.render("Настройки", True, COLOR_TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        for btn in self.settings_buttons:
            btn.draw(self.screen)

    def draw_about(self):
        title = self.big_font.render("About game", True, COLOR_TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        info_lines = [
            "Зомби-лаборатория 3D — CEE",
            "Игра для изучения Python",
            "Производитель: ShadowLabs Ltd",
            "Все права защищены",
        ]
        y = 150
        for line in info_lines:
            surf = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
            y += 40
        for btn in self.about_buttons:
            btn.draw(self.screen)

    def draw_game(self):
        self.raycaster.draw(self.player)

        brain_text = self.small_font.render(f"Мозги: {self.brains}", True, COLOR_TEXT)
        self.screen.blit(brain_text, (10, 10))
        zombie_text = self.small_font.render(f"Зомби: {self.zombie_count}", True, COLOR_TEXT)
        self.screen.blit(zombie_text, (10, 30))
        if self.current_mission_index < len(self.missions):
            mission_title = self.missions[self.current_mission_index].title
            mission_text = self.small_font.render(f"Текущая миссия: {mission_title}", True, COLOR_BLUE)
            self.screen.blit(mission_text, (10, 50))

        if self.is_near_computer() and self.mode == "game":
            prompt = self.small_font.render("Нажмите E для взаимодействия", True, COLOR_YELLOW)
            self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT - 100))

        if self.mode == "coding":
            self.draw_coding_interface()
        elif self.mode == "terminal":
            self.draw_terminal()

    def draw_terminal(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        if self.terminal_screen == "main":
            title = self.big_font.render("Терминал", True, COLOR_TEXT)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            for btn in self.terminal_buttons:
                btn.draw(self.screen)
        elif self.terminal_screen == "attack":
            title = self.big_font.render("Атака городов", True, COLOR_TEXT)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
            info = self.small_font.render(f"Доступно зомби: {self.zombie_count}", True, COLOR_YELLOW)
            self.screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, 100))
            for btn in self.attack_buttons:
                btn.draw(self.screen)

    def draw_coding_interface(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_BLACK, panel_rect, 2, border_radius=10)

        if self.current_mission_index < len(self.missions):
            mission = self.missions[self.current_mission_index]
            title_surf = self.big_font.render(f"Миссия: {mission.title}", True, COLOR_TEXT)
            self.screen.blit(title_surf, (panel_rect.x + 20, panel_rect.y + 20))

            desc_lines = mission.description.split('\n')
            y_offset = panel_rect.y + 70
            for line in desc_lines:
                desc_surf = self.small_font.render(line, True, COLOR_TEXT)
                self.screen.blit(desc_surf, (panel_rect.x + 20, y_offset))
                y_offset += 20

            input_rect = pygame.Rect(panel_rect.x + 20, panel_rect.y + 140, panel_rect.width - 40, 200)
            pygame.draw.rect(self.screen, COLOR_BLACK, input_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLOR_TEXT, input_rect, 2, border_radius=5)

            code_lines = self.coding_input.split('\n')
            y_text = input_rect.y + 10
            for line in code_lines:
                line_surf = self.small_font.render(line, True, COLOR_GREEN)
                self.screen.blit(line_surf, (input_rect.x + 10, y_text))
                y_text += 20

            if self.coding_hint_shown:
                hint_surf = self.small_font.render(f"Подсказка: {mission.hint}", True, COLOR_YELLOW)
                self.screen.blit(hint_surf, (panel_rect.x + 20, input_rect.bottom + 10))

            instr_surf = self.small_font.render("Введите код. Enter — новая строка, Ctrl+Enter — выполнить. Esc — выход.", True, COLOR_TEXT)
            self.screen.blit(instr_surf, (panel_rect.x + 20, panel_rect.bottom - 40))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

# ---------- Точка входа ----------
if __name__ == "__main__":
    game = Game()
    game.run()