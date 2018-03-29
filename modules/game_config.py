class Config:
    GAME_TICKS = 0
    GAME_WIDTH = 0
    GAME_HEIGHT = 0
    FOOD_MASS = 0
    FOOD_RADIUS = 2.5
    MAX_FRAGS_CNT = 0
    TICKS_TIL_FUSION = 0
    VIRUS_RADIUS = 0
    VIRUS_SPLIT_MASS = 0
    VISCOSITY = 0
    INERTION_FACTOR = 0
    SPEED_FACTOR = 0

    def update(self, config: dict):
        self.GAME_TICKS = config['GAME_TICKS']
        self.GAME_WIDTH = config['GAME_WIDTH']
        self.GAME_HEIGHT = config['GAME_HEIGHT']
        self.FOOD_MASS = config['FOOD_MASS']
        self.MAX_FRAGS_CNT = config['MAX_FRAGS_CNT']
        self.TICKS_TIL_FUSION = config['TICKS_TIL_FUSION']
        self.VIRUS_RADIUS = config['VIRUS_RADIUS']
        self.VIRUS_SPLIT_MASS = config['VIRUS_SPLIT_MASS']
        self.VISCOSITY = config['VISCOSITY']
        self.INERTION_FACTOR = config['INERTION_FACTOR']
        self.SPEED_FACTOR = config['SPEED_FACTOR']
