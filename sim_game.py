import argparse
import json
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
        first_move_selection = 'optimized',
        n_players: int = 3,
        n_cards: int = 6
    ):
        self.logger = logger
        self.n_games = n_games
        self.player_style = player_style
        self.n_players = n_players
        self.n_cards = n_cards
        self.first_move_selection = first_move_selection

    def get_new_game(self):
        return Game(self.n_players, 
            self.n_cards,
            logger,
            player_style=self.player_style,
            first_move_selection=self.first_move_selection
        )


    def run_sim(self):
        for game_num in range(self.n_games):
            if game_num % 100 == 0:
                print(f"Completed {game_num} of {self.n_games}")
            
            game = self.get_new_game()
            self.sim_single_game(game)

    def sim_single_game(self, game: Game):
        game.setup_game()

        player_cards = {
            player_id: sorted(player.hand)
            for player_id, player in game.players.items()
        }

        log_body = {
            'game_event': 'start_game',
            'game_parameters': {
                'player_style': self.player_style,
                'n_players': self.n_players,
                'n_cards': self.n_cards,
                'first_move_selection': self.first_move_selection,
            },
            'starting_cards': player_cards
        }

        logger.info(json.dumps(log_body))

        while not game.game_won:
            try:
                game.make_move()
            except NoValidMoveError:
                n_cards_remaining = sum([
                    len(game.deck), 
                    sum([len(p.hand) for p in game.players.values()])
                ])

                logger.info(
                    json.dumps({
                        'game_event': 'game_over', 
                        'game_won': False,
                        'cards_remaining': n_cards_remaining,
                        'cards_in_deck_remaining': len(game.deck),
                    })
                )

                return

        logger.info(
            json.dumps({
                'game_event': 'game_over', 
                'game_won': True,
                'cards_remaining': 0
            })
        )
        return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--n_games',
        action='store', 
        type=int, 
        default=100, 
        required=False,
    )
    parser.add_argument(
        '--player_style', 
        action='store', 
        type=str, 
        default='optimized', 
        required=False,
    )
    parser.add_argument(
        '--n_players', 
        action='store',
        type=int,
        default=3,
        required=False
    )
    parser.add_argument(
        '--n_cards', 
        action='store',
        type=str,
        default=6,
        required=False
    )
    parser.add_argument(
        '--first_move_selection', 
        action='store', 
        type=str,
        default='optimized', 
        required=False
    )
    args = parser.parse_args()

    sim = SimGame(
        n_games=args.n_games, 
        player_style=args.player_style, 
        first_move_selection=args.first_move_selection,
        n_players=args.n_players,
        n_cards=args.n_cards
    )
    sim.run_sim()
