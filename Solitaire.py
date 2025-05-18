import pygame
import random
import sys
import math

# ─── Configuration ───────────────────────────────────────────────────────────────
WIDTH, HEIGHT    = 1024, 768
FPS              = 60
CARD_W, CARD_H   = 100, 145
TABLEAU_Y        = 250
SPACING_DOWN     = 10
SPACING_UP       = 30

# Stocks draw count & waste display count
DIFFICULTY_SETTINGS = {'easy': 1, 'medium': 3, 'hard': 5}
WASTE_DISPLAY       = {'easy': 1, 'medium': 2, 'hard': 3}

SUITS        = ['S', 'H', 'D', 'C']
SUIT_SYMBOLS = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
RED_SUITS    = {'H', 'D'}
RANKS        = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
RANK_VALUE   = {r: i+1 for i, r in enumerate(RANKS)}

# Themes
THEMES = ['Basic','Casino','Pirate','Blue','Future','Dinosaur','Gold','Tiger','Alien','One Piece']
THEME_CONFIG = {
    'Basic':     {'bg': (0,120,0),   'back': (50,50,200)},
    'Casino':    {'bg': (100,0,0),   'back': (0,0,0)},
    'Pirate':    {'bg': (139,69,19), 'back': (255,215,0)},
    'Blue':      {'bg': (0,0,100),   'back': (0,128,255)},
    'Future':    {'bg': (70,70,70),  'back': (200,200,200)},
    'Dinosaur':  {'bg': (34,139,34), 'back': (107,142,35)},
    'Gold':      {'bg': (218,165,32), 'back': (255,215,0)},
    'Tiger':     {'bg': (255,140,0), 'back': (255,69,0)},
    'Alien':     {'bg': (75,0,130),  'back': (148,0,211)},
    'One Piece': {'bg': (0,191,255), 'back': (255,215,0)},
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solitaire")
clock = pygame.time.Clock()
font_s = pygame.font.SysFont(None, 24)
font_L = pygame.font.SysFont(None, 48, bold=True)

# ─── Difficulty Selection ────────────────────────────────────────────────────────
def select_difficulty():
    rects = []
    w, h = 200, 60
    for i, label in enumerate(['easy', 'medium', 'hard']):
        rects.append((pygame.Rect((WIDTH//2 - w//2, 200 + i*100), (w, h)), label))
    while True:
        screen.fill((30, 30, 30))
        title = font_L.render("Select Difficulty", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for rect, label in rects:
            pygame.draw.rect(screen, (100, 100, 100), rect)
            txt = font_s.render(label.capitalize(), True, (255, 255, 255))
            screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for rect, label in rects:
                    if rect.collidepoint(e.pos):
                        return label
        pygame.display.flip()
        clock.tick(FPS)

# ─── Generate Card Faces ─────────────────────────────────────────────────────────
def make_card_faces():
    faces = {}
    for suit in SUITS:
        for rank in RANKS:
            surf = pygame.Surface((CARD_W, CARD_H))
            surf.fill((255,255,255))
            pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
            color = (200,0,0) if suit in RED_SUITS else (0,0,0)
            corner = font_s.render(rank + SUIT_SYMBOLS[suit], True, color)
            surf.blit(corner, (5,5))
            rot = pygame.transform.rotate(corner, 180)
            surf.blit(rot, (CARD_W-rot.get_width()-5, CARD_H-rot.get_height()-5))
            big = font_L.render(SUIT_SYMBOLS[suit], True, color)
            bw, bh = big.get_size()
            surf.blit(big, ((CARD_W-bw)//2, (CARD_H-bh)//2 - 10))
            faces[rank + suit] = surf
    return faces

card_faces = make_card_faces()
card_back = None

# ─── Card Class ─────────────────────────────────────────────────────────────────
class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
        self.rect = pygame.Rect(0, 0, CARD_W, CARD_H)
    def draw(self, surf, x, y):
        self.rect.topleft = (x, y)
        if self.face_up:
            surf.blit(card_faces[self.rank + self.suit], self.rect)
        else:
            surf.blit(card_back, self.rect)

# ─── Deck Creation ───────────────────────────────────────────────────────────────
def create_deck():
    deck = [Card(s, r, False) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

# ─── Main Solitaire Game ─────────────────────────────────────────────────────────
class SolitaireGame:
    def __init__(self, difficulty):
        # Random theme
        self.theme = random.choice(THEMES)
        cfg = THEME_CONFIG[self.theme]
        self.bg_color = cfg['bg']
        global card_back
        card_back = pygame.Surface((CARD_W, CARD_H))
        card_back.fill(cfg['back'])
        pygame.draw.rect(card_back, (255,255,255), card_back.get_rect(), 2)

        # Initialize state
        self.difficulty = difficulty
        self.draw_n = DIFFICULTY_SETTINGS[difficulty]
        self.disp_n = WASTE_DISPLAY[difficulty]
        self.deck = create_deck()
        self.waste = []
        self.found = [[] for _ in range(4)]
        self.tableau = [[] for _ in range(7)]
        self.history = []
        self.undo_btn = pygame.Rect(WIDTH-120, 50, 100, 40)
        self.play_btn = pygame.Rect(WIDTH//2-100, HEIGHT//2+50, 200, 50)
        self.shake = None
        self.anims = []
        self.mouse_info = None
        self.won = False
        self.start_time = pygame.time.get_ticks()
        self._deal()
        # Drag state
        self.dragging = False
        self.drag_cards = []
        self.drag_orig = None
        self.drag_offset = (0, 0)
        self.drag_pos = (0, 0)

    def _deal(self):
        for i in range(7):
            for j in range(i+1):
                c = self.deck.pop()
                c.face_up = (j == i)
                self.tableau[i].append(c)

    def start_shake(self):
        self.shake = {'t': 20, 'o': 0, 'd': 1}

    def _auto_flip(self, orig):
        if orig and orig[0] == 'tableau':
            idx = orig[1]
            pile = self.tableau[idx]
            if pile and not pile[-1].face_up:
                pile[-1].face_up = True

    def _ok_tab(self, c, top):
        return ((c.suit in RED_SUITS) != (top.suit in RED_SUITS)
                and RANK_VALUE[c.rank] + 1 == RANK_VALUE[top.rank])

    def _ok_found(self, c, f):
        if not f:
            return c.rank == 'A'
        return c.suit == f[-1].suit and RANK_VALUE[c.rank] == RANK_VALUE[f[-1].rank] + 1

    def attempt_auto_from_pile(self, idx):
        pile = self.tableau[idx]
        if not pile:
            return False
        c = pile[-1]
        rest = pile[:-1]
        for i, f in enumerate(self.found):
            if self._ok_found(c, f):
                pile.pop()
                self.start_slide([c], ('tableau', idx, rest), 'found', i)
                return True
        return False

    def attempt_auto_move_waste(self):
        if not self.waste:
            return
        c = self.waste.pop()
        for i, f in enumerate(self.found):
            if self._ok_found(c, f):
                self.start_slide([c], ('waste',), 'found', i)
                return
        for i, p in enumerate(self.tableau):
            if (p and self._ok_tab(c, p[-1])) or (not p and c.rank == 'K'):
                self.start_slide([c], ('waste',), 'tableau', i)
                return
        # Invalid
        self.waste.append(c)
        self.start_shake()

    def start_slide(self, cards, orig, dest, idx):
        sx, sy = cards[0].rect.topleft
        dur = 15 if orig[0] == 'waste' else 10
        if dest == 'found':
            ex, ey = 400 + idx*120, 50
        elif dest == 'tableau':
            ex, ey = 50 + idx*120, TABLEAU_Y + len(self.tableau[idx]) * SPACING_UP
        else:
            ex, ey = 170 + len(self.waste) * 20, 50 + len(self.waste) * 5
        self.anims.append({'cards': cards, 'orig': orig, 'dest': (dest, idx), 's': (sx, sy), 'e': (ex, ey), 'p': 0, 'd': dur})

    def on_mouse_down(self, pos):
        if self.won and self.play_btn.collidepoint(pos):
            self.__init__(self.difficulty)
            return
        if self.undo_btn.collidepoint(pos):
            self.undo()
            return
        # Auto tableau
        for i, p in enumerate(self.tableau):
            if p and p[-1].rect.collidepoint(pos):
                if self.attempt_auto_from_pile(i):
                    return
        # Stock click
        sr = pygame.Rect(50, 50, CARD_W, CARD_H)
        if sr.collidepoint(pos):
            if self.deck:
                drawn = []
                for _ in range(min(self.draw_n, len(self.deck))):
                    c = self.deck.pop()
                    c.face_up = True
                    drawn.append(c)
                self.start_slide(drawn, ('stock',), 'waste', None)
                self.history.append({'type': 'draw', 'cards': drawn})
            else:
                saved = list(self.waste)
                self.history.append({'type': 'draw', 'cards': saved, 'recycle': True})
                self.deck = list(reversed(self.waste))
                self.waste.clear()
            return
        # Waste click/drag
        if self.waste and self.waste[-1].rect.collidepoint(pos):
            self.mouse_info = ('waste',)
            return
        # Tableau drag
        for i, p in enumerate(self.tableau):
            for j in range(len(p)-1, -1, -1):
                if p[j].face_up and p[j].rect.collidepoint(pos):
                    mv, rest = p[j:], p[:j]
                    del p[j:]
                    self._start_drag(mv, ('tableau', i, rest), pos)
                    return

    def on_mouse_motion(self, pos):
        if self.mouse_info and not self.dragging:
            ox, oy = self.waste[-1].rect.topleft if self.waste else pos
            if (pos[0]-ox)**2 + (pos[1]-oy)**2 > 25:
                c = self.waste.pop()
                self._start_drag([c], ('waste',), pos)
                self.mouse_info = None
                return
        if self.dragging:
            self.drag_pos = pos

    def on_mouse_up(self, pos):
        if self.mouse_info and not self.dragging:
            self.attempt_auto_move_waste()
            self.mouse_info = None
            return
        if not self.dragging:
            return
        cards, orig = self.drag_cards, self.drag_orig
        # Foundations
        for i, f in enumerate(self.found):
            fr = pygame.Rect(400+i*120, 50, CARD_W, CARD_H)
            if fr.collidepoint(pos) and self._ok_found(cards[0], f):
                self.start_slide(cards, orig, 'found', i)
                self._end_drag()
                return
        # Tableau
        for i, p in enumerate(self.tableau):
            tr = pygame.Rect(50+i*120, TABLEAU_Y, CARD_W, CARD_H)
            if ((not p and cards[0].rank == 'K' and tr.collidepoint(pos)) or
               (p and p[-1].rect.collidepoint(pos) and self._ok_tab(cards[0], p[-1]))):
                self.start_slide(cards, orig, 'tableau', i)
                self._end_drag()
                return
        # Snap back
        if orig[0] == 'waste':
            self.waste.extend(cards)
        else:
            idx, rest = orig[1], orig[2]
            self.tableau[idx] = rest + cards
        self._end_drag()

    def _start_drag(self, cards, orig, pos):
        self.dragging    = True
        self.drag_cards  = cards
        self.drag_orig   = orig
        ox, oy = cards[0].rect.topleft
        mx, my = pos
        self.drag_offset = (mx - ox, my - oy)
        self.drag_pos    = pos

    def _end_drag(self):
        self.dragging    = False
        self.drag_cards  = []
        self.drag_orig   = None

    def undo(self):
        if not self.history:
            return
        act = self.history.pop()
        if act.get('recycle'):
            self.deck.clear()
            self.waste = act['cards'][:]
            for c in self.waste:
                c.face_up = True
            return
        if act['type'] == 'draw':
            for c in reversed(act['cards']):
                c.face_up = False
                self.deck.append(c)

    def update(self):
        # Win detection
        if not self.won and all(len(f) == 13 for f in self.found):
            self.won = True
        # Shake animation
        if self.shake:
            self.shake['t'] -= 1
            off = self.shake['o'] + self.shake['d'] * 5
            if abs(off) > 20:
                self.shake['d'] *= -1
                off = self.shake['o'] + self.shake['d'] * 5
            self.shake['o'] = off
            if self.shake['t'] <= 0:
                self.shake = None
        # Slide animations
        new_anims = []
        for anim in self.anims:
            anim['p'] += 1
            t = anim['p'] / anim['d']
            ease = 0.5 - math.cos(math.pi * t) / 2
            sx, sy = anim['s']; ex, ey = anim['e']
            x = int(sx + (ex - sx) * ease)
            y = int(sy + (ey - sy) * ease)
            if anim['p'] >= anim['d']:
                dest, idx = anim['dest']
                cards = anim['cards']
                if dest == 'found':
                    self.found[idx].extend(cards)
                elif dest == 'tableau':
                    self.tableau[idx].extend(cards)
                else:
                    self.waste.extend(cards)
                self._auto_flip(anim['orig'])
                self.history.append({'type': 'move', 'cards': cards})
            else:
                new_anims.append(anim)
        self.anims = new_anims

    def draw(self, surf):
        surf.fill(self.bg_color)
        # Timer
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        surf.blit(font_s.render(f"Time: {elapsed//60:02d}:{elapsed%60:02d}", True, (255,255,255)), (50,5))
        # Undo button
        pygame.draw.rect(surf, (200,200,200), self.undo_btn)
        surf.blit(font_s.render("Undo", True, (0,0,0)), (self.undo_btn.x+20, self.undo_btn.y+10))
        # Stock
        if self.deck:
            surf.blit(card_back, (50,50))
        # Waste
        for i, c in enumerate(self.waste[-self.disp_n:]):
            c.draw(surf, 170 + i*20, 50 + i*5)
        # Foundations
        for i, f in enumerate(self.found):
            x, y = 400 + i*120, 50
            rect = pygame.Rect(x, y, CARD_W, CARD_H)
            if f:
                f[-1].draw(surf, x, y)
            else:
                pygame.draw.rect(surf, (255,255,255), rect, 2)
                icon = font_L.render(SUIT_SYMBOLS[SUITS[i]], True, (200,200,200))
                surf.blit(icon, (x + (CARD_W-icon.get_width())//2, y + (CARD_H-icon.get_height())//2))
        # Tableau
        for i, pile in enumerate(self.tableau):
            x, y = 50 + i*120, TABLEAU_Y
            for c in pile:
                c.draw(surf, x, y)
                y += SPACING_UP if c.face_up else SPACING_DOWN
        # Dragging
        if self.dragging:
            mx, my = self.drag_pos
            ox, oy = self.drag_offset
            for idx, c in enumerate(self.drag_cards):
                c.draw(surf, mx-ox, my-oy + idx*SPACING_UP)
        # Animations
        for anim in self.anims:
            t = anim['p'] / anim['d']
            ease = 0.5 - math.cos(math.pi * t) / 2
            sx, sy = anim['s']; ex, ey = anim['e']
            x = int(sx + (ex - sx) * ease)
            y = int(sy + (ey - sy) * ease)
            for idx, c in enumerate(anim['cards']):
                c.draw(surf, x, y + idx*SPACING_UP)
        # Win screen
        if self.won:
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(180); overlay.fill((0,0,0))
            surf.blit(overlay, (0,0))
            wt = font_L.render("You Win!", True, (255,255,0))
            surf.blit(wt, (WIDTH//2-wt.get_width()//2, HEIGHT//2-50))
            pygame.draw.rect(surf, (100,200,100), self.play_btn)
            pt = font_s.render("Play Again", True, (0,0,0))
            surf.blit(pt, (self.play_btn.x+40, self.play_btn.y+15))

# ─── Main Loop ─────────────────────────────────────────────────────────────────
def run_game():
    diff = select_difficulty()
    game = SolitaireGame(diff)
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                game.on_mouse_down(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP:
                game.on_mouse_up(e.pos)
            elif e.type == pygame.MOUSEMOTION:
                game.on_mouse_motion(e.pos)
        game.update()
        game.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    run_game()
