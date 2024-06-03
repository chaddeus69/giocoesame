import pygame
import json
import tkinter as tk
from tkinter import simpledialog, filedialog, colorchooser
import os

# Inizializzazione di Pygame
pygame.init()

# Inizializzazione di Tkinter
root = tk.Tk()
root.withdraw()  # Nasconde la finestra principale di Tkinter

# Costanti per la finestra
LARGHEZZA, ALTEZZA = 800, 600
FINESTRA = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Level Editor")

# Colori
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
GRIGIO = (200, 200, 200)
ROSSO = (255, 0, 0)
VERDE = (0, 255, 0)
ARANCIONE = (255, 165, 0)
BLU = (0, 0, 255)
CELESTE = (173, 216, 230)

# Dimensioni dei pulsanti di selezione
BUTTON_SIZE = 50

# Caricamento delle immagini
block_image = pygame.image.load('assets/block.png')
spike_image = pygame.image.load('assets/spike.png')
base_image = pygame.image.load('assets/base.png')
bg_image = pygame.image.load('assets/bg.png')
end_image = pygame.image.load('assets/end.png')
wave_image = pygame.image.load('assets/wave.png')
bgcolor_image = pygame.image.load('assets/bgcolor.png')

# Ridimensionamento delle immagini
BLOCK_SIZE = 50
SPIKE_SIZE = 50
GRID_SIZE = 50

block_image = pygame.transform.scale(block_image, (BLOCK_SIZE, BLOCK_SIZE))
spike_image = pygame.transform.scale(spike_image, (SPIKE_SIZE, SPIKE_SIZE))
base_image = pygame.transform.scale(base_image, (LARGHEZZA, 50))
bg_image = pygame.transform.scale(bg_image, (LARGHEZZA, ALTEZZA))
end_image = pygame.transform.scale(end_image, (BLOCK_SIZE, BLOCK_SIZE))
wave_image = pygame.transform.scale(wave_image, (BLOCK_SIZE, BLOCK_SIZE * 2))
bgcolor_image = pygame.transform.scale(bgcolor_image, (BLOCK_SIZE, BLOCK_SIZE))

# Ridimensionamento per i pulsanti di selezione
wave_button_image = pygame.transform.scale(wave_image, (BUTTON_SIZE, BUTTON_SIZE))

# Posizioni dei pulsanti di selezione
block_button_rect = pygame.Rect(10, 10, BUTTON_SIZE, BUTTON_SIZE)
spike_button_rect = pygame.Rect(70, 10, BUTTON_SIZE, BUTTON_SIZE)
end_button_rect = pygame.Rect(130, 10, BUTTON_SIZE, BUTTON_SIZE)
wave_button_rect = pygame.Rect(190, 10, BUTTON_SIZE, BUTTON_SIZE)
bgcolor_button_rect = pygame.Rect(250, 10, BUTTON_SIZE, BUTTON_SIZE)
close_button_rect = pygame.Rect(LARGHEZZA - 60, 10, 50, 50)  # Pulsante "X" in alto a destra
open_button_rect = pygame.Rect(LARGHEZZA - 120, 10, 50, 50)  # Pulsante "+" per aprire un livello
music_button_rect = pygame.Rect(LARGHEZZA - 180, 10, 50, 50)  # Pulsante "M" per scegliere la musica
delete_button_rect = pygame.Rect(LARGHEZZA - 240, 10, 50, 50)  # Pulsante "D" per cancellare oggetti

# Tipo di oggetto attualmente selezionato
current_object = None
current_music = None  # Percorso del file della musica selezionata

# Variabili per tenere traccia degli oggetti nel livello
oggetti = []

# Variabili per lo scorrimento
scroll_x = 0
scroll_y = 0
SCROLL_SPEED = 20

def draw_repeating_background():
    for x in range(-scroll_x % LARGHEZZA - LARGHEZZA, LARGHEZZA * 2, LARGHEZZA):
        for y in range(-scroll_y % ALTEZZA - ALTEZZA, ALTEZZA * 2, ALTEZZA):
            FINESTRA.blit(bg_image, (x, y))

def draw_repeating_base():
    for x in range(-scroll_x % LARGHEZZA - LARGHEZZA, LARGHEZZA * 2, LARGHEZZA):
        FINESTRA.blit(base_image, (x, ALTEZZA - 50 - scroll_y))

def draw_grid():
    for x in range(0, LARGHEZZA, GRID_SIZE):
        pygame.draw.line(FINESTRA, GRIGIO, (x - scroll_x % GRID_SIZE, 0), (x - scroll_x % GRID_SIZE, ALTEZZA))
    for y in range(0, ALTEZZA, GRID_SIZE):
        pygame.draw.line(FINESTRA, GRIGIO, (0, y - scroll_y % GRID_SIZE), (LARGHEZZA, y - scroll_y % GRID_SIZE))

def snap_to_grid(x, y):
    return (x // GRID_SIZE) * GRID_SIZE, (y // GRID_SIZE) * GRID_SIZE

def save_level():
    livello = {
        "level_name": "example_level",
        "objects": oggetti,
        "music": current_music  # Salva il percorso della musica
    }
    file_name = simpledialog.askstring("Salva livello", "Inserisci il nome del livello:")
    if file_name:
        if not os.path.exists('levels'):
            os.makedirs('levels')
        with open(f'levels/{file_name}.json', 'w') as file:
            json.dump(livello, file)
        print(f"Livello salvato come {file_name}.json")

def load_level():
    file_path = filedialog.askopenfilename(initialdir="levels", title="Seleziona un livello",
                                           filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
    if file_path:
        with open(file_path, 'r') as file:
            livello = json.load(file)
            global oggetti, current_music
            oggetti = livello["objects"]
            current_music = livello.get("music")
        print(f"Livello {file_path} caricato")

def choose_music():
    global current_music
    file_path = filedialog.askopenfilename(initialdir="music", title="Seleziona un file musicale",
                                           filetypes=(("MP3 files", "*.mp3"), ("all files", "*.*")))
    if file_path:
        current_music = file_path
        print(f"Musica selezionata: {file_path}")

def choose_bgcolor():
    color_code = colorchooser.askcolor(title="Scegli un colore")[1]
    if not color_code:
        return None, None
    color_time = simpledialog.askfloat("Tempo di transizione", "Inserisci il tempo di transizione (massimo 2.5 secondi):", minvalue=0, maxvalue=2.5)
    return color_code, color_time

def delete_object(x, y):
    for obj in oggetti:
        if obj["x"] == x and obj["y"] == y:
            oggetti.remove(obj)
            break

# Ciclo principale del gioco
running = True
while running:
    FINESTRA.fill(BIANCO)
    draw_repeating_background()
    draw_repeating_base()
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if block_button_rect.collidepoint(x, y):
                current_object = "block"
            elif spike_button_rect.collidepoint(x, y):
                current_object = "spike"
            elif end_button_rect.collidepoint(x, y):
                current_object = "end"
            elif wave_button_rect.collidepoint(x, y):
                current_object = "wave"
            elif bgcolor_button_rect.collidepoint(x, y):
                current_object = "bgcolor"
            elif close_button_rect.collidepoint(x, y):
                save_level()
            elif open_button_rect.collidepoint(x, y):
                load_level()
            elif music_button_rect.collidepoint(x, y):
                choose_music()
            elif delete_button_rect.collidepoint(x, y):
                current_object = "delete"
            else:
                x, y = snap_to_grid(x + scroll_x, y + scroll_y)
                if current_object == "delete":
                    delete_object(x, y)
                elif current_object == "block":
                    oggetti.append({"type": "block", "x": x, "y": y})
                elif current_object == "spike":
                    oggetti.append({"type": "spike", "x": x, "y": y})
                elif current_object == "end":
                    oggetti.append({"type": "end", "x": x, "y": y})
                elif current_object == "wave":
                    oggetti.append({"type": "wave", "x": x, "y": y})
                elif current_object == "bgcolor":
                    color_code, color_time = choose_bgcolor()
                    if color_code and color_time is not None:
                        oggetti.append({"type": "bgcolor", "x": x, "y": y, "color": color_code, "time": color_time})
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_x -= SCROLL_SPEED
            elif event.key == pygame.K_RIGHT:
                scroll_x += SCROLL_SPEED
            elif event.key == pygame.K_UP:
                scroll_y -= SCROLL_SPEED
            elif event.key == pygame.K_DOWN:
                scroll_y += SCROLL_SPEED

    # Disegna i pulsanti di selezione
    pygame.draw.rect(FINESTRA, NERO, block_button_rect)
    FINESTRA.blit(block_image, (10, 10))
    pygame.draw.rect(FINESTRA, NERO, spike_button_rect)
    FINESTRA.blit(spike_image, (70, 10))
    pygame.draw.rect(FINESTRA, NERO, end_button_rect)
    FINESTRA.blit(end_image, (130, 10))
    pygame.draw.rect(FINESTRA, NERO, wave_button_rect)
    FINESTRA.blit(wave_button_image, (190, 10))  # Usa l'immagine ridimensionata per il pulsante
    pygame.draw.rect(FINESTRA, NERO, bgcolor_button_rect)
    FINESTRA.blit(bgcolor_image, (250, 10))
    pygame.draw.rect(FINESTRA, ROSSO, close_button_rect)
    pygame.draw.line(FINESTRA, BIANCO, (close_button_rect.left + 10, close_button_rect.top + 10),
                     (close_button_rect.right - 10, close_button_rect.bottom - 10), 5)
    pygame.draw.line(FINESTRA, BIANCO, (close_button_rect.left + 10, close_button_rect.bottom - 10),
                     (close_button_rect.right - 10, close_button_rect.top + 10), 5)
    pygame.draw.rect(FINESTRA, VERDE, open_button_rect)
    pygame.draw.line(FINESTRA, BIANCO, (open_button_rect.centerx, open_button_rect.top + 10),
                     (open_button_rect.centerx, open_button_rect.bottom - 10), 5)
    pygame.draw.line(FINESTRA, BIANCO, (open_button_rect.left + 10, open_button_rect.centery),
                     (open_button_rect.right - 10, open_button_rect.centery), 5)
    pygame.draw.rect(FINESTRA, ARANCIONE, music_button_rect)
    pygame.draw.line(FINESTRA, BIANCO, (music_button_rect.centerx - 10, music_button_rect.centery - 10),
                     (music_button_rect.centerx - 10, music_button_rect.centery + 10), 5)
    pygame.draw.line(FINESTRA, BIANCO, (music_button_rect.centerx + 10, music_button_rect.centery - 10),
                     (music_button_rect.centerx + 10, music_button_rect.centery + 10), 5)
    pygame.draw.line(FINESTRA, BIANCO, (music_button_rect.centerx - 10, music_button_rect.centery),
                     (music_button_rect.centerx + 10, music_button_rect.centery), 5)
    pygame.draw.rect(FINESTRA, BLU, delete_button_rect)
    if current_object == "delete":
        pygame.draw.rect(FINESTRA, CELESTE, delete_button_rect)
    pygame.draw.line(FINESTRA, BIANCO, (delete_button_rect.left + 10, delete_button_rect.centery),
                     (delete_button_rect.right - 10, delete_button_rect.centery), 5)

    # Disegna gli oggetti
    for obj in oggetti:
        if obj["type"] == "block":
            FINESTRA.blit(block_image, (obj["x"] - scroll_x, obj["y"] - scroll_y))
        elif obj["type"] == "spike":
            FINESTRA.blit(spike_image, (obj["x"] - scroll_x, obj["y"] - scroll_y))
        elif obj["type"] == "end":
            FINESTRA.blit(end_image, (obj["x"] - scroll_x, obj["y"] - scroll_y))
        elif obj["type"] == "wave":
            FINESTRA.blit(wave_image, (obj["x"] - scroll_x, obj["y"] - scroll_y))
        elif obj["type"] == "bgcolor":
            pygame.draw.rect(FINESTRA, pygame.Color(obj["color"]), (obj["x"] - scroll_x, obj["y"] - scroll_y, BLOCK_SIZE, BLOCK_SIZE))

    pygame.display.flip()

pygame.quit()
