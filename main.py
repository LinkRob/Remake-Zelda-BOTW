from ursina import *
from ursina.prefabs.first_person_controller import First_Person_Controller

# --- INITIALISATION DU MOTEUR ---
app = Ursina()

# Paramètres de rendu (Style Zelda)
window.title = "ZELDA RIM'K - PROTOTYPE 3D"
window.color = color.black
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# --- DÉCOR ET AMBIANCE ---
Sky(texture='sky_cloudy', color=color.light_gray) # Ajoute un vrai ciel
ground = Entity(model='plane', scale=200, texture='grass', collider='box', texture_scale=(50,50))

# Lumière pour le relief
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))

# --- CLASSES PRINCIPALES ---

class Bokoblin(Entity):
    def __init__(self, x, z):
        super().__init__(
            model='cube', 
            color=color.red, 
            scale=(1.5, 2, 1.5), 
            position=(x, 1, z), 
            collider='box'
        )
        self.hp = 3
        self.health_bar = Entity(parent=self, model='quad', color=color.red, scale=(1, 0.1, 0.1), position=(0, 1.2, 0))

    def update(self):
        # IA de traque : l'ennemi avance vers Link
        dist = distance(self.position, player.position)
        if 2 < dist < 25:
            self.look_at(player.position)
            self.position += self.forward * 3.5 * time.dt
        
        self.health_bar.look_at(camera.world_position) # Barre de vie toujours face caméra

    def take_damage(self):
        self.hp -= 1
        self.health_bar.scale_x = self.hp / 3
        
        # Game Feel : Flash blanc + Recul
        self.color = color.white
        self.animate_position(self.position - self.forward * 2, duration=0.1)
        invoke(setattr, self, 'color', color.red, delay=0.1)
        
        if self.hp <= 0:
            # Effet de mort (particules simples)
            destroy(self)

class Sword(Entity):
    def __init__(self):
        super().__init__(
            model='cube', 
            parent=camera, 
            scale=(0.2, 1.8, 0.2), 
            position=(0.7, -0.8, 1.2), 
            rotation=(35, -15, 0), 
            color=color.light_gray
        )

    def swing(self):
        # Animation d'attaque fluide
        self.animate_rotation((120, 10, 10), duration=0.1, curve=curve.out_expo)
        invoke(self.animate_rotation, (35, -15, 0), duration=0.2, delay=0.15)
        
        # Système de Raycast (Collision épée)
        hit_info = raycast(camera.world_position, camera.forward, distance=4.5, ignore=[player,])
        if hit_info.hit and isinstance(hit_info.entity, Bokoblin):
            hit_info.entity.take_damage()

# --- LE JOUEUR (LINK 3D) ---
player = First_Person_Controller(model='cube', z=-10, color=color.green, origin_y=-0.5, speed=8)
player.cursor.visible = False
player.sword = Sword()

# Interface (HUD)
stamina_container = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(0.42, 0.04), position=(-0.5, 0.4))
stamina_bar = Entity(parent=stamina_container, model='quad', color=color.lime, scale=(0.95, 0.7), position=(0,0))
stamina = 100

# --- LOGIQUE DE JEU ---

def update():
    global stamina
    
    # Sprint & Endurance
    moving = held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']
    if held_keys['left shift'] and stamina > 0 and moving:
        player.speed = 15
        stamina -= 50 * time.dt
    else:
        player.speed = 8
        if stamina < 100: stamina += 25 * time.dt
    
    stamina_bar.scale_x = stamina / 100
    stamina_bar.color = color.lime if stamina > 20 else color.red

def input(key):
    if key == 'left mouse button' or key == 'space':
        player.sword.swing()

# --- GÉNÉRATION DU NIVEAU ---
enemies = [Bokoblin(x=random.randint(-20, 20), z=random.randint(10, 40)) for i in range(5)]

app.run()
