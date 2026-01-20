from ursina import *
from ursina.prefabs.first_person_controller import First_Person_Controller

app = Ursina()

# --- OPTIMISATION GRAPHIQUE ---
window.fps_counter.enabled = True
window.entity_counter.enabled = False
window.color = color.black

# --- LE MONDE ---
# Création d'un terrain avec du relief (plus "fort" qu'un sol plat)
ground = Entity(model='plane', collider='box', scale=100, texture='grass', texture_scale=(20,20))

# Ajout d'une lumière directionnelle (le Soleil) pour les ombres
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))

# --- LE JOUEUR (LINK 3.0) ---
class Link(Entity):
    def __init__(self):
        super().__init__(
            model='cube', # Remplace par 'link_model.obj' plus tard
            color=color.green,
            scale=(1, 2, 1),
            position=(0, 1, 0),
            collider='box'
        )
        self.health = 3
        self.stamina = 100
        self.is_sprinting = False

    def update(self):
        # Déplacement 3D
        move_direction = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        ).normalized()
        
        speed = 12 if held_keys['left shift'] and self.stamina > 0 else 6
        self.position += move_direction * speed * time.dt
        
        # Gestion Endurance
        if held_keys['left shift'] and move_direction != Vec3(0,0,0):
            self.stamina -= 50 * time.dt
        elif self.stamina < 100:
            self.stamina += 20 * time.dt

# Initialisation
player = Link()

# Caméra qui suit (3ème personne)
camera.parent = player
camera.position = (0, 10, -20)
camera.rotation_x = 25

# --- INTERFACE (HUD) ---
stamina_bar = Entity(parent=camera.ui, model='quad', color=color.lime, 
                     scale=(0.4, 0.02), position=(-0.5, 0.4))

def update():
    stamina_bar.scale_x = (player.stamina / 100) * 0.4
    stamina_bar.color = color.lime if player.stamina > 20 else color.red

app.run()
