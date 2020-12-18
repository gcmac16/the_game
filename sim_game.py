import argparse
import logging

from the_game.exceptions import NoValidMoveError
from the_game.game import Game


logger = logging.getLogger('sim_game_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('sim.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)


class SimGame(object):

    def __init__(
        self,
        n_games: int = 100,
        player_style: str = 'optimized',
        n_players: int = 4,
        n_cards: int = 6
    ):
        self.logger = logger
        self.n_games = n_games
        self.player_style = player_style
        self.n_players = n_players
        self.n_cards = n_cards

    def run_sim(self):
        for _ in range(self.n_games):
            logger.info('Starting New Game')
            game = Game(self.n_players, 
                        self.n_cards,
                        logger,
                        player_style=self.player_style)

            self.sim_single_game(game)

    def sim_single_game(self, game: Game):
        game.setup_game()
        game.deal_cards()

        for player_id, player in game.players.items():
            logger.info(f"Player {player_id} dealt hand {player.hand}")

        while not game.game_won:
            game.make_move()
            try:
                game.make_move()
            except NoValidMoveError:
                n_cards_remaining = sum([
                    len(game.deck), 
                    sum([len(p.hand) for p in game.players.values()])
                ])

                logger.info(f"Game Lost - {n_cards_remaining} cards remaining")
                return

        logger.info("Game Won")
        return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_games', action='store', type=int, default=100, required=False)
    parser.add_argument('--player_style', action='store', type=str, default='optimized', required=False)
    parser.add_argument('--n_players', action='store', type=int, default=3, required=False)
    parser.add_argument('--n_cards', action='store', type=str, default=6, required=False)
    args = parser.parse_args()

    log_str = f"Starting simulation with args n_games = {args.n_games}, player_style = {args.player_style}"
    logger.info(log_str)

    sim = SimGame(n_games=args.n_games, player_style=args.player_style)
    sim.run_sim()
