# ===== FILE: entities.py =====
"""entities.py - Game objects: Toothbrush, Bacteria, Mouth (teeth) and Particle."""
import math
import random
import pygame
from settings import *   # constants only


def circle_hits_rect(center, radius, rect):
    """True if a circle overlaps a rectangle (closest-point test)."""
    closest_x = max(rect.left, min(center.x, rect.right))
    closest_y = max(rect.top, min(center.y, rect.bottom))
    return (center.x - closest_x) ** 2 + (center.y - closest_y) ** 2 <= radius ** 2


# ---------------------------------------------------------------- Toothbrush
class Toothbrush:
    """The player. (x, y) is the top-left corner of the brush HEAD block."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.x = float((WIDTH - BRUSH_TOTAL_W) // 2)
        self.y = float(HEIGHT - BRUSH_START_BOTTOM_MARGIN)

    def clamp(self):
        """Keep the whole brush (head + handle) inside the screen."""
        self.x = max(0, min(self.x, WIDTH - BRUSH_TOTAL_W))
        self.y = max(HUD_HEIGHT + BRUSH_BRISTLE_H, min(self.y, HEIGHT - BRUSH_HEAD_H))

    def move_to(self, mouse_pos):
        """Optional mouse control: center the head under the cursor."""
        self.x = mouse_pos[0] - BRUSH_HEAD_W / 2
        self.y = mouse_pos[1] - BRUSH_HEAD_H / 2
        self.clamp()

    def update(self, dt, keys):
        """Move with Arrow keys or WASD, same speed in every direction."""
        move = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        if move.length_squared() > 0:
            move = move.normalize() * BRUSH_SPEED * dt
            self.x += move.x
            self.y += move.y
        self.clamp()

    @property
    def clean_rect(self):
        """The part of the brush that cleans: the bristles plus the head block."""
        return pygame.Rect(int(self.x), int(self.y) - BRUSH_BRISTLE_H,
                           BRUSH_HEAD_W, BRUSH_HEAD_H + BRUSH_BRISTLE_H)

    def draw(self, surface):
        head = pygame.Rect(int(self.x), int(self.y), BRUSH_HEAD_W, BRUSH_HEAD_H)
        handle = pygame.Rect(head.right - 4, head.centery - BRUSH_HANDLE_H // 2,
                             BRUSH_HANDLE_L + 4, BRUSH_HANDLE_H)
        bristles = pygame.Rect(head.left + 4, head.top - BRUSH_BRISTLE_H,
                               BRUSH_HEAD_W - 8, BRUSH_BRISTLE_H)
        # Handle with little grip stripes
        pygame.draw.rect(surface, BRUSH_HANDLE, handle, border_radius=7)
        for gx in range(handle.left + 30, handle.right - 10, 14):
            pygame.draw.line(surface, WHITE, (gx, handle.top + 3), (gx, handle.bottom - 3), 2)
        pygame.draw.rect(surface, BRUSH_OUTLINE, handle, 2, border_radius=7)
        # Head block
        pygame.draw.rect(surface, BRUSH_HEAD, head, border_radius=6)
        pygame.draw.rect(surface, BRUSH_OUTLINE, head, 2, border_radius=6)
        # Bristles (light blue with dark outline so they show on white teeth)
        for bx in range(bristles.left + 3, bristles.right, BRISTLE_SPACING):
            pygame.draw.line(surface, BRISTLE_COLOR, (bx, head.top), (bx, bristles.top), 4)
        pygame.draw.rect(surface, BRUSH_OUTLINE, bristles, 2)


# ------------------------------------------------------------------ Bacteria
class Bacteria:
    """An angry germ that wobbles toward the teeth."""

    def __init__(self, level_cfg, target):
        self.radius = BACTERIA_RADIUS
        self.pos = self._random_edge_position()
        self.target = pygame.Vector2(target)
        self.speed = level_cfg["speed"] * random.uniform(*BACTERIA_SPEED_VARIATION)
        self.wobble = level_cfg["wobble"]
        self.age = random.uniform(0, 10)                 # Timer for wobble animation
        self.phase = random.uniform(0, math.tau)
        self.freq = random.uniform(*WOBBLE_FREQ_RANGE)
        self.drift = random.uniform(-1, 1)               # Random zig-zag sideways push
        self.drift_timer = random.uniform(*DRIFT_CHANGE_RANGE)
        self.color = random.choice(BACTERIA_COLORS)
        self.dark = tuple(int(c * 0.55) for c in self.color)

    def _random_edge_position(self):
        """Pick a random point along one of the four screen edges."""
        m = self.radius
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return pygame.Vector2(random.uniform(m, WIDTH - m), HUD_HEIGHT + m)
        if side == "bottom":
            return pygame.Vector2(random.uniform(m, WIDTH - m), HEIGHT - m)
        if side == "left":
            return pygame.Vector2(m, random.uniform(HUD_HEIGHT + m, HEIGHT - m))
        return pygame.Vector2(WIDTH - m, random.uniform(HUD_HEIGHT + m, HEIGHT - m))

    def update(self, dt):
        self.age += dt
        self.drift_timer -= dt
        if self.drift_timer <= 0:                        # Pick a new zig-zag direction
            self.drift = random.uniform(-1, 1)
            self.drift_timer = random.uniform(*DRIFT_CHANGE_RANGE)
        to_target = self.target - self.pos
        forward = to_target.normalize() if to_target.length_squared() > 0 else pygame.Vector2()
        side = pygame.Vector2(-forward.y, forward.x)     # Perpendicular direction
        sway = self.wobble * (WOBBLE_SINE_WEIGHT * math.sin(self.age * self.freq + self.phase)
                              + WOBBLE_DRIFT_WEIGHT * self.drift)
        self.pos += (forward * self.speed + side * sway * self.speed) * dt

    def draw(self, surface):
        cx, cy = int(self.pos.x), int(self.pos.y)
        r = int(self.radius * (1 + 0.08 * math.sin(self.age * 10)))   # Pulsing body
        # Spikes / little legs
        for i in range(SPIKE_COUNT):
            ang = i * math.tau / SPIKE_COUNT + self.age * 1.5
            length = r + SPIKE_LENGTH * (0.7 + 0.3 * math.sin(self.age * 8 + i))
            end = (cx + math.cos(ang) * length, cy + math.sin(ang) * length)
            pygame.draw.line(surface, self.dark, (cx, cy), end, 3)
            pygame.draw.circle(surface, self.dark, end, 3)
        # Body
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, self.dark, (cx, cy), r, 2)
        # Angry eyes and eyebrows
        for sign in (-1, 1):
            ex = cx + sign * r * 0.38
            ey = cy - r * 0.1
            pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), max(3, r // 4))
            pygame.draw.circle(surface, BLACK, (int(ex - sign * 1), int(ey + 1)), max(2, r // 8))
            pygame.draw.line(surface, BLACK,
                             (cx + sign * r * 0.75, cy - r * 0.6),
                             (cx + sign * r * 0.1, cy - r * 0.28), 3)
        # Grumpy mouth
        pygame.draw.line(surface, BLACK, (cx - r * 0.3, cy + r * 0.5), (cx + r * 0.3, cy + r * 0.5), 2)


# --------------------------------------------------------------------- Mouth
class Mouth:
    """The big cartoon mouth. Its teeth are the area the player protects."""

    def __init__(self):
        row_w = TEETH_PER_ROW * TOOTH_W + (TEETH_PER_ROW - 1) * TOOTH_GAP
        x0 = MOUTH_CENTER[0] - row_w // 2
        self.upper = [pygame.Rect(x0 + i * (TOOTH_W + TOOTH_GAP), UPPER_TEETH_Y, TOOTH_W, TOOTH_H)
                      for i in range(TEETH_PER_ROW)]
        self.lower = [pygame.Rect(x0 + i * (TOOTH_W + TOOTH_GAP), LOWER_TEETH_Y, TOOTH_W, TOOTH_H)
                      for i in range(TEETH_PER_ROW)]
        # One rectangle covering all teeth, used for bacteria collisions
        self.teeth_rect = pygame.Rect(x0, UPPER_TEETH_Y, row_w, LOWER_TEETH_Y + TOOTH_H - UPPER_TEETH_Y)
        self.upper_gum = pygame.Rect(x0 - GUM_OVERHANG, UPPER_TEETH_Y - 35, row_w + 2 * GUM_OVERHANG, 65)
        self.lower_gum = pygame.Rect(x0 - GUM_OVERHANG, LOWER_TEETH_Y + TOOTH_H - 30, row_w + 2 * GUM_OVERHANG, 65)
        self.flash_timer = 0.0

    def reset(self):
        self.flash_timer = 0.0

    def trigger_flash(self):
        self.flash_timer = FLASH_DURATION

    def update(self, dt):
        self.flash_timer = max(0.0, self.flash_timer - dt)

    def draw(self, surface):
        cx, cy = MOUTH_CENTER
        lips = pygame.Rect(0, 0, *LIPS_SIZE); lips.center = (cx, cy)
        inner = pygame.Rect(0, 0, *INNER_MOUTH_SIZE); inner.center = (cx, cy)
        pygame.draw.ellipse(surface, LIP_RED, lips)
        pygame.draw.ellipse(surface, MOUTH_DARK, inner)
        pygame.draw.rect(surface, GUM_PINK, self.upper_gum, border_radius=30)
        pygame.draw.rect(surface, GUM_PINK, self.lower_gum, border_radius=30)
        for tooth in self.upper + self.lower:
            pygame.draw.rect(surface, TOOTH_WHITE, tooth, border_radius=TOOTH_RADIUS)
            pygame.draw.rect(surface, TOOTH_OUTLINE, tooth, 2, border_radius=TOOTH_RADIUS)
        # Red flash when bacteria reach the teeth
        if self.flash_timer > 0:
            alpha = int(FLASH_MAX_ALPHA * self.flash_timer / FLASH_DURATION)
            flash = pygame.Surface(self.teeth_rect.size, pygame.SRCALPHA)
            flash.fill((*FLASH_RED, alpha))
            surface.blit(flash, self.teeth_rect.topleft)


# ------------------------------------------------------------------ Particle
class Particle:
    """A short-lived visual effect: a sparkle star or an expanding ring."""

    def __init__(self, pos, vel, life, color, kind="spark"):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.life = self.max_life = life
        self.color = color
        self.kind = kind

    @property
    def alive(self):
        return self.life > 0

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt

    def draw(self, surface):
        t = max(0.0, self.life / self.max_life)          # 1 -> 0 over its life
        if self.kind == "ring":
            radius = int(RING_MAX_RADIUS * (1 - t)) + 2
            pygame.draw.circle(surface, self.color, self.pos, radius, 3)
        else:                                            # 4-point star
            size = 9 * t + 2
            pts = []
            for i in range(8):
                ang = i * math.pi / 4
                rad = size if i % 2 == 0 else size * 0.35
                pts.append((self.pos.x + math.cos(ang) * rad, self.pos.y + math.sin(ang) * rad))
            pygame.draw.polygon(surface, self.color, pts)


def make_pop(pos):
    """Create the 'pop' ring plus sparkles for a cleaned bacteria."""
    parts = [Particle(pos, (0, 0), RING_LIFE, WHITE, "ring")]
    for _ in range(SPARKLE_COUNT):
        ang = random.uniform(0, math.tau)
        speed = random.uniform(*SPARKLE_SPEED)
        vel = (math.cos(ang) * speed, math.sin(ang) * speed)
        parts.append(Particle(pos, vel, random.uniform(*SPARKLE_LIFE), random.choice(SPARKLE_COLORS)))
    return parts