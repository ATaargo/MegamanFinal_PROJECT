import pygame
import os
import random
import pygame.mixer

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load background image
background_image = pygame.transform.scale(pygame.image.load("assets/BG.png"), screen.get_size())

# Constants
STANDING_IMAGES_COUNT = 2
JUMPING_IMAGES_COUNT = 2
RUNNING_IMAGES_COUNT = 4
SHOOTING_IMAGES_COUNT = 2
IDLE_IMAGES_COUNT = 2
BUSTER_IMAGES_COUNT = 2
laser_sound = pygame.mixer.Sound('assets/laser_sound.wav')


# Function to load player images
def load_images(prefix, count):
    images = []
    for i in range(1, count + 1):
        image_path = f'assets/{prefix}_{i}.png'
        if not os.path.exists(image_path):
            # If the image with the number doesn't exist, try without the number
            image_path = f'assets/{prefix}.png'
        images.append(pygame.image.load(image_path).convert_alpha())
    return images


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, max_health):
        super().__init__()

        # Load player images
        self.standing_images = load_images('player_standing', STANDING_IMAGES_COUNT)
        self.jumping_images = load_images('player_jumping', JUMPING_IMAGES_COUNT)
        self.running_images = load_images('player_walking', RUNNING_IMAGES_COUNT)
        self.shooting_images = load_images('player_shooting', SHOOTING_IMAGES_COUNT)
        self.hurt_image = pygame.image.load('assets/player_hurt.png').convert_alpha()

        # Set the initial image and rect
        self.image = self.standing_images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = 0
        self.speed_y = 0
        self.facing_right = True
        self.is_shooting = False
        self.invincible = False
        self.invincibility_duration = 3
        self.invincibility_timer = 0
        # Health attributes
        self.max_health = max_health
        self.health = self.max_health

        # Set up hitbox
        self.hitbox = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        # Animation variables
        self.current_standing_frame = 0
        self.standing_animation_speed = 0.02
        self.current_jumping_frame = 0
        self.jumping_animation_speeds = [0.5, 0.01]
        self.current_running_frame = 0
        self.running_animation_speed = 0.08
        self.current_shooting_frame = 0
        self.shooting_animation_speed = 0.1

        self.start_time = None  # Variable to store the start time when the boss fight begins
        self.bullets_landed = 0  # Track how many bullets the player lands on the boss

    def update(self):
        # Update player position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Apply gravity
        self.speed_y += 0.5

        # Keep the player within the screen boundaries
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

        # Update animation based on movement or shooting
        if self.is_shooting:
            self.update_shooting_animation()
        elif self.speed_y < 0:
            self.update_jumping_animation()
        elif self.speed_x != 0:
            self.update_running_animation()
        else:
            self.update_standing_animation()

        # Check for invincibility
        if self.invincible:
            self.invincibility_timer += 1
            if self.invincibility_timer >= self.invincibility_duration * FPS:
                self.invincible = False
                self.invincibility_timer = 0

        # Update hitbox position
        self.hitbox.topleft = (self.rect.x, self.rect.y)

    def update_hurt_animation(self):
        if not self.invincible:
            # Decrease player health
            if boss_enemy.current_behavior == "sword_charge":
                self.health -= 5
            else:
                self.health -= 2

            # Check if player is still alive
            if self.health <= 0:
                self.kill()  # Remove player from sprite groups

            # Flash white for a few frames
            flash_duration = 0.5  # Adjust the flash duration as needed
            flash_frequency = 10  # Adjust the flash frequency as needed

            flash_timer = 0

            while flash_timer < flash_duration * FPS:
                if flash_timer % flash_frequency == 0:
                    self.image = pygame.transform.flip(self.hurt_image, not self.facing_right, False)
                    pygame.display.flip()  # Update the display
                    pygame.time.delay(50)

                flash_timer += 1

            self.invincible = True
            self.speed_x = 0
            self.speed_y = 0

            # Increase the duration of invincibility by setting the invincibility timer to a higher value
            self.invincibility_timer = 0

    def update_standing_animation(self):
        self.current_standing_frame += self.standing_animation_speed
        if self.current_standing_frame >= len(self.standing_images):
            self.current_standing_frame = 0
        self.image = pygame.transform.flip(self.standing_images[int(self.current_standing_frame)],
                                           not self.facing_right, False)

    def update_jumping_animation(self):
        self.current_jumping_frame += self.jumping_animation_speeds[int(self.current_jumping_frame)]
        if self.current_jumping_frame >= len(self.jumping_images):
            self.current_jumping_frame = 0
        self.image = pygame.transform.flip(self.jumping_images[int(self.current_jumping_frame)],
                                           not self.facing_right, False)

    def update_running_animation(self):
        self.current_running_frame += self.running_animation_speed
        if self.current_running_frame >= len(self.running_images):
            self.current_running_frame = 0
        self.image = pygame.transform.flip(self.running_images[int(self.current_running_frame)],
                                           not self.facing_right, False)

    def update_shooting_animation(self):
        self.current_shooting_frame += self.shooting_animation_speed
        if self.current_shooting_frame >= len(self.shooting_images):
            self.current_shooting_frame = 0
        self.image = pygame.transform.flip(self.shooting_images[int(self.current_shooting_frame)],
                                           not self.facing_right, False)

        if self.current_shooting_frame == 0:
            self.is_shooting = False
        # Plays the sound effect
        laser_sound.play()

    def update_bullets(self):
        for bullet in bullet_group:
            bullet.update()
            if bullet.hitbox.colliderect(boss_enemy.hitbox):
                boss_enemy.reduce_health(5)
                self.bullets_landed += 1

    def get_centerx(self):
        return self.rect.centerx


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        super().__init__()

        # Load bullet image
        self.image = pygame.image.load('assets/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = 7 * direction
        self.shooter = shooter  # Store a reference to the object that fired the bullet

        # Adjust bullet position based on direction
        if direction == 1:
            self.rect.topleft = (x + self.shooter.rect.width, y)
        else:
            self.rect.topright = (x, y)

        # Set up hitbox
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def update(self):
        self.rect.x += self.speed
        self.hitbox.topleft = (self.rect.x, self.rect.y)

        # Check for collisions based on the shooter
        if self.shooter == player and self.rect.colliderect(boss_enemy.hitbox):
            boss_enemy.reduce_health(5)  # Adjust the damage value as needed
            self.kill()

        elif self.shooter == boss_enemy and self.rect.colliderect(player.hitbox):
            player.update_hurt_animation()
            self.kill()

        # Remove the bullet when it goes off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

    def draw_hitbox(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


# BossEnemy class
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, max_health):
        super().__init__()

        # Load boss enemy sprites
        self.idle_image = pygame.image.load('assets/boss_enemy_idle.png').convert_alpha()
        self.floating_image = pygame.image.load('assets/boss_enemy_floating.png').convert_alpha()
        self.buster_image = pygame.image.load('assets/boss_enemy_buster.png').convert_alpha()
        self.sword_charge_image = pygame.image.load('assets/boss_enemy_sword_charge.png').convert_alpha()
        self.alt_buster_image = pygame.image.load('assets/Alt_boss_enemy3.png').convert_alpha()
        self.alt_sword_charge_image = pygame.image.load('assets/Alt_boss_enemy4.png').convert_alpha()

        # Set the initial image and rect
        self.image = self.idle_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = 2
        self.speed_y = 0
        self.current_behavior = "idle"
        self.can_change_direction = True
        self.charge_speed = 4  # Adjust the charge speed as needed
        self.sword_charge_cooldown = 4 * FPS  # Cooldown duration for sword_charge behavior
        self.sword_charge_timer = 0
        self.charge_timer = 0
        self.charge_duration = 0.5 * FPS  # Adjust the charge duration as needed
        # Health attributes
        self.max_health = max_health
        self.health = self.max_health
        # New attributes for behavior control
        self.behavior_duration = 0  # Duration of the current behavior
        self.behavior_timer = 0  # Timer to track how long the current behavior has been active
        self.current_behavior = None  # Current behavior state
        self.next_behavior = None  # Next behavior state
        self.current_behavior_frame = 0
        self.bullet_counter = 0
        self.max_bullets = 3
        self.bullet_cooldown = int(FPS * 0.5)
        self.bullet_timer = 0
        self.facing_right = True

        # Initialize the boss with an initial behavior
        self.choose_next_behavior()

        # Set up hitbox
        self.hitbox = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Adjust boss's image to smoothly face the player character
        player_center = player.rect.centerx
        boss_center = self.rect.centerx

        # Reverse direction only if not near the screen boundaries
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speed_x *= -1
            self.can_change_direction = True

        # Adjust facing direction based on player's position
        self.adjust_facing_direction(player_center)

        # Adjust facing direction based on player's position
        if player_center < boss_center:
            self.facing_right = True
        else:
            self.facing_left = False

        # Correct the facing direction based on the current behavior
        if self.current_behavior == "buster":
            if self.facing_right:
                self.image = pygame.transform.flip(self.buster_image, not self.facing_right, False)
            else:
                self.image = pygame.transform.flip(self.buster_image, True, False)
        elif self.current_behavior == "sword_charge":
            if self.facing_right:
                self.image = pygame.transform.flip(self.sword_charge_image, not self.facing_right, False)
            else:
                self.image = pygame.transform.flip(self.sword_charge_image, True, False)

        # Update boss behavior based on some condition
        if pygame.time.get_ticks() % (60 * FPS) == 0:
            self.switch_boss_behavior()

        if self.bullet_timer > 0:
            self.bullet_timer -= 1

        # Update hitbox position
        self.hitbox.topleft = (self.rect.x, self.rect.y)

        if self.current_behavior == "sword_charge":
            self.update_sword_charge_behavior()
        elif self.current_behavior == "buster":
            self.update_buster_behavior()

        # Update boss behavior based on the state machine
        self.behavior_timer += 1

        if self.behavior_timer >= self.behavior_duration:
            # If the current behavior duration is reached, switch to the next behavior
            self.current_behavior = self.next_behavior
            self.behavior_timer = 0
            self.choose_next_behavior()

            self.execute_current_behavior()

    def check_bullet_collisions(self):
        # Check for collisions with bullets
        for bullet in bullet_group:
            if bullet.hitbox.colliderect(self.hitbox):
                bullet.kill()
                print("Boss hitbox:", self.hitbox.topleft)
                self.health -= 5

    def reduce_health(self, amount):
        self.health -= amount
        print(f"Boss health reduced to {self.health}")

        # Check if the boss is still alive
        if self.health <= 0:
            self.kill()  # Remove boss from sprite groups
            print("Boss VANQUISHED!")

    def switch_boss_behavior(self):
        behaviors = ["idle", "floating", "buster", "sword_charge"]
        current_index = behaviors.index(self.current_behavior)

        if self.current_behavior == "floating":
            self.switch_floating_behavior(behaviors)
        elif self.current_behavior == "buster":
            self.switch_buster_behavior(behaviors)
        elif self.current_behavior == "sword_charge":
            self.switch_sword_charge_behavior(behaviors)
        else:
            # Otherwise, switch to the next behavior in the list
            current_index = (current_index + 1) % len(behaviors)

        self.current_behavior = behaviors[current_index]

    def switch_idle_behavior(self, behaviors):
        # Logic for idle behavior
        if pygame.time.get_ticks() % (3 * FPS) == 0:
            self.current_behavior_frame = 0  # Reset the animation frame for idle
            self.is_firing_bullets = True
            self.load_boss_images(self.rect.x, self.rect.y)  # Reload boss images to update the behavior frames
            self.fire_bullets()

    def switch_floating_behavior(self, behaviors):
        # If boss is floating, alternate between idle and floating every second
        if pygame.time.get_ticks() % (60 * FPS) == 0:
            current_index = (behaviors.index(self.current_behavior) + 1) % 2  # Switch between idle and floating
            self.current_behavior = behaviors[current_index]

            # Check if the boss is within the screen boundaries after switching
            self.check_screen_boundaries()

    def switch_buster_behavior(self, behaviors):
        # If boss is in the buster state, periodically match player's y-coordinate and fire three bullets
        if pygame.time.get_ticks() % (120 * FPS) == 0:
            self.rect.y = player.rect.y
            self.current_behavior_frame = 0  # Reset the animation frame for buster
            self.is_firing_bullets = True
            self.load_boss_images(self.rect.x, self.rect.y)  # Reload boss images to update the behavior frames
            self.fire_bullets()

            # Check if the boss is within the screen boundaries after firing bullets
            self.check_screen_boundaries()

    def switch_sword_charge_behavior(self, behaviors):
        # If boss is in the sword_charge state, check if the charge duration is reached
        self.sword_charge_timer += 1
        if self.sword_charge_timer >= self.sword_charge_cooldown:
            self.sword_charge_timer = 0
            current_index = (behaviors.index(self.current_behavior) + 1) % len(behaviors)  # Switch to the next behavior
            self.current_behavior = behaviors[current_index]

            # Check if the boss is within the screen boundaries after switching
            self.check_screen_boundaries()

    def check_screen_boundaries(self):
        # Keep the boss within the screen boundaries
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def update_sword_charge_behavior(self):
        # If boss is in the sword_charge state, charge towards the player
        if self.sword_charge_timer <= self.sword_charge_cooldown:
            if player.rect.colliderect(self.hitbox):
                player.update_hurt_animation()
                self.sword_charge_timer = self.sword_charge_cooldown
            else:
                if player.rect.centerx > self.rect.centerx:
                    self.rect.x += self.charge_speed
                else:
                    self.rect.x -= self.charge_speed
        else:
            # After the charge duration, switch to idle
            self.current_behavior = "idle"

    def update_buster_behavior(self):
        # Logic for buster behavior
        if self.behavior_timer % (120 * FPS) == 0:
            self.rect.y = player.rect.y
            self.current_behavior_frame = 0  # Reset the animation frame for buster
            self.is_firing_bullets = True
            self.fire_bullets()

            # Check if the boss is within the screen boundaries after firing bullets
            self.check_screen_boundaries()

    def update_idle_behavior(self):
        # Logic for idle behavior
        if self.behavior_timer % (3 * FPS) == 0:
            self.current_behavior_frame = 0  # Reset the animation frame for idle
            self.is_firing_bullets = True
            self.fire_bullets()

            # Check if the boss is within the screen boundaries after firing bullets
            self.check_screen_boundaries()

    def update_behavior_animation(self, player_centerx):
        # Update animation based on the current behavior
        if self.current_behavior == "buster":
            self.update_buster_animation()
        elif self.current_behavior == "idle":
            self.update_buster_animation()
        elif self.current_behavior == "sword_charge":
            self.image = self.sword_charge_image
        elif self.current_behavior == "floating":
            self.adjust_facing_direction(player_centerx)

    def adjust_facing_direction(self, player_centerx):
        boss_center = self.rect.centerx

        # Adjust facing direction based on player's position
        self.facing_right = player_centerx < boss_center

        if self.current_behavior == "buster":
            if self.facing_right:
                self.image = pygame.transform.flip(self.buster_image, not self.facing_right, False)
            else:
                self.image = pygame.transform.flip(self.alt_buster_image, True, False)
        elif self.current_behavior == "sword_charge":
            if self.facing_right:
                self.image = pygame.transform.flip(self.sword_charge_image, not self.facing_right, False)
            else:
                self.image = pygame.transform.flip(self.alt_sword_charge_image, True, False)

    def update_buster_animation(self):
        # Update buster animation
        self.current_behavior_frame += 1
        if self.current_behavior_frame >= len(self.buster_images):
            self.current_behavior_frame = 0
            self.is_firing_bullets = False  # Stop firing bullets at the end of the animation

        self.image = self.buster_images[self.current_behavior_frame]
        self.check_screen_boundaries()

    def update_idle_animation(self):
        # Update idle animation
        self.current_behavior_frame += 1
        if self.current_behavior_frame >= len(self.idle_images):
            self.current_behavior_frame = 0
            self.is_firing_bullets = False  # Stop firing bullets at the end of the animation

        self.image = self.idle_images[self.current_behavior_frame]
        self.check_screen_boundaries()

    def load_boss_images(self, x, y):
        # Load boss enemy sprites
        self.idle_images = load_images('boss_enemy_idle', IDLE_IMAGES_COUNT)
        self.floating_image = pygame.image.load('assets/boss_enemy_floating.png').convert_alpha()
        self.buster_images = load_images('boss_enemy_buster', BUSTER_IMAGES_COUNT)
        self.sword_charge_image = pygame.image.load('assets/boss_enemy_sword_charge.png').convert_alpha()

        # Set the initial image and rect based on the current behavior
        if self.current_behavior == "idle":
            self.image = self.idle_images[0]
        elif self.current_behavior == "buster":
            if player.rect.x < self.rect.x:
                self.image = self.buster_image
            else:
                self.image = self.alt_buster_image
        elif self.current_behavior == "floating":
            self.image = self.floating_image
        elif self.current_behavior == "sword_charge":
            if player.rect.x < self.rect.x:
                self.image = self.sword_charge_image
            else:
                self.image = self.alt_sword_charge_image

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))

    def execute_current_behavior(self):
        if self.current_behavior == "idle":
            self.execute_idle_behavior()
        elif self.current_behavior == "floating":
            self.execute_floating_behavior()
        elif self.current_behavior == "buster":
            self.execute_buster_behavior()
        elif self.current_behavior == "sword_charge":
            self.execute_sword_charge_behavior()

    def execute_idle_behavior(self):
        # Stop moving
        self.speed_x = 0
        self.speed_y = 0

        # Logic for shooting bullets slowly
        if self.behavior_timer % (3 * FPS) == 0:
            self.fire_bullets()

            # Check if the boss is within the screen boundaries after firing bullets
            self.check_screen_boundaries()

    def execute_floating_behavior(self):
        # Move slower
        self.speed_x = 1

        # Reverse direction if hitting the screen edge
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1

    def create_bullet(self):
        # Calculate the direction based on the player's position
        direction = 1 if player.rect.x > self.rect.x else -1
        bullet = Bullet(self.rect.x, self.rect.y, direction, self)  # Boss always faces right
        all_sprites.add(bullet)
        bullet_group.add(bullet)

        laser_sound.play()

    def update_bullets(self):
        for bullet in bullet_group:
            bullet.update()

    def execute_buster_behavior(self):
        # Logic for buster behavior
        if self.behavior_timer % (120 * FPS) == 0:
            self.rect.y = player.rect.y
            self.create_bullet()  # Use the new method to create bullets

            # Check if the boss is within the screen boundaries after firing bullets
            self.check_screen_boundaries()

        self.adjust_facing_direction(player.rect.centerx)
        self.update_buster_animation()

    def execute_sword_charge_behavior(self):
        # Logic for sword_charge behavior
        if self.sword_charge_timer <= self.sword_charge_cooldown:
            if player.rect.centerx > self.rect.centerx:
                self.rect.x += self.charge_speed
            else:
                self.rect.x -= self.charge_speed
        else:
            # After the charge duration, switch to idle
            self.current_behavior = "idle"

        self.adjust_facing_direction(player.rect.centerx)
        self.image = self.sword_charge_image

    def fire_bullets(self):
        global boss_bullets_missed

        if self.bullet_counter < self.max_bullets and self.bullet_timer == 0:
            for _ in range(3):
                direction = 1 if self.rect.x < player.rect.x else -1
                bullet = Bullet(self.rect.x, self.rect.y, direction, self)
                all_sprites.add(bullet)
                bullet_group.add(bullet)

                # Increment the boss bullets missed counter when the player avoids the bullets
                if not bullet.hitbox.colliderect(player.hitbox):
                    boss_bullets_missed += 1

            self.bullet_counter += 1
            self.bullet_timer = self.bullet_cooldown

    def reset_bullet_counter(self):
        self.bullet_counter = 0

    def choose_next_behavior(self):
        # Randomly choose the next behavior from available behaviors
        behaviors = ["idle", "floating", "buster", "sword_charge"]
        if self.current_behavior in behaviors:
            behaviors.remove(self.current_behavior)  # Remove the current behavior from options

        self.reset_bullet_counter()
        self.next_behavior = random.choice(behaviors)
        self.behavior_duration = 2 * FPS


# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()

        # Create a surface for the platform
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 165, 0))  # Orange color
        self.rect = self.image.get_rect(topleft=(x, y))


# Create Sprite groups
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

# Create game objects
player = Player(100, 300, max_health=50)
boss_enemy = BossEnemy(x=400, y=375, max_health=150)
boss_enemy.load_boss_images(400, 375)

# Add platforms to the left side
platform_left1 = Platform(160, 400, SCREEN_WIDTH // 5, 20)
platform_left2 = Platform(50, 300, SCREEN_WIDTH // 5, 20)

# Add platforms to the right side
platform_right1 = Platform(SCREEN_WIDTH - 50 - SCREEN_WIDTH // 5, 350, SCREEN_WIDTH // 5, 20)
platform_right2 = Platform(SCREEN_WIDTH - 170 - SCREEN_WIDTH // 5, 250, SCREEN_WIDTH // 5, 20)

# Add all objects to groups
all_sprites.add(player, boss_enemy, platform_left1, platform_left2, platform_right1, platform_right2)
player_group.add(player)
boss_group.add(boss_enemy)
platform_group.add(platform_left1, platform_left2, platform_right1, platform_right2)

# Define game states
GAME_IN_PROGRESS = 0
PLAYER_DEFEATED = 1
BOSS_DEFEATED = 2

score = 0
time_to_defeat_boss = 0  # Track how fast the player defeats the boss
bullets_landed = 0  # Track how many bullets the player lands on the boss
boss_bullets_missed = 0  # Track how many bullets from the boss the player avoids

# Initialize game state
game_state = GAME_IN_PROGRESS

# Set the desired frame rate
clock = pygame.time.Clock()

score_calculated = False


# Game loop
def main():
    global game_state
    global score_calculated
    global score
    global time_to_defeat_boss
    global bullets_landed
    global boss_bullets_missed

    running = True

    # Check if the boss fight begins and set the start time
    if boss_enemy.health > 0 and player.start_time is None:
        player.start_time = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Check game state
        if game_state == GAME_IN_PROGRESS:
            # Move player
            player.speed_x = 0
            if keys[pygame.K_a]:
                player.speed_x = -5
                player.facing_right = False
            elif keys[pygame.K_d]:
                player.speed_x = 5
                player.facing_right = True

            # Check for collisions with platforms
            platform_collision = pygame.sprite.spritecollideany(player, platform_group)

            if platform_collision:
                # Adjust the player's position and velocity when colliding with a platform from the top
                if player.speed_y > 0:
                    player.rect.bottom = platform_collision.rect.top
                    player.speed_y = 0

            # Check if the player is on the ground
            on_ground = platform_collision or player.rect.bottom == SCREEN_HEIGHT

            if on_ground:
                # Reset the vertical speed when on the ground
                player.speed_y = 0

                # Jumping (for simplicity, press 'space' to jump)
                if keys[pygame.K_w]:
                    player.speed_y = -12  # Adjust the jump height as needed

            # Jumping (for simplicity, press 'space' to jump)
            if keys[pygame.K_w] and player.rect.bottom == SCREEN_HEIGHT:
                player.speed_y = -12

            # Shooting (press 'backspace' to shoot)
            if keys[pygame.K_BACKSPACE]:
                if not player.is_shooting:
                    player.is_shooting = True
                    direction = 1 if player.facing_right else -1
                    bullet = Bullet(player.rect.x, player.rect.y, direction, player)
                    all_sprites.add(bullet)
                    bullet_group.add(bullet)

            # Update sprite groups
            all_sprites.update()

            # Update boss's behavior animation
            boss_enemy.update_behavior_animation(player.rect.centerx)
            boss_enemy.execute_current_behavior()
            boss_enemy.update_bullets()

            # Check for collisions between player and boss hitboxes
            if player.hitbox.colliderect(boss_enemy.hitbox) and not player.invincible:
                player.update_hurt_animation()

            # Check for bullet collisions with the boss
            bullet_hits = pygame.sprite.groupcollide(bullet_group, boss_group, True, False)
            for bullet in bullet_group:
                if bullet.hitbox.colliderect(boss_enemy.hitbox):
                    bullet.kill()

            # Fire bullets based on boss behavior
            if boss_enemy.current_behavior == "buster":
                boss_enemy.fire_bullets()

            # Check if the player or boss is defeated
            if player.health <= 0:
                game_state = PLAYER_DEFEATED
            elif boss_enemy.health <= 0:
                game_state = BOSS_DEFEATED

        # Draw the background
        screen.blit(background_image, (0, 0))

        # Draw sprites on the screen
        all_sprites.draw(screen)

        # Display the end screen
        if game_state in [PLAYER_DEFEATED, BOSS_DEFEATED]:
            # Cease all functions
            player.speed_x = 0
            player.speed_y = 0

        # Check if the boss is defeated and calculate the score
        if boss_enemy.health <= 0 and not score_calculated:
            game_state = BOSS_DEFEATED
            end_time = pygame.time.get_ticks()

            # Check if player.start_time is set before calculating the time difference
            if player.start_time is not None:
                time_to_defeat_boss = (end_time - player.start_time) / 1000  # Convert to seconds
                score = int(10000 / time_to_defeat_boss) + (bullets_landed * 10) - (boss_bullets_missed * 5)
                print("Score:", score)

            score_calculated = True

            # Display the score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 18))

        # Display player's health
        font = pygame.font.Font(None, 36)
        health_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Quit the game
    pygame.quit()


if __name__ == "__main__":
    main()
