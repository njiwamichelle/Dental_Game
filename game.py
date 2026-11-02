# ===== FILE: game.py =====
"""game.py - The Game class: state machine, input, updating and drawing screens."""
import random
import sys
from enum import Enum, auto
import pygame
from settings import *
from entities import Toothbrush, Bacteria, Mouth, circle_hits_rect, make_pop
from drawing import (create_background, draw_text, draw_overlay, draw_hud, draw_tooth_face)


class State(Enum):
    """Every screen the game can be on."""
    TITLE = auto()
    LEVEL_INTRO = auto()
    PLAYING = auto()
    WIN = auto()
    LOSE = auto()
    TIME_UP = auto()
    FINAL = auto()


CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
PANEL_SIZE = (900, 460)
DIM_LIGHT, DIM_HEAVY = 110, 170


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.Font(None, 110),
            "big": pygame.font.Font(None, 52),
            "medium": pygame.font.Font(None, 38),
            "small": pygame.font.Font(None, 28),
            "hud": pygame.font.Font(None, 30),
        }
        self.background = create_background()
        self.mouth = Mouth()
        self.brush = Toothbrush()
        self.state = State.TITLE
        self.level_index = 0
        self.paused = False
        self.running = True
        self.reset_round_data()

    # ------------------------------------------------------------ round setup
    def reset_round_data(self):
        """Reset score, timer and objects. Called at the start of every round."""
        self.bacteria = []
        self.particles = []
        self.cleaned = 0
        self.reached = 0
        self.time_left = float(ROUND_TIME_SECONDS)
        self.spawn_timer = FIRST_SPAWN_DELAY
        self.paused = False
        self.brush.reset()
        self.mouth.reset()

    @property
    def level(self):
        return LEVELS[self.level_index]

    def start_round(self):
        self.reset_round_data()
        self.state = State.PLAYING

    # -------------------------------------------------------------- main loop
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, MAX_DT)   # Seconds since last frame
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------ input
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
            elif event.type == pygame.MOUSEMOTION:            # Optional mouse control
                if self.state == State.PLAYING and not self.paused:
                    self.brush.move_to(event.pos)

    def handle_keydown(self, key):
        confirm = key in CONFIRM_KEYS
        if self.state == State.TITLE:
            if confirm:
                self.level_index = 0
                self.reset_round_data()
                self.state = State.LEVEL_INTRO
            elif key == pygame.K_ESCAPE:
                self.running = False
        elif key == pygame.K_ESCAPE:                           # ESC = back to menu everywhere else
            self.state = State.TITLE
        elif self.state == State.LEVEL_INTRO:
            if confirm:
                self.start_round()
        elif self.state == State.PLAYING:
            if key == pygame.K_p:
                self.paused = not self.paused
        elif self.state == State.WIN:
            if confirm:
                self.level_index += 1
                self.reset_round_data()
                self.state = State.LEVEL_INTRO
        elif self.state in (State.LOSE, State.TIME_UP):
            if confirm:
                self.start_round()                             # Retry the same level
        elif self.state == State.FINAL:
            if confirm:
                self.level_index = 0
                self.reset_round_data()
                self.state = State.LEVEL_INTRO
            elif key == pygame.K_q:
                self.running = False

    # ----------------------------------------------------------------- update
    def update(self, dt):
        if self.paused:
            return
        if self.state == State.PLAYING:
            self.update_playing(dt)
        # Visual effects keep animating on every screen
        self.mouth.update(dt)
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def spawn_bacteria(self, dt):
        """Spawn on a timer, never exceeding this level's max on screen."""
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            if len(self.bacteria) < self.level["max_bacteria"]:
                self.bacteria.append(Bacteria(self.level, self.mouth.teeth_rect.center))
            self.spawn_timer = self.level["spawn_interval"] * random.uniform(*SPAWN_JITTER)

    def update_playing(self, dt):
        self.time_left -= dt
        self.brush.update(dt, pygame.key.get_pressed())
        self.spawn_bacteria(dt)

        clean_rect = self.brush.clean_rect
        for bac in self.bacteria[:]:                           # Copy: we remove while looping
            bac.update(dt)
            if circle_hits_rect(bac.pos, bac.radius, clean_rect):          # Brushed away!
                self.bacteria.remove(bac)
                self.cleaned += 1
                self.particles += make_pop(bac.pos)
            elif circle_hits_rect(bac.pos, bac.radius, self.mouth.teeth_rect):  # Reached teeth
                self.bacteria.remove(bac)
                self.reached += 1
                self.mouth.trigger_flash()

        # Check the end-of-round conditions
        if self.reached >= BACTERIA_TO_LOSE:
            self.state = State.LOSE
        elif self.cleaned >= BACTERIA_TO_CLEAN:
            last_level = self.level_index == len(LEVELS) - 1
            self.state = State.FINAL if last_level else State.WIN
        elif self.time_left <= 0:
            self.time_left = 0
            self.state = State.TIME_UP

    # ------------------------------------------------------------------- draw
    def draw_world(self):
        """Background, mouth, bacteria, effects and toothbrush."""
        self.screen.blit(self.background, (0, 0))
        self.mouth.draw(self.screen)
        for bac in self.bacteria:
            bac.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)
        self.brush.draw(self.screen)

    def draw(self):
        self.draw_world()
        if self.state == State.TITLE:
            self.draw_title()
        elif self.state == State.LEVEL_INTRO:
            self.draw_intro()
        else:
            self.draw_hud()
            if self.state == State.PLAYING:
                if self.paused:
                    draw_overlay(self.screen, DIM_LIGHT)
                    draw_text(self.screen, "PAUSED", self.fonts["title"], WHITE, center=(WIDTH // 2, HEIGHT // 2 - 20))
                    draw_text(self.screen, "Press P to resume", self.fonts["medium"], WHITE, center=(WIDTH // 2, HEIGHT // 2 + 50))
            elif self.state == State.WIN:
                self.draw_result("Sparkling Clean! The Dentist Wins!", "Press ENTER for Next Level", True)
            elif self.state == State.LOSE:
                self.draw_result("The Bacteria Win! Cavities Everywhere!", "Press ENTER to Retry This Level", False)
            elif self.state == State.TIME_UP:
                self.draw_result("Time's Up – Everybody Loses!", "Press ENTER to Retry This Level", False)
            elif self.state == State.FINAL:
                self.draw_result("You're the Ultimate Tooth Defender!", "ENTER: Play Again    Q: Quit", True)
        pygame.display.flip()

    def draw_hud(self):
        draw_hud(self.screen, self.fonts["hud"], self.level_index + 1, self.level["name"],
                 self.cleaned, self.reached, self.time_left)

    def blink(self):
        """True half the time, used for blinking 'Press ENTER' text."""
        return (pygame.time.get_ticks() // 500) % 2 == 0

    def draw_title(self):
        draw_overlay(self.screen, DIM_HEAVY)
        cx = WIDTH // 2
        draw_text(self.screen, "DENTAL GAME", self.fonts["title"], WHITE, center=(cx, 120))
        draw_tooth_face(self.screen, (cx, 235), 0.8, True)
        lines = ["You are the dentist! Move the toothbrush to scrub away the bacteria.",
                 "Move: Arrow keys / WASD (or the mouse)",
                 f"Clean {BACTERIA_TO_CLEAN} bacteria to win. Don't let {BACTERIA_TO_LOSE} reach the teeth!",
                 "P = Pause     ESC = Menu"]
        for i, line in enumerate(lines):
            draw_text(self.screen, line, self.fonts["small"], WHITE, center=(cx, 340 + i * 34))
        if self.blink():
            draw_text(self.screen, "Press ENTER to Start", self.fonts["big"], (255, 235, 90), center=(cx, 540))

    def draw_intro(self):
        draw_overlay(self.screen, DIM_HEAVY)
        cx, cy = WIDTH // 2, HEIGHT // 2
        draw_text(self.screen, f"Level {self.level_index + 1}: {self.level['name']}",
                  self.fonts["title"], WHITE, center=(cx, cy - 60))
        draw_text(self.screen, f"Clean {BACTERIA_TO_CLEAN} bacteria before {BACTERIA_TO_LOSE} reach the teeth!",
                  self.fonts["medium"], WHITE, center=(cx, cy + 20))
        if self.blink():
            draw_text(self.screen, "Press ENTER to begin", self.fonts["big"], (255, 235, 90), center=(cx, cy + 100))

    def draw_result(self, headline, prompt, happy):
        """Win / lose / time-up / final panel with a tooth drawing."""
        draw_overlay(self.screen, DIM_LIGHT)
        panel = pygame.Rect(0, 0, *PANEL_SIZE)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        surf = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, PANEL_BG, surf.get_rect(), border_radius=30)
        self.screen.blit(surf, panel.topleft)
        pygame.draw.rect(self.screen, TEXT_DARK, panel, 4, border_radius=30)
        draw_tooth_face(self.screen, (panel.centerx, panel.top + 130), 1.0, happy)
        draw_text(self.screen, headline, self.fonts["big"], TEXT_DARK, center=(panel.centerx, panel.top + 270), shadow=False)
        draw_text(self.screen, f"Cleaned: {self.cleaned}   Reached teeth: {self.reached}",
                  self.fonts["small"], TEXT_DARK, center=(panel.centerx, panel.top + 325), shadow=False)
        if self.blink():
            draw_text(self.screen, prompt, self.fonts["medium"], (200, 60, 60), center=(panel.centerx, panel.top + 395), shadow=False)