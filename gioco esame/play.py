import pygame
import json
import tkinter as tk
from tkinter import filedialog

# Inizializzazione di Pygame
pygame.init()

# Inizializzazione di Tkinter
root = tk.Tk()
root.withdraw()  # Nasconde la finestra principale di Tkinter

# Costanti per la finestra
LARGHEZZA, ALTEZZA = 800, 600
FINESTRA = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Geometry Dash Clone")

# Colori
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)

# Costanti del gioco
ICON_SIZE = 50
BLOCK_SIZE = 50
SPIKE_SIZE = 50
SCROLL_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -10.5
FPS = 60
START_X = -50
END_X = 100

# Caricamento delle immagini
icon_image = pygame.image.load('icons/icon.png').convert_alpha()
base_image = pygame.image.load('assets/base.png').convert()
bg_image = pygame.image.load('assets/bg.png').convert_alpha()  # Usa convert_alpha per supportare la trasparenza
block_image = pygame.image.load('assets/block.png').convert_alpha()
spike_image = pygame.image.load('assets/spike.png').convert_alpha()
end_image = pygame.image.load('assets/end.png').convert_alpha()

# Ridimensionamento delle immagini
icon_image = pygame.transform.scale(icon_image, (ICON_SIZE, ICON_SIZE))
block_image = pygame.transform.scale(block_image, (BLOCK_SIZE, BLOCK_SIZE))
spike_image = pygame.transform.scale(spike_image, (SPIKE_SIZE, SPIKE_SIZE))
end_image = pygame.transform.scale(end_image, (BLOCK_SIZE, BLOCK_SIZE))  # End occupa un blocco di altezza
base_image = pygame.transform.scale(base_image, (LARGHEZZA, 50))
bg_image = pygame.transform.scale(bg_image, (LARGHEZZA, ALTEZZA))

# Posizione iniziale del personaggio
icon_x = START_X
icon_y = ALTEZZA - 50 - ICON_SIZE

# Variabili di stato del personaggio
icon_velocity_y = 0
on_ground = True
rotation_angle = 0
rotation_speed = 0
total_rotation = 0
intro_done = False

# Variabile per tenere traccia dello stato del mouse
mouse_held = False

# Variabile per tenere traccia del livello corrente
current_level = None

# Imposta il framerate
clock = pygame.time.Clock()

# Colore di sfondo iniziale
current_bg_color = (255, 255, 255, 0)
target_bg_color = (255, 255, 255, 0)
bg_transition_time = 0
bg_transition_progress = 0

# Dati del livello originale per il reset
level_data = None
original_objects = []
music_path = None

def load_level():
    global current_level, level_data, original_objects, music_path
    file_path = filedialog.askopenfilename(initialdir="levels", title="Seleziona un livello",
                                           filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
    if file_path:
        current_level = file_path
        with open(file_path, 'r') as file:
            level_data = json.load(file)
        original_objects = level_data["objects"]
        music_path = level_data.get("music")
        return level_data
    return None

def reset_level():
    global oggetti, icon_x, icon_y, icon_velocity_y, on_ground, rotation_angle, rotation_speed, total_rotation, intro_done, current_bg_color, target_bg_color, bg_transition_time, bg_transition_progress, mouse_held
    oggetti = json.loads(json.dumps(original_objects))  # Ripristina gli oggetti originali
    icon_x = START_X
    icon_y = ALTEZZA - 50 - ICON_SIZE
    icon_velocity_y = 0
    on_ground = True
    rotation_angle = 0
    rotation_speed = 0
    total_rotation = 0
    mouse_held = False
    intro_done = False
    current_bg_color = (255, 255, 255, 0)
    target_bg_color = (255, 255, 255, 0)
    bg_transition_time = 0
    bg_transition_progress = 0
    if music_path:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # Riproduce la musica in loop

# Caricamento del livello
level_data = load_level()
if level_data:
    oggetti = json.loads(json.dumps(original_objects))  # Copia degli oggetti per modifiche temporanee
    if music_path:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # Riproduce la musica in loop
else:
    oggetti = []
    music_path = None

def draw_repeating_background(scroll_x):
    background_surface = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
    for x in range(-scroll_x % LARGHEZZA - LARGHEZZA, LARGHEZZA * 2, LARGHEZZA):
        background_surface.blit(bg_image, (x, 0))
    
    # Applica l'overlay del colore di sfondo
    color_overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
    color_overlay.fill(current_bg_color)
    background_surface.blit(color_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    FINESTRA.blit(background_surface, (0, 0))

def draw_repeating_base(scroll_x):
    for x in range(-scroll_x % LARGHEZZA - LARGHEZZA, LARGHEZZA * 2, LARGHEZZA):
        FINESTRA.blit(base_image, (x, ALTEZZA - 50))

def handle_events():
    global mouse_held, running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False

def closest_rotation_angle(angle):
    lower_bound = (angle // 90) * 90
    upper_bound = lower_bound + 90
    return upper_bound if angle - lower_bound > upper_bound - angle else lower_bound

def update_player():
    global icon_velocity_y, icon_y, on_ground, rotation_angle, rotation_speed, total_rotation, intro_done, icon_x

    if not intro_done:
        icon_x += SCROLL_SPEED
        if icon_x >= END_X:
            icon_x = END_X
            intro_done = True
        return

    icon_velocity_y += GRAVITY
    icon_y += icon_velocity_y

    # Controllo collisioni con gli oggetti
    player_rect = pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE)
    player_landed = False
    for obj in oggetti:
        if obj["type"] == "block":
            obj_rect = pygame.Rect(obj["x"], obj["y"], BLOCK_SIZE, BLOCK_SIZE)
            top_rect = pygame.Rect(obj["x"], obj["y"] - 1, BLOCK_SIZE, 1)
            if player_rect.colliderect(top_rect) and icon_velocity_y >= 0:
                icon_y = obj["y"] - ICON_SIZE
                icon_velocity_y = 0
                on_ground = True
                player_landed = True
            elif player_rect.colliderect(obj_rect):
                game_over()
        elif obj["type"] == "spike":
            obj_rect = pygame.Rect(obj["x"], obj["y"], SPIKE_SIZE, SPIKE_SIZE)
            if player_rect.colliderect(obj_rect):
                game_over()
        elif obj["type"] == "bgcolor":
            obj_rect = pygame.Rect(obj["x"], obj["y"], BLOCK_SIZE, BLOCK_SIZE)
            if player_rect.colliderect(obj_rect):
                start_bg_transition(pygame.Color(obj["color"]), obj["time"])
        elif obj["type"] == "end":
            obj_rect = pygame.Rect(obj["x"], obj["y"], BLOCK_SIZE, BLOCK_SIZE)
            if player_rect.colliderect(obj_rect):
                level_complete()

    if icon_y >= ALTEZZA - 50 - ICON_SIZE:
        icon_y = ALTEZZA - 50 - ICON_SIZE
        icon_velocity_y = 0
        on_ground = True
        player_landed = True

    if player_landed:
        rotation_angle = closest_rotation_angle(rotation_angle)
        total_rotation = (total_rotation + rotation_angle) % 360
        if total_rotation < 0:
            total_rotation += 360
        total_rotation = closest_rotation_angle(total_rotation)
        rotation_speed = 0
        rotation_angle = 0
    else:
        if on_ground:
            rotation_speed = 180 / (2 * abs(JUMP_STRENGTH) / GRAVITY)
        on_ground = False
        rotation_angle -= rotation_speed

    if mouse_held and on_ground:
        icon_velocity_y = JUMP_STRENGTH
        on_ground = False
        rotation_speed = 180 / (2 * abs(JUMP_STRENGTH) / GRAVITY)

def start_bg_transition(target_color, duration):
    global target_bg_color, bg_transition_time, bg_transition_progress
    target_bg_color = target_color
    bg_transition_time = duration * FPS
    bg_transition_progress = 0

def update_bg_color():
    global current_bg_color, bg_transition_progress, target_bg_color
    if bg_transition_progress < bg_transition_time:
        bg_transition_progress += 1
        progress_ratio = bg_transition_progress / bg_transition_time
        current_bg_color = [
            int(current_bg_color[i] + (target_bg_color[i] - current_bg_color[i]) * progress_ratio)
            for i in range(3)
        ]
        current_bg_color = tuple(current_bg_color)

def draw_objects():
    for obj in oggetti:
        obj["x"] -= SCROLL_SPEED
        if obj["type"] == "block":
            FINESTRA.blit(block_image, (obj["x"], obj["y"]))
        elif obj["type"] == "spike":
            FINESTRA.blit(spike_image, (obj["x"], obj["y"]))
        elif obj["type"] == "bgcolor":
            pygame.draw.rect(FINESTRA, pygame.Color(obj["color"]), (obj["x"], obj["y"], BLOCK_SIZE, BLOCK_SIZE))
        elif obj["type"] == "end":
            FINESTRA.blit(end_image, (obj["x"], obj["y"]))

def draw_player():
    current_rotation = total_rotation + rotation_angle
    rotated_icon = pygame.transform.rotate(icon_image, current_rotation)
    icon_rect = rotated_icon.get_rect(center=(icon_x + ICON_SIZE // 2, icon_y + ICON_SIZE // 2))
    FINESTRA.blit(rotated_icon, icon_rect.topleft)

def game_over():
    global running
    print("Game Over")
    reset_level()

def level_complete():
    global running
    print("Level Complete")
    running = False  # Termina il gioco quando il livello è completato

scroll_x = 0
running = True
while running:
    FINESTRA.fill(BIANCO)

    scroll_x += SCROLL_SPEED

    draw_repeating_background(scroll_x)
    draw_repeating_base(scroll_x)

    handle_events()
    update_player()
    update_bg_color()
    draw_objects()
    draw_player()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
