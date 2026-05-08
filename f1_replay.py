"""
F1-Replay — Interactive Formula 1 Race Replay & Circuit Visualization
Python 3.13 | Libraries: pygame, matplotlib, numpy
Install: pip install pygame matplotlib numpy
"""

import pygame
import numpy as np
import math
import random
import sys
import time
from dataclasses import dataclass, field
from typing import ClassVar

# ─────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ─────────────────────────────────────────────
WIDTH, HEIGHT = 1400, 850
FPS = 60
TRACK_COLOR     = (30, 30, 40)
BG_COLOR        = (10, 10, 18)
WHITE           = (255, 255, 255)
YELLOW          = (255, 214, 0)
RED             = (220, 30, 30)
GREEN           = (0, 200, 80)
CYAN            = (0, 220, 255)
GRAY            = (80, 80, 100)
DARK_GRAY       = (25, 25, 35)
ORANGE          = (255, 120, 0)
PINK            = (255, 80, 160)
PURPLE          = (160, 60, 255)

TEAM_COLORS: dict[str, tuple[int, int, int]] = {
    "Red Bull":    (30,  65, 255),
    "Ferrari":     (220, 30,  30),
    "Mercedes":    (0,  210, 190),
    "McLaren":     (255,135,  0),
    "Aston Martin":(0,  110, 80),
    "Alpine":      (0,  147, 204),
    "Williams":    (0,  90, 200),
    "VCARB":       (30, 65, 200),
    "Haas":        (180,180,180),
    "Kick Sauber": (82, 226, 82),
}

# ─────────────────────────────────────────────
#  CIRCUIT DEFINITIONS  (normalised 0-1 coords)
# ─────────────────────────────────────────────
CIRCUITS: dict[str, dict] = {
    "Monza": {
        "name": "Autodromo Nazionale Monza",
        "country": "Italy 🇮🇹",
        "laps": 53,
        "points": [
            (0.50,0.10),(0.70,0.10),(0.85,0.15),(0.90,0.25),(0.88,0.38),
            (0.82,0.45),(0.75,0.48),(0.65,0.50),(0.55,0.55),(0.50,0.62),
            (0.50,0.75),(0.55,0.85),(0.55,0.90),(0.45,0.92),(0.35,0.88),
            (0.30,0.78),(0.30,0.65),(0.25,0.55),(0.18,0.45),(0.15,0.35),
            (0.18,0.22),(0.28,0.14),(0.40,0.10),(0.50,0.10),
        ],
        "drs_zones": [(0, 3), (12, 15)],
        "notable": "Temple of Speed — longest straight in F1",
    },
    "Monaco": {
        "name": "Circuit de Monaco",
        "country": "Monaco 🇲🇨",
        "laps": 78,
        "points": [
            (0.50,0.08),(0.65,0.08),(0.78,0.12),(0.88,0.20),(0.90,0.32),
            (0.85,0.42),(0.75,0.50),(0.65,0.55),(0.60,0.65),(0.62,0.76),
            (0.68,0.84),(0.62,0.90),(0.50,0.92),(0.38,0.90),(0.28,0.84),
            (0.20,0.74),(0.18,0.62),(0.22,0.52),(0.30,0.44),(0.28,0.33),
            (0.22,0.26),(0.28,0.16),(0.38,0.10),(0.50,0.08),
        ],
        "drs_zones": [(0, 2)],
        "notable": "Streets of Monte Carlo — no overtaking!",
    },
    "Silverstone": {
        "name": "Silverstone Circuit",
        "country": "United Kingdom 🇬🇧",
        "laps": 52,
        "points": [
            (0.50,0.08),(0.62,0.08),(0.75,0.12),(0.88,0.18),(0.92,0.28),
            (0.90,0.40),(0.85,0.50),(0.78,0.58),(0.70,0.62),(0.60,0.65),
            (0.55,0.72),(0.55,0.82),(0.48,0.90),(0.38,0.90),(0.28,0.85),
            (0.20,0.76),(0.15,0.65),(0.15,0.52),(0.20,0.40),(0.28,0.32),
            (0.32,0.22),(0.28,0.14),(0.38,0.10),(0.50,0.08),
        ],
        "drs_zones": [(0, 3), (11, 14)],
        "notable": "Home of British GP — iconic Copse & Maggotts-Becketts",
    },
    "Suzuka": {
        "name": "Suzuka International Racing Course",
        "country": "Japan 🇯🇵",
        "laps": 53,
        "points": [
            (0.50,0.08),(0.62,0.08),(0.75,0.12),(0.85,0.20),(0.88,0.32),
            (0.80,0.42),(0.68,0.46),(0.56,0.44),(0.50,0.50),(0.52,0.58),
            (0.60,0.64),(0.65,0.72),(0.60,0.80),(0.50,0.85),(0.38,0.82),
            (0.28,0.74),(0.22,0.64),(0.24,0.54),(0.30,0.46),(0.36,0.42),
            (0.30,0.34),(0.22,0.28),(0.20,0.18),(0.28,0.12),(0.38,0.08),(0.50,0.08),
        ],
        "drs_zones": [(0, 2), (13, 16)],
        "notable": "Figure-8 layout — Spoon Curve & 130R legendary",
    },
}

# ─────────────────────────────────────────────
#  DRIVER DATA
# ─────────────────────────────────────────────
DRIVERS_DATA = [
    ("VER", "Max Verstappen",       "Red Bull",    1),
    ("NOR", "Lando Norris",         "McLaren",     4),
    ("LEC", "Charles Leclerc",      "Ferrari",     16),
    ("PIA", "Oscar Piastri",        "McLaren",     81),
    ("SAI", "Carlos Sainz",         "Ferrari",     55),
    ("HAM", "Lewis Hamilton",       "Ferrari",     44),
    ("RUS", "George Russell",       "Mercedes",    63),
    ("ANT", "Kimi Antonelli",       "Mercedes",    12),
    ("ALO", "Fernando Alonso",      "Aston Martin",14),
    ("STR", "Lance Stroll",         "Aston Martin",18),
    ("GAS", "Pierre Gasly",         "Alpine",      10),
    ("COL", "Franco Colapinto",     "Alpine",       5),
    ("ALB", "Alexander Albon",      "Williams",    23),
    ("SAR", "Carlos Sainz Jr.",     "Williams",     2),
    ("TSU", "Yuki Tsunoda",         "VCARB",       22),
    ("LAW", "Liam Lawson",          "VCARB",       30),
    ("MAG", "Kevin Magnussen",      "Haas",        20),
    ("OCO", "Esteban Ocon",         "Haas",        31),
    ("HUL", "Nico Hulkenberg",      "Kick Sauber", 27),
    ("BOR", "Gabriel Bortoleto",    "Kick Sauber", 98),
]

# ─────────────────────────────────────────────
#  HELPER — smooth track spline
# ─────────────────────────────────────────────
def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t*t, t*t*t
    return (
        0.5*(2*p1[0] + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3),
        0.5*(2*p1[1] + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3),
    )

def build_spline(pts: list[tuple], steps: int = 30) -> list[tuple]:
    result = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[(i-1) % n]
        p1 = pts[i]
        p2 = pts[(i+1) % n]
        p3 = pts[(i+2) % n]
        for s in range(steps):
            result.append(catmull_rom(p0, p1, p2, p3, s/steps))
    return result

# ─────────────────────────────────────────────
#  CAR dataclass
# ─────────────────────────────────────────────
@dataclass
class Car:
    abbr: str
    name: str
    team: str
    number: int
    color: tuple[int,int,int]
    # race state
    progress: float = 0.0          # 0-1 position along track spline
    lap: int = 1
    lap_time: float = 0.0
    best_lap: float = float('inf')
    total_time: float = 0.0
    speed: float = 0.0
    base_speed: float = 0.0        # set at runtime
    pit_stops: int = 0
    is_pitting: bool = False
    pit_timer: float = 0.0
    drs_active: bool = False
    dnf: bool = False
    position: int = 0
    gap_to_leader: float = 0.0
    tyre: str = "Medium"
    tyre_age: int = 0
    tyre_deg: float = 0.0          # 0-1
    _trail: list = field(default_factory=list)
    TYRES: ClassVar[list[str]] = ["Soft","Medium","Hard"]

    def update(self, dt: float, spline: list[tuple], track_rect, total_laps: int):
        if self.dnf or self.lap > total_laps:
            return
        if self.is_pitting:
            self.pit_timer -= dt
            if self.pit_timer <= 0:
                self.is_pitting = False
                self.tyre = random.choice(self.TYRES)
                self.tyre_age = 0
                self.tyre_deg = 0.0
                self.pit_stops += 1
            return

        # tyre degradation
        self.tyre_age += dt
        self.tyre_deg = min(1.0, self.tyre_age / 120.0)
        grip = 1.0 - self.tyre_deg * 0.18

        # DRS boost
        drs_boost = 1.08 if self.drs_active else 1.0

        # speed variation — sinusoidal "throttle/braking"
        wave = math.sin(self.progress * math.tau * 3 + self.number) * 0.06
        self.speed = self.base_speed * grip * drs_boost * (1 + wave)

        advance = self.speed * dt
        self.progress += advance
        self.lap_time += dt
        self.total_time += dt

        if self.progress >= 1.0:
            self.progress -= 1.0
            if self.lap_time < self.best_lap:
                self.best_lap = self.lap_time
            self.lap_time = 0.0
            self.lap += 1
            # random pit
            if self.lap in range(15, total_laps - 5, 18) and self.pit_stops < 2:
                self.is_pitting = True
                self.pit_timer = random.uniform(2.5, 3.5)

        # trail
        px, py = self._track_pos(spline, track_rect)
        self._trail.append((px, py, self.drs_active))
        if len(self._trail) > 18:
            self._trail.pop(0)

    def _track_pos(self, spline, rect) -> tuple[float, float]:
        idx = int(self.progress * len(spline)) % len(spline)
        sx, sy = spline[idx]
        return rect.x + sx * rect.width, rect.y + sy * rect.height

    def draw(self, surface, spline, rect, font_tiny, selected: bool):
        if self.dnf or self.lap > 999:
            return
        px, py = self._track_pos(spline, rect)

        # trail
        for i, (tx, ty, drs) in enumerate(self._trail):
            alpha = int(180 * i / len(self._trail))
            r, g, b = (CYAN if drs else self.color)
            col = (min(r, 255), min(g, 255), min(b, 255))
            pygame.draw.circle(surface, (*col, alpha), (int(tx), int(ty)), max(1, i//4))

        # car body
        r = 7 if selected else 5
        pygame.draw.circle(surface, self.color, (int(px), int(py)), r + 2)
        pygame.draw.circle(surface, WHITE,      (int(px), int(py)), r)
        pygame.draw.circle(surface, self.color, (int(px), int(py)), r - 1)

        # DRS halo
        if self.drs_active:
            pygame.draw.circle(surface, CYAN, (int(px), int(py)), r+4, 1)

        # abbreviation label
        lbl = font_tiny.render(self.abbr, True, WHITE)
        surface.blit(lbl, (int(px)+8, int(py)-6))

# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class F1Replay:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("F1-Replay ⏱ Interactive Formula 1 Race Replay")
        self.screen   = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock    = pygame.time.Clock()

        self.font_h1  = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_h2  = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_sm  = pygame.font.SysFont("monospace", 14)
        self.font_xs  = pygame.font.SysFont("monospace", 11)

        self.circuit_key = "Monza"
        self.circuit      = CIRCUITS[self.circuit_key]
        self.spline: list = []
        self.track_rect   = pygame.Rect(60, 90, 780, 680)
        self._build_track()

        self.cars: list[Car] = []
        self._init_cars()

        self.running      = True
        self.paused       = False
        self.speed_mult   = 1.0        # 1×, 2×, 4×
        self.elapsed      = 0.0
        self.selected_idx = 0
        self.show_help    = False
        self.race_started = False
        self.lights_phase = 0          # 0=off 1-5=lights 6=go
        self.lights_timer = 0.0
        self.circuit_menu = False

        self._start_race()

    # ── SETUP ──────────────────────────────────
    def _build_track(self):
        pts = self.circuit["points"]
        scaled = [(x, y) for x, y in pts]
        self.spline = build_spline(scaled, steps=40)

    def _init_cars(self):
        self.cars = []
        speeds = np.linspace(0.200, 0.170, 20)   # top car fastest (fraction of lap per second)
        np.random.shuffle(speeds)
        for i, (abbr, name, team, num) in enumerate(DRIVERS_DATA):
            color = TEAM_COLORS.get(team, GRAY)
            c = Car(abbr=abbr, name=name, team=team, number=num, color=color)
            c.base_speed = float(speeds[i])
            c.progress   = -i * 0.008   # staggered start
            c.tyre       = random.choice(Car.TYRES)
            c.position   = i + 1
            self.cars.append(c)

    def _start_race(self):
        self.lights_phase = 1
        self.lights_timer = 0.0
        self.race_started = False

    # ── CIRCUIT SWITCH ─────────────────────────
    def _switch_circuit(self, key: str):
        self.circuit_key = key
        self.circuit     = CIRCUITS[key]
        self._build_track()
        self._init_cars()
        self._start_race()
        self.elapsed     = 0.0

    # ── EVENT LOOP ─────────────────────────────
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if   e.key == pygame.K_ESCAPE: self.running = False
                elif e.key == pygame.K_SPACE:  self.paused = not self.paused
                elif e.key == pygame.K_h:      self.show_help = not self.show_help
                elif e.key == pygame.K_c:      self.circuit_menu = not self.circuit_menu
                elif e.key == pygame.K_r:
                    self._init_cars(); self._start_race(); self.elapsed = 0.0
                elif e.key == pygame.K_RIGHT:
                    self.selected_idx = (self.selected_idx + 1) % len(self.cars)
                elif e.key == pygame.K_LEFT:
                    self.selected_idx = (self.selected_idx - 1) % len(self.cars)
                elif e.key == pygame.K_1: self.speed_mult = 1.0
                elif e.key == pygame.K_2: self.speed_mult = 2.0
                elif e.key == pygame.K_4: self.speed_mult = 4.0
                elif e.key == pygame.K_8: self.speed_mult = 8.0
                # circuit hotkeys
                for i, k in enumerate(CIRCUITS):
                    if e.key == getattr(pygame, f"K_{i+1}", None) and self.circuit_menu:
                        self._switch_circuit(k)
                        self.circuit_menu = False

    # ── UPDATE ─────────────────────────────────
    def update(self, dt: float):
        dt *= self.speed_mult

        # lights sequence
        if not self.race_started:
            self.lights_timer += dt
            if self.lights_timer > 0.8 and self.lights_phase < 6:
                self.lights_phase += 1
                self.lights_timer = 0
            if self.lights_phase == 6:
                self.race_started = True
            return

        if self.paused:
            return

        self.elapsed += dt

        # update cars
        for c in self.cars:
            c.update(dt, self.spline, self.track_rect, self.circuit["laps"])

        # assign positions
        active = [c for c in self.cars if not c.dnf and c.lap <= self.circuit["laps"]]
        active.sort(key=lambda c: -(c.lap + c.progress))
        for i, c in enumerate(active):
            c.position = i + 1

        # DRS: car within 1 second of car ahead gets DRS
        leader_prog = active[0].total_time if active else 0
        for i, c in enumerate(active):
            if i == 0:
                c.drs_active = False
                c.gap_to_leader = 0.0
            else:
                ahead = active[i-1]
                gap = abs(c.total_time - ahead.total_time) if c.lap == ahead.lap else 99
                c.drs_active = gap < 1.2
                c.gap_to_leader = active[0].total_time - c.total_time

        # random DNF (rare)
        for c in self.cars:
            if not c.dnf and c.lap > 5 and random.random() < 0.000008:
                c.dnf = True

    # ── DRAW HELPERS ───────────────────────────
    def _draw_track(self):
        tr = self.track_rect
        # background panel
        pygame.draw.rect(self.screen, DARK_GRAY, tr.inflate(20, 20), border_radius=12)

        # track outline (thick black)
        spline_px = [(tr.x + x*tr.width, tr.y + y*tr.height) for x, y in self.spline]
        if len(spline_px) > 2:
            pygame.draw.lines(self.screen, (0,0,0),   False, spline_px, 18)
            pygame.draw.lines(self.screen, TRACK_COLOR, False, spline_px, 14)
            pygame.draw.lines(self.screen, (50,50,70), False, spline_px, 2)

        # start/finish line
        s0 = spline_px[0]
        s1 = spline_px[1] if len(spline_px) > 1 else s0
        dx = s1[0]-s0[0]; dy = s1[1]-s0[1]
        norm = math.hypot(dx, dy) or 1
        nx, ny = -dy/norm * 12, dx/norm * 12
        pygame.draw.line(self.screen, YELLOW,
                         (int(s0[0]+nx), int(s0[1]+ny)),
                         (int(s0[0]-nx), int(s0[1]-ny)), 3)

        # circuit name overlay
        lbl = self.font_xs.render(self.circuit["name"], True, (120,120,140))
        self.screen.blit(lbl, (tr.x+6, tr.y+4))

    def _draw_cars(self):
        selected = self.cars[self.selected_idx] if self.cars else None
        for c in self.cars:
            c.draw(self.screen, self.spline, self.track_rect,
                   self.font_xs, selected=(c is selected))

    def _draw_timing_tower(self):
        x, y = 870, 90
        w, h = 510, 650
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((15, 15, 25, 230))
        pygame.draw.rect(surf, (50, 50, 70), (0, 0, w, h), 1, border_radius=6)
        self.screen.blit(surf, (x, y))

        active = sorted([c for c in self.cars if not c.dnf], key=lambda c: c.position)
        dnf_cars = [c for c in self.cars if c.dnf]

        # Header
        hdr = self.font_h2.render("LIVE TIMING", True, YELLOW)
        self.screen.blit(hdr, (x+10, y+8))
        lap_info = self.font_sm.render(
            f"LAP — / {self.circuit['laps']}  |  {self.circuit_key.upper()}",
            True, (160,160,180))
        self.screen.blit(lap_info, (x+10, y+34))
        pygame.draw.line(self.screen, (60,60,80), (x+8, y+55), (x+w-8, y+55), 1)

        row_h = 27
        for i, c in enumerate(active[:20]):
            ry = y + 62 + i * row_h
            sel = (c is self.cars[self.selected_idx])
            if sel:
                pygame.draw.rect(self.screen, (30,30,55), (x+4, ry-2, w-8, row_h-1), border_radius=3)

            # position badge
            badge_col = {1: YELLOW, 2: (200,200,200), 3: ORANGE}.get(c.position, GRAY)
            pygame.draw.rect(self.screen, badge_col, (x+8, ry, 22, 20), border_radius=3)
            pos_lbl = self.font_xs.render(str(c.position), True, (10,10,10))
            self.screen.blit(pos_lbl, (x+11 if c.position < 10 else x+9, ry+4))

            # team colour strip
            pygame.draw.rect(self.screen, c.color, (x+34, ry+2, 4, 16), border_radius=2)

            # abbreviation
            abbr_lbl = self.font_sm.render(c.abbr, True, WHITE if not sel else YELLOW)
            self.screen.blit(abbr_lbl, (x+42, ry+2))

            # lap
            lap_lbl = self.font_xs.render(f"L{c.lap}", True, (160,160,180))
            self.screen.blit(lap_lbl, (x+96, ry+5))

            # gap
            if c.position == 1:
                gap_txt = "LEADER"
                gap_col = GREEN
            else:
                gap_txt = f"+{c.gap_to_leader:.2f}s"
                gap_col = (200,200,200)
            gap_lbl = self.font_xs.render(gap_txt, True, gap_col)
            self.screen.blit(gap_lbl, (x+130, ry+5))

            # tyre indicator
            tyre_colors = {"Soft":(220,0,0),"Medium":(220,200,0),"Hard":(200,200,200)}
            tc = tyre_colors.get(c.tyre, GRAY)
            pygame.draw.circle(self.screen, tc, (x+248, ry+10), 6)
            tyre_age_lbl = self.font_xs.render(f"{int(c.tyre_age)}s", True, (140,140,160))
            self.screen.blit(tyre_age_lbl, (x+258, ry+5))

            # speed bar
            bar_w = int(c.speed / 0.22 * 80)
            pygame.draw.rect(self.screen, (30,30,50), (x+310, ry+6, 80, 8), border_radius=3)
            pygame.draw.rect(self.screen, c.color, (x+310, ry+6, min(bar_w,80), 8), border_radius=3)

            # pit indicator
            if c.is_pitting:
                pit_lbl = self.font_xs.render("PIT", True, ORANGE)
                self.screen.blit(pit_lbl, (x+400, ry+5))
            elif c.drs_active:
                drs_lbl = self.font_xs.render("DRS", True, CYAN)
                self.screen.blit(drs_lbl, (x+400, ry+5))

            # best lap
            if c.best_lap < float('inf'):
                bl = self.font_xs.render(f"{c.best_lap:.3f}", True, PURPLE)
                self.screen.blit(bl, (x+435, ry+5))

        # DNF section
        if dnf_cars:
            dnf_y = y + 62 + 21 * row_h
            dnf_hdr = self.font_xs.render("DNF", True, RED)
            self.screen.blit(dnf_hdr, (x+8, dnf_y))
            for j, c in enumerate(dnf_cars):
                self.screen.blit(
                    self.font_xs.render(f"{c.abbr} (OUT)", True, (140,50,50)),
                    (x+36 + j*80, dnf_y))

    def _draw_selected_info(self):
        c = self.cars[self.selected_idx]
        x, y = 870, 750
        lbl = self.font_sm.render(
            f"▶ {c.name}  #{c.number}  {c.team}  "
            f"P{c.position}  Lap {c.lap}/{self.circuit['laps']}  "
            f"Tyre: {c.tyre}[{int(c.tyre_age)}s]  "
            f"Pits: {c.pit_stops}  BL: {'--' if c.best_lap==float('inf') else f'{c.best_lap:.3f}'}",
            True, YELLOW)
        self.screen.blit(lbl, (x, y))

    def _draw_hud(self):
        # header bar
        pygame.draw.rect(self.screen, (18,18,28), (0, 0, WIDTH, 80))
        pygame.draw.line(self.screen, (50,50,70), (0,80), (WIDTH,80), 1)

        title = self.font_h1.render("F1-REPLAY  ⏱  INTERACTIVE RACE VISUALIZER", True, RED)
        self.screen.blit(title, (20, 20))

        flags = f"{'⏸ PAUSED' if self.paused else '▶ RUNNING'}   ×{self.speed_mult:.0f}   {self.elapsed:.1f}s"
        fl = self.font_sm.render(flags, True, (200,200,200))
        self.screen.blit(fl, (20, 52))

        # controls hint
        keys = "[SPACE] Pause  [1/2/4/8] Speed  [←/→] Select  [C] Circuit  [R] Restart  [H] Help"
        kl = self.font_xs.render(keys, True, (100,100,120))
        self.screen.blit(kl, (20, HEIGHT-20))

    def _draw_lights(self):
        if self.lights_phase == 0 or (self.race_started and self.lights_phase == 6):
            return
        cx, base_y = WIDTH//2, HEIGHT//2 - 60
        for i in range(5):
            lx = cx - 120 + i*60
            lit = i < self.lights_phase and self.lights_phase < 6
            col = RED if lit else (40,0,0)
            pygame.draw.circle(self.screen, col, (lx, base_y), 24)
            pygame.draw.circle(self.screen, (200,0,0) if lit else (20,0,0), (lx, base_y), 18)

        if self.lights_phase == 6:
            go = self.font_h1.render("GO! GO! GO!", True, GREEN)
            self.screen.blit(go, go.get_rect(center=(WIDTH//2, base_y+60)))

    def _draw_circuit_menu(self):
        if not self.circuit_menu:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))

        mx, my = WIDTH//2 - 280, HEIGHT//2 - 200
        panel = pygame.Surface((560, 420))
        panel.fill((18,18,28))
        pygame.draw.rect(panel, (60,60,90), (0,0,560,420), 2, border_radius=10)
        self.screen.blit(panel, (mx, my))

        hdr = self.font_h2.render("SELECT CIRCUIT", True, YELLOW)
        self.screen.blit(hdr, (mx+20, my+16))
        pygame.draw.line(self.screen, (60,60,90), (mx+8, my+48), (mx+552, my+48), 1)

        for i, (key, circ) in enumerate(CIRCUITS.items()):
            ry = my + 60 + i*80
            sel = key == self.circuit_key
            if sel:
                pygame.draw.rect(self.screen, (30,30,60), (mx+8, ry-4, 544, 68), border_radius=6)
            pygame.draw.rect(self.screen, TEAM_COLORS.get("Red Bull",(60,60,90)),
                             (mx+10, ry, 4, 56), border_radius=2)
            n_lbl = self.font_h2.render(f"[{i+1}]  {key}", True, YELLOW if sel else WHITE)
            self.screen.blit(n_lbl, (mx+24, ry+4))
            d_lbl = self.font_xs.render(f"{circ['country']}  •  {circ['laps']} laps  •  {circ['notable']}", True, (160,160,180))
            self.screen.blit(d_lbl, (mx+24, ry+30))

        close = self.font_sm.render("[C] or [ESC] to close", True, (120,120,140))
        self.screen.blit(close, (mx+20, my+390))

    def _draw_help(self):
        if not self.show_help:
            return
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,190))
        self.screen.blit(ov, (0,0))
        px, py = WIDTH//2 - 240, HEIGHT//2 - 180
        panel = pygame.Surface((480, 360))
        panel.fill((18,18,28))
        pygame.draw.rect(panel, (60,60,90), (0,0,480,360), 2, border_radius=10)
        self.screen.blit(panel, (px, py))
        lines = [
            ("F1-REPLAY  HELP", YELLOW),
            ("", WHITE),
            ("SPACE     Pause / Resume", WHITE),
            ("1 2 4 8   Speed multiplier", WHITE),
            ("← →       Select driver", WHITE),
            ("C         Circuit menu", WHITE),
            ("R         Restart race", WHITE),
            ("H         Toggle help", WHITE),
            ("ESC       Quit", WHITE),
            ("", WHITE),
            ("LEGEND:", CYAN),
            ("● Coloured dot = car position", WHITE),
            ("○ Cyan halo = DRS active", CYAN),
            ("PIT = Pit stop in progress", ORANGE),
            ("Tyre: 🔴 Soft 🟡 Medium ⚪ Hard", WHITE),
        ]
        for i, (txt, col) in enumerate(lines):
            if i == 0:
                s = self.font_h2.render(txt, True, col)
            else:
                s = self.font_sm.render(txt, True, col)
            self.screen.blit(s, (px+20, py+14+i*21))

    # ── MAIN DRAW ──────────────────────────────
    def draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_hud()
        self._draw_track()
        self._draw_cars()
        self._draw_timing_tower()
        self._draw_selected_info()
        self._draw_lights()
        self._draw_circuit_menu()
        self._draw_help()
        pygame.display.flip()

    # ── RUN ────────────────────────────────────
    def run(self):
        prev = time.perf_counter()
        while self.running:
            now = time.perf_counter()
            dt  = min(now - prev, 0.05)
            prev = now

            self.handle_events()
            self.update(dt)
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = F1Replay()
    app.run()
