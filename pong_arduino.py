from asyncio.windows_events import NULL
import random
import pygame
import sys
import serial
from threading import Thread
import os
# Bruno Seki Schenberg 32041292
# Gabriel da Silva Morishita Garbi 32048661
# Vitor Cheung 32037902

ttf_path = os.path.join(sys.path[0], "comic_sans.ttf")
# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser = serial.Serial('COM3', 115200, timeout=1)
ax = 0.0
ay = 0.0
ball_speed_x = 3
ball_speed_y = 3
player_score = 0
bot_score = 0
game_state = "menu"
mode = "x"
mode_data = {"x": {"player_width": 90, "player_height": 5, "player_posX": 355, "player_posY": 590, "bot_posX": 355, "bot_posY": 5}, "y": {
    "player_width": 5, "player_height": 90, "player_posX": 790, "player_posY": 255, "bot_posX": 5, "bot_posY": 255}}
calibrated = False
def read_data():
    while True:
        global ay
        global ax
        global calibrated
        ser.write(b".")
        line = ser.readline()
        angles = line.split(b"\t")
        angles.pop(0)
        #print(angles)
        if ay != 0:
            calibrated = True
        if len(angles) == 3:
            ay = float(angles[1])
            ax = float(angles[0])

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Pong Arduino')
    bg_color = pygame.Color(50, 50, 50)
    light_gray = (150, 150, 150)
    font = pygame.font.Font(ttf_path, 30)
    smallfont = pygame.font.Font(ttf_path, 20)
    
    def score(ball):
        global player_score, bot_score
        if ball.left <= 0:
            player_score += 1
        if ball.right >= screen_width:
            bot_score += 1

    def scoreX(ball):
        global player_score, bot_score
        if ball.top <= 0:
            player_score += 1
        if ball.bottom >= screen_height:
            bot_score += 1

    def ballmovementX(ball,player,bot):
        global ball_speed_x, ball_speed_y

        if ball.colliderect(player) or ball.colliderect(bot):
            ball_speed_y *= -1

        ball.x += ball_speed_x
        ball.y += ball_speed_y

        if ball.left <= 0 or ball.right >= screen_width:
            ball_speed_x *= -1

        if ball.top < -1 or ball.bottom > screen_height + 1:
            ball.center = (screen_width / 2, screen_height / 2)
            ball_speed_x = ball_speed_x * random.choice([-1, 1])
            ball_speed_y = ball_speed_y * random.choice([-1, 1])

    def ballmovement(ball,player,bot):
        global ball_speed_x, ball_speed_y

        if ball.colliderect(player) or ball.colliderect(bot):
            ball_speed_x *= -1

        ball.x += ball_speed_x
        ball.y += ball_speed_y

        if ball.top <= 0 or ball.bottom >= screen_height:
            ball_speed_y *= -1

        if ball.left < 0 or ball.right > screen_width:
            ball.center = (screen_width / 2, screen_height / 2)
            ball_speed_x = ball_speed_x * random.choice([-1, 1])
            ball_speed_y = ball_speed_y * random.choice([-1, 1])

    def playermovement(ball,player,bot):
        if ay < -5:
            player.y -= 3
        elif ay > 10:
            player.y += 3

        if player.top <= 0:
            player.top = 0
        if player.bottom >= screen_height:
            player.bottom = screen_height
        if bot.top <= 0:
            bot.top = 0
        if bot.bottom >= screen_height:
            bot.bottom = screen_height

        if bot.y < ball.y:
            bot.y += random.randint(1, 3)
        if bot.y > ball.y:
            bot.y -= random.randint(1, 3)

    def playermovementX(ball,player,bot):
        if ax < -5:
            player.x += 4
        elif ax > 5:
            player.x -= 4

        if player.left <= 0:
            player.left = 0
        if player.right >= screen_width:
            player.right = screen_width
        if bot.left <= 0:
            bot.left = 0
        if bot.right >= screen_width:
            bot.right = screen_width

        if bot.x < ball.x:
            bot.x += random.randint(2, 3)
        if bot.x > ball.x:
            bot.x -= random.randint(2, 3)
    
    def game(mode):
        global ball
        global player
        global bot
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        player_score_text = font.render(str(player_score), True, (0, 96, 255))
        bot_score_text = font.render(str(bot_score), True, (224, 76, 76))
        player_score_rect = player_score_text.get_rect()
        bot_score_rect = bot_score_text.get_rect()

        player_score_rect.center = (
           int(screen_width * 3 / 4), int(screen_height * 1 / 3))
        bot_score_rect.center = (
           int(screen_width * 1 / 4), int(screen_height * 1 / 3))
        if mode == "x":
            scoreX(ball)
            ballmovementX(ball,player,bot)
            playermovementX(ball,player,bot)
        else:
            score(ball)
            ballmovement(ball,player,bot)
            playermovement(ball,player,bot)

        pygame.draw.rect(screen, (0, 96, 255), player)
        pygame.draw.rect(screen, (224, 76, 76), bot)
        pygame.draw.ellipse(screen, light_gray, ball)
        screen.blit(player_score_text, player_score_rect)
        screen.blit(bot_score_text, bot_score_rect)

    def menu():
        global game_state
        global mode
        global ball
        global player
        global bot
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()       
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    mode = "x" if mode == "y" else "y"
                    print(mode)
                if event.key == pygame.K_UP:
                    mode = "y" if mode == "x" else "x"
                    print(mode)
                if event.key == pygame.K_SPACE:
                    current_mode = mode_data[mode]
                    ball = pygame.Rect(screen_width / 2 - 10, screen_height / 2 - 10, 20, 20)
                    player = pygame.Rect(current_mode["player_posX"], current_mode["player_posY"],
                                            current_mode["player_width"], current_mode["player_height"])
                    bot = pygame.Rect(current_mode["bot_posX"], current_mode["bot_posY"],
                                        current_mode["player_width"], current_mode["player_height"])    
                    game_state = "playing"
                    print(game_state)
        
        title_text = font.render(str("Pong Fisioterapêutico"), True, (255, 255, 255))
        instruction_text = smallfont.render(str("Setinhas para mudar o modo, barra de espaço para iniciar"), True, (255, 255, 255))
        mode_text = smallfont.render(str(f"Modo selecionado: {'vertical' if mode == 'y' else 'horizontal'}"), True, (255, 255, 255))
        calibration_text = smallfont.render('Sensor Calibrado!' if calibrated else 'Calibrando o sensor, mantenha parado....', True, (255, 255, 255))        
        
        title_text_rect = title_text.get_rect()
        instruction_text_rect = instruction_text.get_rect()
        mode_text_rect = mode_text.get_rect()
        calibration_text_rect = calibration_text.get_rect()
        
        title_text_rect.center = (
           int(screen_width * 2 / 4), int(screen_height * 1 / 4))
        instruction_text_rect.center = (
           int(screen_width * 2 / 4), int(screen_height * 4 / 5))
        mode_text_rect.center = (
           int(screen_width * 2 / 4), int(screen_height * 2 / 4))
        calibration_text_rect.center = (
           int(screen_width * 2 / 4), int(screen_height * 2 / 3))
        
        screen.blit(title_text, title_text_rect)
        screen.blit(instruction_text, instruction_text_rect)        
        screen.blit(mode_text, mode_text_rect)
        screen.blit(calibration_text, calibration_text_rect)

    while True:
        screen.fill(bg_color)
        if game_state == "playing":
            game(mode)
        else:
            menu()
        pygame.display.flip()
        clock.tick(60)

thread1 = Thread(target=read_data)
thread2 = Thread(target=main)
thread1.start()
thread2.start()
