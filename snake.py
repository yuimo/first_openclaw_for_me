import pygame
import time
import random

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
DARK_BLUE = (30, 30, 60)
GRID_COLOR = (40, 40, 70)
YELLOW = (255, 255, 102)
GOLD = (255, 215, 0)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
DARK_GREEN = (50, 200, 50)
BLUE = (80, 150, 255)
PURPLE = (180, 100, 255)

# Display
WIDTH = 800
HEIGHT = 600

dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('贪吃蛇 🐍')

clock = pygame.time.Clock()

# Game settings
SNAKE_BLOCK = 20
SNAKE_SPEED = 12

# Fonts
title_font = pygame.font.SysFont("microsoftyahei", 60, bold=True)
font_style = pygame.font.SysFont("microsoftyahei", 25)
score_font = pygame.font.SysFont("microsoftyahei", 30, bold=True)
small_font = pygame.font.SysFont("microsoftyahei", 18)

# Load sounds (optional - with fallback)
try:
    pygame.mixer.init()
    eat_sound = pygame.mixer.Sound
    # Create simple beep sounds programmatically
    class SimpleSound:
        def play(self): pass
    eat_sound = SimpleSound()
    game_over_sound = SimpleSound()
except:
    pass

def draw_grid():
    for x in range(0, WIDTH, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SNAKE_BLOCK):
        pygame.draw.line(dis, GRID_COLOR, (0, y), (WIDTH, y))

def draw_food(x, y, pulse=0):
    # Pulsing food effect
    size = SNAKE_BLOCK + pulse
    offset = (SNAKE_BLOCK - size) // 2
    
    # Outer glow
    pygame.draw.rect(dis, RED, [x + offset - 2, y + offset - 2, size + 4, size + 4], border_radius=5)
    # Main food
    pygame.draw.rect(dis, (255, 100, 100), [x + offset, y + offset, size, size], border_radius=4)
    # Inner highlight
    pygame.draw.rect(dis, (255, 150, 150), [x + offset + 3, y + offset + 3, size//2, size//2], border_radius=2)

def draw_snake(snake_list):
    for i, segment in enumerate(snake_list):
        # Gradient color based on position
        ratio = i / max(len(snake_list), 1)
        color = (
            int(GREEN[0] * (1 - ratio * 0.3)),
            int(GREEN[1] * (0.9 + ratio * 0.1)),
            int(GREEN[2] * (1 - ratio * 0.3))
        )
        
        # Draw segment shadow
        pygame.draw.rect(dis, (0, 0, 0), [segment[0] + 2, segment[1] + 2, SNAKE_BLOCK, SNAKE_BLOCK], border_radius=4)
        # Draw segment
        pygame.draw.rect(dis, color, [segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK], border_radius=4)
        
        # Draw eyes on head
        if i == len(snake_list) - 1:
            eye_size = 4
            # Determine direction for eye position
            if i > 0:
                prev = snake_list[i - 1]
                if prev[0] > segment[0]:  # Moving right
                    eye_positions = [(segment[0] + 12, segment[0] + 6), (segment[0] + 12, segment[0] + 14)]
                elif prev[0] < segment[0]:  # Moving left
                    eye_positions = [(segment[0] + 4, segment[0] + 6), (segment[0] + 4, segment[0] + 14)]
                elif prev[1] > segment[1]:  # Moving down
                    eye_positions = [(segment[0] + 6, segment[0] + 12), (segment[0] + 14, segment[0] + 12)]
                else:  # Moving up
                    eye_positions = [(segment[0] + 6, segment[0] + 4), (segment[0] + 14, segment[0] + 4)]
            else:
                eye_positions = [(segment[0] + 5, segment[0] + 5), (segment[0] + 11, segment[0] + 5)]
            
            for ex, ey in eye_positions:
                pygame.draw.circle(dis, BLACK, (segment[0] + ex, segment[1] + ey), eye_size)
                pygame.draw.circle(dis, WHITE, (segment[0] + ex - 1, segment[1] + ey - 1), 1)

def Your_score(score):
    # Score background
    score_bg = pygame.Rect(10, 10, 150, 40)
    pygame.draw.rect(dis, (0, 0, 0, 150), score_bg, border_radius=10)
    pygame.draw.rect(dis, GOLD, score_bg, 2, border_radius=10)
    
    value = score_font.render(f"得分: {score}", True, GOLD)
    dis.blit(value, [20, 18])

def draw_button(text, x, y, w, h, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    is_hovered = x < mouse[0] < x + w and y < mouse[1] < y + h
    
    btn_color = hover_color if is_hovered else color
    pygame.draw.rect(dis, btn_color, [x, y, w, h], border_radius=15)
    pygame.draw.rect(dis, WHITE, [x, y, w, h], 3, border_radius=15)
    
    text_surf = font_style.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    dis.blit(text_surf, text_rect)
    
    if is_hovered and click[0] == 1:
        return True
    return False

def start_screen():
    waiting = True
    while waiting:
        dis.fill(DARK_BLUE)
        
        # Draw decorative grid
        draw_grid()
        
        # Title
        title = title_font.render("贪吃蛇", True, GREEN)
        title_shadow = title_font.render("贪吃蛇", True, (0, 100, 0))
        dis.blit(title_shadow, [WIDTH//2 - title.get_width()//2 + 3, 150 + 3])
        dis.blit(title, [WIDTH//2 - title.get_width()//2, 150])
        
        # Snake emoji art
        snake_art = small_font.render("🐍" * 10, True, GREEN)
        dis.blit(snake_art, [WIDTH//2 - snake_art.get_width()//2, 230])
        
        # Instructions
        instr = [
            "🎮 使用方向键控制移动",
            "🍎 吃到红色食物变长",
            "⚠️ 不要撞到墙壁或自己"
        ]
        for i, line in enumerate(instr):
            text = small_font.render(line, True, WHITE)
            dis.blit(text, [WIDTH//2 - text.get_width()//2, 320 + i * 30])
        
        # Start button
        if draw_button("开始游戏", WIDTH//2 - 100, 420, 200, 50, GREEN, DARK_GREEN):
            waiting = False
        
        # Quit button
        if draw_button("退出", WIDTH//2 - 100, 490, 200, 50, RED, (200, 50, 50)):
            pygame.quit()
            quit()
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def game_over_screen(score):
    waiting = True
    while waiting:
        dis.fill(DARK_BLUE)
        
        # Game over text
        go_text = title_font.render("游戏结束!", True, RED)
        dis.blit(go_text, [WIDTH//2 - go_text.get_width()//2, 180])
        
        # Score
        score_text = score_font.render(f"最终得分: {score}", True, GOLD)
        dis.blit(score_text, [WIDTH//2 - score_text.get_width()//2, 280])
        
        # High score (stored in file)
        try:
            with open("highscore.txt", "r") as f:
                high_score = int(f.read())
        except:
            high_score = 0
        
        if score > high_score:
            high_score = score
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))
            hs_text = score_font.render("🎉 新纪录!", True, GREEN)
            dis.blit(hs_text, [WIDTH//2 - hs_text.get_width()//2, 330])
        else:
            hs_text = score_font.render(f"最高分: {high_score}", True, WHITE)
            dis.blit(hs_text, [WIDTH//2 - hs_text.get_width()//2, 330])
        
        # Buttons
        if draw_button("再玩一次", WIDTH//2 - 100, 400, 200, 50, GREEN, DARK_GREEN):
            gameLoop()
        
        if draw_button("退出", WIDTH//2 - 100, 470, 200, 50, RED, (200, 50, 50)):
            pygame.quit()
            quit()
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def gameLoop():
    start_screen()
    
    game_over = False
    game_close = False

    x1 = WIDTH // 2
    y1 = HEIGHT // 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(50, WIDTH - 50 - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
    foody = round(random.randrange(50, HEIGHT - 50 - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
    
    food_pulse = 0
    pulse_direction = 1
    
    last_move_time = time.time()
    move_delay = 1 / SNAKE_SPEED

    while not game_over:

        while game_close == True:
            game_over_screen(Length_of_snake - 1)
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = SNAKE_BLOCK
                    x1_change = 0
                elif event.key == pygame.K_ESCAPE:
                    game_over = True

        current_time = time.time()
        if current_time - last_move_time >= move_delay:
            last_move_time = current_time
            
            if x1 >= WIDTH - 10 or x1 < 10 or y1 >= HEIGHT - 10 or y1 < 10:
                game_close = True
            x1 += x1_change
            y1 += y1_change
            
            if x1 >= WIDTH - 10 or x1 < 10 or y1 >= HEIGHT - 10 or y1 < 10:
                game_close = True

            # Check self-collision
            for segment in snake_List[:-1]:
                if segment[0] == x1 and segment[1] == y1:
                    game_close = True
                    break

        # Draw background
        dis.fill(DARK_BLUE)
        draw_grid()
        
        # Food animation
        food_pulse += 0.3 * pulse_direction
        if food_pulse > 5 or food_pulse < 0:
            pulse_direction *= -1
        
        # Draw food
        draw_food(foodx, foody, int(food_pulse))
        
        # Snake
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        draw_snake(snake_List)
        Your_score(Length_of_snake - 1)

        pygame.display.update()

        # Eat food
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(50, WIDTH - 50 - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
            foody = round(random.randrange(50, HEIGHT - 50 - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
            Length_of_snake += 1
            try:
                eat_sound.play()
            except:
                pass

        clock.tick(60)

    pygame.quit()
    quit()

if __name__ == "__main__":
    gameLoop()
