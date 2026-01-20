from ursina import *
from ursina.prefabs.first_person_controller import First_Person_Controller

# 1. INITIALISATION DU MOTEUR
app = Ursina()

# Paramètres de la fenêtre
window.title = "Zelda Rim'K 3D"
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# 2. LE MONDE (PLATEAU DU PRÉLUDE)
ground = Entity(model='plane', collider='box', scale=100, texture='grass', texture_scale=(20,20))
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))

# 3. CLASSE DE L'ENNEMI (BOKOBLIN)
class Ennemi(Entity):
    def __init__(self, position=(10, 0.5, 10)):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(1.5, 1.5, 1.5),
            position=position,
            collider='box'
        )
        self.hp = 3

    def update(self):
        # IA simple : Suit le joueur s'il est proche
        dist = distance(self.position, player.position)
        if 2 < dist < 20:
            self.look_at(player.position)
            self.position += self.forward * 3 * time.dt

    def take_damage(self):
        self.hp -= 1
        self.color = color.white # Flash de dégâts
        invoke(setattr, self, 'color', color.red, delay=0.1)
        self.position -= self.forward * 1.5 # Recul (Knockback)
        print(f"Bokoblin HP: {self.hp}")
        
        if self.hp <= 0:
            destroy(self)
            print("Ennemi vaincu !")

# 4. CLASSE DE L'ÉPÉE
class Epee(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            parent=camera, # Attachée à la vue
            scale=(0.2, 1.5, 0.2),
            position=(0.6, -0.6, 1),
            rotation=(30, -10, 0),
            color=color.light_gray
        )

    def attaquer(self):
        # Animation d'attaque
        self.animate_rotation((90, 0, 0), duration=0.1)
        invoke(self.animate_rotation, (30, -10, 0), duration=0.1, delay=0.2)
        
        # Détection de collision (Raycast)
        hit_info = raycast(camera.world_position, camera.forward, distance=4, ignore=[player,])
        if hit_info.hit and isinstance(hit_info.entity, Ennemi):
            hit_info.entity.take_damage()

# 5. LE JOUEUR ET L'INTERFACE
player = First_Person_Controller()
player.cursor.visible = False
player.speed = 8
player.epee = Epee()

# HUD : Barre d'endurance
stamina_bar = Entity(parent=camera.ui, model='quad', color=color.lime, 
                     scale=(0.4, 0.02), position=(-0.5, 0.4))
stamina = 100

# 6. LOGIQUE GLOBALE (UPDATE & INPUT)
def update():
    global stamina
    
    # Gestion du Sprint
    if held_keys['left shift'] and stamina > 0 and (held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']):
        player.speed = 16
        stamina -= 50 * time.dt
    else:
        player.speed = 8
        if stamina < 100:
            stamina += 25 * time.dt
            
    # Mise à jour visuelle HUD
    stamina_bar.scale_x = (stamina / 100) * 0.4
    stamina_bar.color = color.lime if stamina > 25 else color.red

def input(key):
    # Attaque (Clic gauche ou Espace)
    if key == 'left mouse button' or key == 'space':
        player.epee.attaquer()

# 7. LANCEMENT
# On crée un ennemi de test au début
bokoblin = Ennemi(position=(5, 0.5, 12))

app.run()
