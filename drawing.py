# ===== FILE: drawing.py =====
"""drawing.py - Helper functions that draw the background, HUD, tooth faces and text."""
import math
import pygame
from settings import *


def draw_text(surface, text, font, color, center=None, midleft=None, midright=None, shadow=True):
    """Render text at a position, with an optional drop shadow for readability."""
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center: rect.center = center
    if midleft: rect.midleft = midleft
    if midright: rect.midright = midright
    if shadow:
        surface.blit(font.render(text, True, BLACK), rect.move(2, 2))
    surface.blit(img, rect)


def create_background():
    """Draw the dental office ONCE onto a surface (fast to blit every frame)."""
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(WALL_COLOR)
    for x in range(0, WIDTH, 80):                                    # Subtle wall stripes
        pygame.draw.rect(bg, WALL_STRIPE, (x, 0, 40, FLOOR_Y))

    # Tiled floor (checkerboard)
    for row, y in enumerate(range(FLOOR_Y, HEIGHT, TILE_SIZE)):
        for col, x in enumerate(range(0, WIDTH, TILE_SIZE)):
            color = FLOOR_A if (row + col) % 2 == 0 else FLOOR_B
            pygame.draw.rect(bg, color, (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.line(bg, (150, 150, 160), (0, FLOOR_Y), (WIDTH, FLOOR_Y), 4)

    # Wall cabinet (top-left)
    cab = pygame.Rect(30, 60, 220, 130)
    pygame.draw.rect(bg, (245, 245, 250), cab, border_radius=6)
    pygame.draw.line(bg, (160, 160, 175), cab.midtop, cab.midbottom, 3)
    pygame.draw.rect(bg, (120, 120, 140), cab, 3, border_radius=6)
    for hx in (cab.centerx - 12, cab.centerx + 12):
        pygame.draw.circle(bg, (120, 120, 140), (hx, cab.centery), 5)

    # Tooth poster
    poster = pygame.Rect(285, 60, 100, 110)
    pygame.draw.rect(bg, (255, 250, 220), poster)
    pygame.draw.rect(bg, (150, 110, 70), poster, 4)
    draw_tooth_face(bg, (poster.centerx, poster.centery + 5), 0.4, True)

    # Window (top-right)
    win = pygame.Rect(730, 60, 180, 130)
    pygame.draw.rect(bg, (150, 210, 255), win)
    pygame.draw.circle(bg, WHITE, (win.x + 55, win.y + 45), 18)
    pygame.draw.circle(bg, WHITE, (win.x + 75, win.y + 50), 14)
    pygame.draw.line(bg, WHITE, win.midtop, win.midbottom, 6)
    pygame.draw.line(bg, WHITE, win.midleft, win.midright, 6)
    pygame.draw.rect(bg, (230, 230, 235), win, 8)

    # Overhead dental lamp
    cx = WIDTH // 2
    pygame.draw.line(bg, (110, 110, 125), (cx, 0), (cx, 95), 8)
    pygame.draw.polygon(bg, (225, 225, 235), [(cx - 50, 130), (cx + 50, 130), (cx + 30, 95), (cx - 30, 95)])
    pygame.draw.polygon(bg, (110, 110, 125), [(cx - 50, 130), (cx + 50, 130), (cx + 30, 95), (cx - 30, 95)], 3)
    pygame.draw.ellipse(bg, (255, 245, 150), (cx - 32, 122, 64, 16))

    # Dental chair (bottom-left)
    pygame.draw.rect(bg, (90, 90, 105), (105, 590, 16, 55))                      # Pole
    pygame.draw.ellipse(bg, (70, 70, 85), (50, 630, 130, 40))                    # Base
    pygame.draw.rect(bg, (60, 140, 200), (30, 540, 160, 50), border_radius=14)   # Seat
    pygame.draw.rect(bg, (60, 140, 200), (20, 430, 50, 140), border_radius=18)   # Backrest
    pygame.draw.rect(bg, (90, 170, 230), (22, 395, 46, 40), border_radius=14)    # Headrest
    pygame.draw.rect(bg, (30, 80, 130), (30, 540, 160, 50), 3, border_radius=14)

    # Tray of dental tools (bottom-right)
    tray = pygame.Rect(750, 520, 210, 20)
    pygame.draw.rect(bg, (120, 120, 135), (770, 540, 8, 100))                    # Legs
    pygame.draw.rect(bg, (120, 120, 135), (932, 540, 8, 100))
    pygame.draw.rect(bg, (200, 205, 215), tray, border_radius=4)
    pygame.draw.rect(bg, (120, 120, 135), tray, 2, border_radius=4)
    pygame.draw.line(bg, (90, 90, 100), (775, 515), (830, 500), 4)               # Mirror handle
    pygame.draw.circle(bg, (190, 230, 250), (832, 498), 9)                       # Mirror
    pygame.draw.line(bg, (90, 90, 100), (850, 517), (900, 505), 3)               # Probe
    pygame.draw.line(bg, (90, 90, 100), (900, 505), (905, 497), 3)
    pygame.draw.rect(bg, (230, 230, 240), (915, 500, 30, 14), border_radius=4)   # Syringe
    pygame.draw.line(bg, (90, 90, 100), (945, 507), (958, 507), 2)
    return bg


def draw_overlay(surface, alpha):
    """Darken whatever is already on screen (used behind menus)."""
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, alpha))
    surface.blit(dim, (0, 0))


def draw_hud(surface, font, level_number, level_name, cleaned, reached, time_left):
    """Top bar: level, cleaned counter, reached counter and MM:SS timer."""
    bar = pygame.Surface((WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
    bar.fill(HUD_BG)
    surface.blit(bar, (0, 0))
    mid = HUD_HEIGHT // 2
    draw_text(surface, f"Level {level_number}: {level_name}", font, HUD_TEXT, midleft=(15, mid), shadow=False)
    draw_text(surface, f"Bacteria Cleaned: {cleaned}/{BACTERIA_TO_CLEAN}", font, HUD_GOOD,
              midleft=(200, mid), shadow=False)
    draw_text(surface, f"Bacteria Reached Teeth: {reached}/{BACTERIA_TO_LOSE}", font, HUD_BAD,
              midleft=(490, mid), shadow=False)
    seconds = max(0, math.ceil(time_left))
    color = HUD_TIME_LOW if seconds <= 30 else HUD_TEXT
    draw_text(surface, f"{seconds // 60:02d}:{seconds % 60:02d}", font, color,
              midright=(WIDTH - 15, mid), shadow=False)


def draw_tooth_face(surface, center, scale, happy):
    """A cartoon tooth, happy (sparkles, smile) or sad (frown, tears)."""
    cx, cy = center
    w, h = int(120 * scale), int(100 * scale)
    crown = pygame.Rect(0, 0, w, h); crown.center = (cx, cy - int(10 * scale))
    root_w, root_h = int(42 * scale), int(60 * scale)
    for rx in (crown.left + int(8 * scale), crown.right - int(8 * scale) - root_w):
        root = pygame.Rect(rx, crown.centery + int(20 * scale), root_w, root_h)
        pygame.draw.rect(surface, TOOTH_WHITE, root, border_radius=int(18 * scale))
        pygame.draw.rect(surface, TOOTH_OUTLINE, root, max(1, int(3 * scale)), border_radius=int(18 * scale))
    pygame.draw.rect(surface, TOOTH_WHITE, crown, border_radius=int(40 * scale))
    pygame.draw.rect(surface, TOOTH_OUTLINE, crown, max(1, int(3 * scale)), border_radius=int(40 * scale))
    eye_r = max(2, int(7 * scale))
    for sign in (-1, 1):
        pygame.draw.circle(surface, BLACK, (crown.centerx + int(sign * 24 * scale), crown.centery - int(8 * scale)), eye_r)
    mouth = pygame.Rect(0, 0, int(44 * scale), int(30 * scale))
    width = max(1, int(4 * scale))
    if happy:
        mouth.center = (crown.centerx, crown.centery + int(12 * scale))
        pygame.draw.arc(surface, BLACK, mouth, math.pi, math.tau, width)       # Smile
        for sign in (-1, 1):                                                   # Blush
            pygame.draw.circle(surface, (255, 170, 180), (crown.centerx + int(sign * 40 * scale), crown.centery + int(8 * scale)), max(2, int(8 * scale)))
        for dx, dy in ((-80, -40), (85, -30), (70, 40)):                       # Sparkles
            sx, sy = cx + int(dx * scale), cy + int(dy * scale)
            pygame.draw.polygon(surface, (255, 235, 90), [(sx, sy - 10), (sx + 3, sy - 3), (sx + 10, sy), (sx + 3, sy + 3), (sx, sy + 10), (sx - 3, sy + 3), (sx - 10, sy), (sx - 3, sy - 3)])
    else:
        mouth.center = (crown.centerx, crown.centery + int(26 * scale))
        pygame.draw.arc(surface, BLACK, mouth, 0, math.pi, width)              # Frown
        for sign in (-1, 1):                                                   # Tears
            tx = crown.centerx + int(sign * 24 * scale)
            pygame.draw.ellipse(surface, (110, 180, 255), (tx - int(4 * scale), crown.centery + int(2 * scale), int(8 * scale), int(16 * scale)))