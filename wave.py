"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

# Brandon Nathasingh bn243 Taerim Oem te89
# 12/14/19
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class ar to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

    #Attribute _last: the number of keys pressed last animation frame
    #Invariant: _lastkeys is an int >=0

    #Attribute _direction: the direction of the ship laterally on the screen
    #Invariant _direction is a string 'right' or 'left'

    #Attribute _interval: how many steps the aliens take before a random one
    #                     shoots
    #Invariant _interval is a random int between 1 and BOLT_RATE

    #Attribute _steps: how many steps the aliens have taken since switching
    #                  directions
    #Invariant _steps is an int >= 0

    #Attribute _playerwin: an accumulator that says whether the player has won
    #Invariant _playerwin is a boolean

    #Attribute _alienwin: an accumulator that says whether the aliens breached
    #                     the defense line
    #Invariant _alienwin is a boolean

    #Attribute _wavenumber: an accumulator that tells which wave number the
    #                       player is on
    #Invariant _wavenumber is an int >= 1

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getShip(self):
        """
        Getter for the ship
        """
        return self._ship


    def setShip(self, ship):
        """
        Setter for ship
        """
        self._ship = ship


    def getLives(self):
        """
        Getter for the number of ship lives.
        """
        return self._lives


    def setLives(self, lives):
        """
        Setter for the number of ship lives.
        """
        self._lives = lives


    def getPlayerwin(self):
        """
        Getter that returns if the player has won the Wave yet.
        """
        return self._playerwin


    def getAlienwin(self):
        """
        Getter that returns if the aliens have breached the defense line yet.
        """
        return self._alienwin


    def setWavenumber(self,  number):
        """
        Setter for which level of wave the player is on.
        """
        self._wavenumber = number


    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self, wavenumber = 1):
        """
        Initializes the application, creating new attributes.
        """
        self._time=0
        self._last=0
        self._aliens = self._fillAliens()
        self._direction = 'right'
        self._ship = Ship(x = GAME_WIDTH // 2, y = SHIP_BOTTOM,
        width = SHIP_WIDTH, height = SHIP_HEIGHT, source = 'ship.png')
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
        linewidth=2, linecolor = 'blue')
        self._bolts = []
        self._interval = random.randrange(1, BOLT_RATE)
        self._steps=0
        self._lives = SHIP_LIVES
        self._playerwin = False
        self._alienwin = False
        self._wavenumber = 1


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,input,dt):
        """
        Handles the Wave. Moves the ship, aliens, and laser bolts.

        Determines whether the player won or lost the Wave.

        Parameter dt: The time since the last animation frame.
        Precondition: dt is a float.
        """
        self._animateShip(input)
        self._animateAliens(dt)
        self._animateBolt(input)
        self._shootfromAliens()
        self._handleShipBolts()
        self._handleAlienBolts()
        self._playerWins()
        self._alienWins()


    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the ship, aliens, defensive line, and bolts to the
        application window (view).

        Parameter view: the view window
        Precondition: view is a GView object"""
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)


    def _fillAliens(self):
        """
        This method fills a 2D array with aliens. All the aliens in a row are
        of the same image and that image rotates every two rows except for the
        first.
        """
        self._aliens = []
        for i in range(ALIEN_ROWS):
            row = []
            if i % 6 == 0 or i % 6 == 5:
                img = 0
            if i % 6 == 1 or i % 6== 2:
                img = 1
            if i % 6 == 3 or i % 6== 4:
                img = 2
            for j in range(ALIENS_IN_ROW):
                   row.append(Alien(x=(ALIEN_H_SEP + ALIEN_WIDTH//2) +
                   j*(ALIEN_H_SEP+ALIEN_WIDTH), y=GAME_HEIGHT - ALIEN_CEILING -
                   i*(ALIEN_V_SEP+ALIEN_HEIGHT), width= ALIEN_WIDTH, height =
                   ALIEN_HEIGHT, source = ALIEN_IMAGES[img]))
            self._aliens.append(row)
        return self._aliens


    def _animateShip(self,input):
        """
        This method animates the ship horizontally across the screen
        according to the user input.

        Parameter input: the user input used to control the ship
        Precondition: input is an instance of GInput
        """
        if self._ship != None:
            dx = self._ship.x
            if input.is_key_down('left'):
                dx -= SHIP_MOVEMENT #0.5*SHIP_WIDTH
            if input.is_key_down('right'):
                dx += SHIP_MOVEMENT
            if self._ship.x > GAME_WIDTH:
                dx = GAME_WIDTH
            if self._ship.x < 0:
                dx = 0
            self._ship.x = dx


    def _animateAliens(self, dt):
        """
        This methods animates the aliens with given horizontal and vertical
        separation between aliens. When the value of _time is greater than
        ALIEN_SPEED, this method moves the aliens and resets the _time to 0.
        Otherwise, this method adds the number of seconds that have passed
        since the aliens have moved to _time, and the aliens stay still.

        The aliens are sped up every Wave up a factor of 1.

        Parameter dt: the time since the last animation frame in seconds.
        Precondition: dt is a float.
        """
        if self._time * self._wavenumber > ALIEN_SPEED:
            if self._direction == 'right':
                self._animatealienright()
            if self._direction == 'left':
                self._animateAlienleft()
            self._time = 0
        else:
            self._time += dt


    def _animateBolt(self, input):
        """
        This method checks for a single key press of 'spacebar' or 'up' from
        the user and when detect, this method creates a bolt and shoots it
        from either the ship or the alien, with velocity or BOLT_SPEED or
        -BOLT_SPEED, respectively.

        Parameter input: the user input, used to control the ship
        Precondition: input is an instance of GInput
        """
        curr_keys = input.key_count
        if input.is_key_down('spacebar') or input.is_key_down('up'):
            player = False
            for bolt in self._bolts:
                if bolt.isPlayerBolt():
                    player = True
            if player == False:
                if self._ship != None:
                    self._bolts.append(Bolt(x=self._ship.x , y=self._ship.y +
                    10 , width = BOLT_WIDTH , height = BOLT_HEIGHT, fillcolor
                    = 'blue' , linewidth = 10, velocity = BOLT_SPEED))
                    newSound = Sound('pew1.wav')
                    newSound.play()
        for bolt in self._bolts:
            if bolt.isPlayerBolt():
                bolt.y += BOLT_SPEED
                if bolt.y - BOLT_HEIGHT // 2 > GAME_HEIGHT:
                    self._bolts.remove(bolt)
            else:
                bolt.y -= BOLT_SPEED
        self._last = curr_keys


    def _shootfromAliens(self):
        """This method controls which alien fires and when. It keep track of
        how many steps the aliens have taken since one last fired and generates
        a new random number after each fire that is used as the number of steps
        until the next bolt is fired.

        This method chooses which alien to fire by randomly choosen a bottommost
        alien in a column."""
        alienlist = []
        for col in range(ALIENS_IN_ROW):
            found = False
            for row in range(ALIEN_ROWS):
                if self._aliens[ALIEN_ROWS - 1 - row][col] \
                != None and found == False:
                    found = True
                    alienlist.append(self._aliens[ALIEN_ROWS - 1 - row][col])
        if len(alienlist)>=1:
            randaliennum = random.randrange(0, len(alienlist))
            randaliencol = randaliennum % ALIENS_IN_ROW
            randalien = alienlist[randaliennum]
        if self._steps > self._interval :
            self._bolts.append(Bolt(x = randalien.x, y = randalien.y,
            width = BOLT_WIDTH, height = BOLT_HEIGHT, fillcolor = 'blue',
            linewidth = 10 , velocity = -BOLT_SPEED))
            self._interval = random.randrange(1,BOLT_RATE)
            self._steps = 0


    def _findFirstAlien(self):
        """
        This method is a helper function to find the first alien in a row.
        """
        x = GAME_WIDTH
        alienresult = None
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                if self._aliens[row][col] != None:
                    if self._aliens[row][col].x<x:
                        x = self._aliens[row][col].x
                        alienresult = self._aliens[row][col]
        return alienresult


    def _findLastAlien(self):
        """
        This method is a helper function to find the last alien in a row.
        """
        x = 0
        alienresult = None
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                if self._aliens[row][col] != None:
                    if self._aliens[row][col].x > x:
                        x = self._aliens[row][col].x
                        alienresult = self._aliens[row][col]
        return alienresult


    def _playerWins(self):
        """
        Changes the _playerwin attribrute to True if all aliens have been killed
        and that round of the Wave is over.
        """
        alivealienlist = []
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                alivealien=self._aliens[row][col]
                if (alivealien != None):
                    alivealienlist.append(alivealien)
        if len(alivealienlist)==0:
            self._playerwin=True


    def _alienWins(self):
        """
        Changes the _alienwin attribrute to True if the aliens have breached
        the defensive line.
        """
        alienbelowlist = []
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                alienbelow=self._aliens[row][col]
                if (alienbelow != None and alienbelow.y \
                - ALIEN_HEIGHT // 2 < DEFENSE_LINE):
                    alienbelowlist.append(alienbelow)
        if len(alienbelowlist)!=0:
            self._alienwin=True


    def _animatealienright(self):
        """
        Helper function for _animateAliens() that moves the aliens to the right
        until they reach reach the right hand border then moves them down
        one step.
        """
        lastalien = self._findLastAlien()
        firstalien = self._findFirstAlien()
        if lastalien != None:
            if lastalien.x < GAME_WIDTH - ALIEN_H_SEP:
                self._steps += 1
                for row in self._aliens:
                    for item in row:
                        if item != None:
                            item.x += ALIEN_H_WALK
            if lastalien.x >= GAME_WIDTH - ALIEN_H_SEP:
                self._steps += 1
                for row in self._aliens:
                    for item in row:
                        if item != None:
                            item.y -= ALIEN_V_WALK
                self._direction = 'left'


    def _animateAlienleft(self):
        """
        Helper function for _animateAliens() that moves the aliens to the left
        until they reach reach the left hand border then moves them down
        one step."""
        lastalien = self._findLastAlien()
        firstalien = self._findFirstAlien()
        if firstalien != None:
            if firstalien.x <= ALIEN_H_SEP + ALIEN_WIDTH // 2:
                self._steps += 1
                for row in self._aliens:
                    for item in row:
                        if item != None:
                            item.y -= ALIEN_V_WALK
                self._direction = 'right'
                print(self._direction)
            if firstalien.x > ALIEN_H_SEP + ALIEN_WIDTH // 2:
                self._steps += 1
                for row in self._aliens:
                    for item in row:
                        if item != None:
                            item.x -= ALIEN_H_WALK


    # HELPER METHODS FOR COLLISION DETECTION
    def _handleAlienBolts(self):
        """This method checks whether each bolt fired from the an alien on
        the screen collides with the ship each animation frame, and deletes
        the ship if a collision is detected. If an alien bolt collides with
        a player and the ship is deleted, the number of ship lives is
        decreased by one."""
        for bolt in self._bolts:
            if bolt.isPlayerBolt() == False:
                if self._ship != None:
                    if self._ship.collides(bolt):
                        self._ship = None
                        self._lives -= 1


    def _handleShipBolts(self):
        """This method checks whether each bolt fired from the ship on the
        screen collides with any alien each animation frame, and deletes that
        alien if a collision is detected. This method plays a pop sound when the
        alien is hit with the bolt.
        """
        for bolt in self._bolts:
            if bolt.isPlayerBolt():
                for row in range(ALIEN_ROWS):
                    for col in range(ALIENS_IN_ROW):
                        alien = self._aliens[row][col]
                        if alien != None and alien.collides(bolt):
                            self._aliens[row][col] = None
                            self._bolts.remove(bolt)
                            popSound = Sound('pop2.wav')
                            popSound.play()
            else:
                if self._ship != None:
                    self._ship.collides(bolt)
                    pass
