import pygame
import random
import sqlite3
import datetime
import argparse

# TODO option to choose class - buttons?
# TODO argparse

# starting positions
start_position_x = 280
start_position_y = 370

width, height = 1000, 600


class Ship:
    """
    The class for the player - superclass of all ships available in the game

    speed: The number of pixel the ship moves every second
    max_capacity: The number of people the ship can hold before it must return to dock
    width_ship: The width of the ship when facing up
    length_ship: The length of the ship when facing up
    hits: Number of collisions with fire/sharks before game over
    obstacle_to_spawn: Number of obstacles to spawn after each unload
    name: The type of ship
    """
    speed = None
    max_capacity = None
    (ship_width, ship_length) = None, None
    hits = None
    obstacles_to_spawn = None
    name = None

    @property
    def image_name(self):
        return f'images/{self.name.replace(" ", "_")}.png'

    def __init__(self):
        self._avatar = pygame.image.load(self.image_name)  # the image of the ship
        self._current_capacity = 0
        self._avatar = pygame.transform.scale(self._avatar, (self.ship_width, self.ship_length))
        self._player = pygame.Rect(start_position_x, start_position_y, self.ship_width, self.ship_length)
        self.survivors_left = set()  # a set of all survivors on screen
        self._dangers = set()  # a set of all obstacles on screen
        self._score = 0
        self._rotation = 0

    def movement(self, keys):
        """
        In charge of responding to the player moving, using the arrow keys
        :param keys: pygame.keys.get_pressed() - a list of all keys currently held down
        """
        if keys[pygame.K_UP] and self._player.y - self.speed > 0:
            self._avatar = pygame.transform.rotate(self._avatar, 0 - self._rotation)
            self._player = pygame.Rect(self._player.x, self._player.y, self.ship_width, self.ship_length)
            self._rotation = 0
            self._player.y -= self.speed
        if keys[pygame.K_DOWN] and self._player.y + self.speed + self._player.height < height:
            if self._player.x > width - 200 and self._player.y + self.speed + self._player.height > height - 300:
                pass
            else:
                self._avatar = pygame.transform.rotate(self._avatar, 180 - self._rotation)
                self._player = pygame.Rect(self._player.x, self._player.y, self.ship_width, self.ship_length)
                self._rotation = 180
                self._player.y += self.speed
        if keys[pygame.K_LEFT] and self._player.x - self.speed > 0:
            self._avatar = pygame.transform.rotate(self._avatar, 90 - self._rotation)
            self._player = pygame.Rect(self._player.x, self._player.y, self.ship_length, self.ship_width)
            self._rotation = 90
            self._player.x -= self.speed
        if keys[pygame.K_RIGHT] and self._player.x + self._player.width + self.speed < width:
            if self._player.y > height - 475 and self._player.x + self.speed + self._player.width > width - 125:
                pass
            else:
                self._avatar = pygame.transform.rotate(self._avatar, 270 - self._rotation)
                self._player = pygame.Rect(self._player.x, self._player.y, self.ship_length, self.ship_width)
                self._rotation = 270
                self._player.x += self.speed
        pygame.display.update()

    def rescue(self, wreck):
        """
        To rescue a group of survivors
        :param wreck: the group of survivors to rescue
        """
        if self._current_capacity + wreck._value <= self.max_capacity:
            self._current_capacity += wreck._value
            wreck.rescued(self)
            num = random.randint(1, 3)
            if num % 2 == 0:  # spawning new survivors one in 3 times
                spawn_survivors(self)
                spawn_survivors(self)

        elif self._current_capacity < self.max_capacity:
            saved = self.max_capacity - self._current_capacity
            self._current_capacity += saved
            wreck.part_saved(saved)

    def unload(self):
        """
        To unload all survivors at the dock
        """
        self._score += self._current_capacity
        self._current_capacity = 0

        for i in range(self.obstacles_to_spawn):
            new_danger = Obstacle()
            self._dangers.add(new_danger)

    def refill(self):
        """
        Spawns 2 more groups of survivors if the screen is empty
        """
        if len(self.survivors_left) == 0:
            spawn_survivors(self)
            spawn_survivors(self)

    def __str__(self):
        return self.name.title()


class Small_Ship(Ship):
    name = "small ship"
    speed = 9
    max_capacity = 20
    (ship_width, ship_length) = 25, 75
    hits = 30
    obstacles_to_spawn = 2


class Medium_Ship(Ship):
    name = "medium ship"
    speed = 5
    max_capacity = 50
    (ship_width, ship_length) = 35, 105
    hits = 40
    obstacles_to_spawn = 4


class Large_Ship(Ship):
    """
    The largest ship available
    """
    name = "large ship"
    speed = 3
    max_capacity = 100
    (ship_width, ship_length) = 45, 135
    hits = 50
    obstacles_to_spawn = 5


class Survivor:
    """
    Groups of stranded people
    The goal of the game is to save as many as possible
    """

    def __init__(self):
        self._x = random.randint(0, width // 2)  # position on screen
        self._y = random.randint(0, height // 2)  # position on screen

        self._image = pygame.image.load('images/survivor.png')
        self._image = pygame.transform.scale(self._image, (70, 35))
        self._rect = pygame.Rect(self._y, self._x, 120, 60)

        self._value = random.randint(1, 10)  # number of survivors at spot
        lives = comic_sans.render(str(self._value), True, (255, 255, 255))
        self._image.blit(lives, (0, 0))

        self._time = 600

    def rescued(self, user):
        """
        When saved by player
        :param user: the player
        """
        user.survivors_left.remove(self)
        del self

    def part_saved(self, number):
        """
        When partially saved by the player - the ship does not have enough capacity for all
        :param number: the number of people saved
        """
        self._image.fill((50, 100, 250))
        self._image = pygame.image.load('images/survivor.png')
        self._image = pygame.transform.scale(self._image, (70, 35))
        self._value -= number
        lives = comic_sans.render(str(self._value), True, (255, 255, 255))
        MAIN_WINDOW.blit(self._image, (self._x, self._y))
        self._image.blit(lives, (0, 0))


class Obstacle:
    """
    An obstacle that the player must avoid
    """

    def __init__(self):
        """
        Randomly chooses between an image of a shark or a fire
        There is no difference between the 2 in size or danger

        The position on screen is also random
        """
        num = random.randint(1, 2)
        if num == 1:
            image = pygame.image.load('images/fire.png')
        else:
            image = pygame.image.load('images/shark.png')
        self._avatar = image
        self._avatar = pygame.transform.scale(self._avatar, (50, 50))
        self.pos_x = random.randint(1, width)
        self.pos_y = random.randint(1, height)
        self.rect = pygame.Rect(self.pos_x, self.pos_y, 50, 50)


def main(player):
    """
    The main game loop - runs constantly and calls all other functions and methods
    """
    game_clock = pygame.time.Clock()
    while True:  # so the window doesn't close immediately
        game_clock.tick(60)  # sets fps to 60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(1)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for s in player.survivors_left:
                        if player._player.colliderect(s._rect):  # if there are any survivors in proximity
                            player.rescue(s)
                            break
                if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                    if player._player.colliderect(dock_rect):
                        player.unload()  # release survivors

        draw_window(player)
        keys = pygame.key.get_pressed()
        player.movement(keys)
        player.refill()

        for d in player._dangers:
            if player._player.colliderect(d.rect):
                player.hits -= 10
                player._dangers.remove(d)
                break

        if player.hits <= 0:
            draw_window(player)
            pygame.time.wait(1000)
            game_over(player)
            break

        reduce_time(player)


def draw_window(player):
    """
    Draws the screen, 60 times a second
    """
    MAIN_WINDOW.fill((50, 100, 250))

    # survivors
    for s in player.survivors_left:
        MAIN_WINDOW.blit(s._image, (s._rect.x, s._rect.y))

    # dangers
    for d in player._dangers:
        MAIN_WINDOW.blit(d._avatar, (d.pos_x, d.pos_y))

    # top right texts
    capacity_score = comic_sans.render("Current capacity: {}".format(player._current_capacity), True, (255, 255, 255))
    max_capacity_show = comic_sans.render("Max Capacity: {}".format(player.max_capacity), True, (255, 255, 255))
    MAIN_WINDOW.blit(capacity_score, (width - capacity_score.get_width() - 10, 0))
    MAIN_WINDOW.blit(max_capacity_show, (width - capacity_score.get_width() - 10, capacity_score.get_height()))

    # bottom left texts
    score_text = comic_sans.render("Score: {}".format(player._score), True, (255, 255, 255))
    MAIN_WINDOW.blit(score_text, (10, height - score_text.get_height() - 10))
    health_text = comic_sans.render(f"Health: {player.hits}", True, (255, 255, 255))
    MAIN_WINDOW.blit(health_text, (10, height - score_text.get_height() - health_text.get_height() - 10))

    # the dock
    MAIN_WINDOW.blit(dock_image, (width - 150, height - 350))

    # the player
    MAIN_WINDOW.blit(player._avatar, (player._player.x, player._player.y))  # placing the player on the screen

    pygame.display.update()


def game_over(player):
    """"
    Runs when the player loses all their health

    Displays the text 'Game Over' and the players score
    """
    comic_sans_2 = pygame.font.SysFont("comic sans", 80)
    big_text = comic_sans_2.render("Game over", True, (255, 0, 0))
    small_text = comic_sans.render(f"You scored {player._score} points", True, (255, 255, 255))
    MAIN_WINDOW.blit(big_text, (width // 2 - big_text.get_width() // 2, (height - big_text.get_height()) // 2))
    MAIN_WINDOW.blit(small_text, ((width - small_text.get_width()) // 2, (height + big_text.get_height()) // 2))
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.display.quit()
    pygame.quit()


def spawn_survivors(user):
    """"
    The function to spawn survivors
    """
    user.survivors_left.add(Survivor())


def reduce_time(player):
    """
    Makes sure the groups of survivors will drown after a certain period if not rescued
    """
    for s in player.survivors_left.copy():
        s._time -= 1
        if s._time <= 0:
            player._score = max(0, player._score - s._value)
            player.survivors_left.remove(s)


def valid_int(x):
    try:
        num = int(x)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Expected integer, got {s!r}")

    if num > 3 or num < 1:
        raise argparse.ArgumentTypeError(f"Expected num between 1 and 3, got {num}")
    return num


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ship type")
    parser.add_argument("Type", type=valid_int, help="Size of ship. Enter num between 1 and 3 to refer to "
                                                     "small, medium or large ship")
    args = parser.parse_args()

    choice = args.Type
    if choice == 1:
        player = Small_Ship()
    elif choice == 2:
        player = Medium_Ship()
    else:
        player = Large_Ship()

    # setting up the game
    pygame.init()
    pygame.font.init()
    MAIN_WINDOW = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Sunken")
    comic_sans = pygame.font.SysFont('comicsans', 20)

    # setting the dock
    dock_image = pygame.image.load("images/dock.png")
    dock_image = pygame.transform.scale(dock_image, (150, 350))
    dock_rect = pygame.Rect(width - 150, height - 350, 150, 350)

    # running the game
    main(player)

    # collecting data to save into database
    game_date = datetime.datetime.now()
    game_date = game_date.strftime('%Y/%b/%d, %H:%M:%S')
    final_score = player._score
    ship_type = player.__str__()

    # connecting to database and inserting the info
    sunken_db = sqlite3.connect('Sunken')
    sunken_db.execute("CREATE TABLE IF NOT EXISTS Scores(score, ship, time)")
    sunken_db.execute(f"INSERT INTO Scores(score, ship, time) VALUES({final_score}, '{ship_type}', '{game_date}')")

    # printing out the scores by date into a text file
    with open('scores_by_date.txt', 'w') as scores:
        for game_score, ship_class, game_date in sunken_db.execute("SELECT * FROM Scores ORDER BY time DESC"):
            s = f"{game_score}\t| {ship_class}\t| {game_date}"
            print(s, file=scores)

    # printing out the high scores into another text file
    high_scores = open("high_scores.txt", 'w')
    for game_score, ship_class, game_date in sunken_db.execute("SELECT * FROM Scores ORDER BY score DESC"):
        s = f"{game_score}\t| {ship_class}\t| {game_date}"
        print(s, file=high_scores)
    high_scores.close()

    # saving changes and closing the database
    sunken_db.commit()
    sunken_db.close()
