import os
from base.move import Move
from parsing.PDN import PDNReader, PDNWriter, translate_to_fen, board_to_PDN_ready
from util.globalconst import BLACK, WHITE, MAN, KING, FREE, square_map


def test_board_to_PDN_ready():
    board_moves = [Move([[23, BLACK | MAN, FREE], [29, WHITE | MAN, FREE], [35, FREE, FREE], [40, WHITE | MAN, FREE],
                        [45, FREE, BLACK | KING]],
                        'Black double jump taking out two white men and landing in the king row')]
    pdn_moves, pdn_annotations = [[16, 23, 32]], \
                                 ['Black double jump taking out two white men and landing in the king row']
    moves, annotations = board_to_PDN_ready(board_moves)
    assert moves == pdn_moves
    assert annotations == pdn_annotations
    # First moves from Ballot 1, trunk line in Complete Checkers by Richard Pask
    board_moves = [Move([[square_map[9], BLACK | MAN, FREE], [square_map[13], FREE, BLACK | MAN]], ""),
                   Move([[square_map[21], WHITE | MAN, FREE], [square_map[17], FREE, WHITE | MAN]], ""),
                   Move([[square_map[5], BLACK | MAN, FREE], [square_map[9], FREE, BLACK | MAN]], ""),
                   Move([[square_map[25], WHITE | MAN, FREE], [square_map[21], FREE, WHITE | MAN]], ""),
                   Move([[square_map[11], BLACK | MAN, FREE], [square_map[15], FREE, BLACK | MAN]], ""),
                   Move([[square_map[29], WHITE | MAN, FREE], [square_map[25], FREE, WHITE | MAN]], ""),
                   Move([[square_map[9], BLACK | MAN, FREE], [square_map[14], FREE, BLACK | MAN]], ""),
                   Move([[square_map[23], WHITE | MAN, FREE], [square_map[18], FREE, WHITE | MAN]], ""),
                   Move([[square_map[14], BLACK | MAN, FREE], [square_map[18], WHITE | MAN, FREE],
                         [square_map[23], FREE, BLACK | MAN]], ""),
                   Move([[square_map[27], WHITE | MAN, FREE], [square_map[23], BLACK | MAN, FREE],
                         [square_map[18], FREE, FREE], [square_map[15], BLACK | MAN, FREE],
                         [square_map[11], FREE, WHITE | MAN]], ""),
                   Move([[square_map[8], BLACK | MAN, FREE], [square_map[11], WHITE | MAN, FREE],
                         [square_map[15], FREE, BLACK | MAN]], ""),
                   Move([[square_map[17], WHITE | MAN, FREE], [square_map[14], FREE, WHITE | MAN]], ""),
                   Move([[square_map[10], BLACK | MAN, FREE], [square_map[14], WHITE | MAN, FREE],
                         [square_map[17], FREE, BLACK | MAN]], ""),
                   Move([[square_map[21], WHITE | MAN, FREE], [square_map[17], BLACK | MAN, FREE],
                         [square_map[14], FREE, WHITE | MAN]], ""),
                   Move([[square_map[12], BLACK | MAN, FREE], [square_map[16], FREE, BLACK | MAN]], ""),
                   Move([[square_map[24], WHITE | MAN, FREE], [square_map[20], FREE, WHITE | MAN]],
                        "26-23; 16-19 23-16; 7-11 16-7 3-26 30-23; 4-8 25-22; 8-11 24-19; 15-24 28-19; 6-10 to a draw"),
                   Move([[square_map[16], BLACK | MAN, FREE], [square_map[19], FREE, BLACK | MAN]], ""),
                   Move([[square_map[25], WHITE | MAN, FREE], [square_map[21], FREE, WHITE | MAN]],
                        "32-27; 4-8 25-21 same"),
                   Move([[square_map[4], BLACK | MAN, FREE], [square_map[8], FREE, BLACK | MAN]], ""),
                   Move([[square_map[32], WHITE | MAN, FREE], [square_map[27], FREE, WHITE | MAN]], ""),
                   Move([[square_map[8], BLACK | MAN, FREE], [square_map[12], FREE, BLACK | MAN]], ""),
                   Move([[square_map[27], WHITE | MAN, FREE], [square_map[24], FREE, WHITE | MAN]], "")]
    pdn_moves = [[27, 24], [8, 12], [32, 27], [4, 8], [25, 21], [16, 19], [24, 20], [12, 16], [21, 14], [10, 17],
                 [17, 14], [8, 15], [27, 18, 11], [14, 23], [23, 18], [9, 14], [29, 25], [11, 15], [25, 21], [5, 9],
                 [21, 17], [9, 13]]
    pdn_annotations = ['', '', '', '', '32-27; 4-8 25-21 same', '',
                       '26-23; 16-19 23-16; 7-11 16-7 3-26 30-23; 4-8 25-22; 8-11 24-19; 15-24 28-19; 6-10 to a draw',
                       '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    moves, annotations = board_to_PDN_ready(board_moves)
    assert moves == pdn_moves
    assert annotations == pdn_annotations


def test_parse_PDN_string_success():
    pdn_string = '[Event "Casual Game"]\n' + \
                 '[Site "https://itsyourturn.com"]\n' + \
                 '[Date "2019.11.26"]\n' + \
                 '[Round "*"]\n' + \
                 '[White "Jubai"]\n ' + \
                 '[Black "windycity"]\n' + \
                 '[Result "1-0"]\n' + \
                 '[Ply "111"]\n' + \
                 '\n' + \
                 '1. 10-15 23-18 2. 7-10 22-17 3. 15-22 25-18 4. 11-15 \n' + \
                 '18-11 5. 8-15 24-20 6. 4-8 27-23 7. 9-13 20-16 8. \n' + \
                 '13-22 26-17 9. 12x19x26 30-23 10. 3-7 23-19 11. 15-24 \n' + \
                 '28-19 12. 7-11 17-14 13. 10-17 21-14 14. 2-7 32-27 \n' + \
                 '15. 8-12 29-25 16. 6-9 31-26 17. 9-18 19-15 18. 7-10 \n' + \
                 '15-8 19. 5-9 26-22 20. 10-15 22-17 21. 1-6 17-14 22. \n' + \
                 '9-13 14-10 23. 6-9 8-3 24. 15-19 3-7 25. 19-23 27-24 \n' + \
                 '26. 23-27 24-20 27. 13-17 25-21 28. 17-22 21-17 29. \n' + \
                 '18-23 17-13 30. 9-14 10-6 31. 14-17 6-2 32. 23-26 \n' + \
                 '7-10 33. 22-25 10-14 34. 17-21 14-18 35. 26-31 13-9 \n' + \
                 '36. 25-30 18-22 37. 27-32 9-5 38. 30-26 22-18 39. \n' + \
                 '26-23 18-27 40. 32-23 5-1 41. 21-25 2-7 42. 25-30 \n' + \
                 '7-10 43. 31-26 10-15 44. 26-31 1-6 45. 30-25 6-9 \n' + \
                 '46. 23-26 9-14 47. 26-22 15-19 48. 25-21 20-16 \n' + \
                 '49. 22-17 14-18 50. 17-22 18-25 51. 21-30 16-11 \n' + \
                 '52. 31-26 11-7 53. 26-23 19-26 54. 30-23 7-3 55. \n' + \
                 '23-18 3-8 56. 18-15 1-0\n'
    reader = PDNReader.from_string(pdn_string)
    game = reader.read_game(0)
    assert game.event == "Casual Game"
    assert game.date == "2019.11.26"
    assert game.white_player == "Jubai"
    assert game.black_player == "windycity"
    assert game.result == "1-0"
    board_moves = [Move(m) for m in [[[30, 9, 16], [24, 16, 9]], [[7, 10, 16], [12, 16, 10]],
                                     [[35, 9, 16], [30, 16, 9]],
                                     [[13, 6, 16], [7, 16, 10]], [[47, 9, 16], [41, 10, 16], [35, 16, 9]],
                                     [[29, 10, 16], [35, 9, 16], [41, 16, 10]], [[41, 9, 16], [35, 16, 9]],
                                     [[18, 6, 16], [13, 16, 6]], [[46, 9, 16], [41, 16, 9]], [[23, 6, 16], [18, 16, 6]],
                                     [[37, 9, 16], [42, 10, 16], [47, 16, 9]],
                                     [[30, 10, 16], [36, 9, 16], [42, 16, 10]],
                                     [[31, 9, 16], [36, 16, 9]], [[25, 10, 16], [30, 16, 10]],
                                     [[36, 9, 16], [31, 16, 9]],
                                     [[28, 6, 16], [23, 16, 6]], [[42, 9, 16], [37, 16, 9]],
                                     [[24, 10, 16], [29, 16, 10]],
                                     [[41, 9, 16], [36, 16, 9]], [[20, 10, 16], [25, 16, 10]],
                                     [[35, 9, 16], [41, 16, 9]],
                                     [[14, 10, 16], [20, 16, 10]], [[47, 9, 16], [42, 16, 9]],
                                     [[9, 10, 16], [14, 16, 10]],
                                     [[41, 9, 16], [46, 16, 9]], [[19, 10, 16], [24, 16, 10]],
                                     [[46, 9, 16], [41, 16, 9]],
                                     [[13, 10, 16], [19, 16, 10]], [[42, 5, 16], [47, 16, 9]],
                                     [[8, 10, 16], [13, 16, 10]],
                                     [[37, 5, 16], [42, 16, 5]], [[15, 6, 16], [9, 16, 10]],
                                     [[45, 9, 16], [40, 10, 16], [35, 16, 9]],
                                     [[30, 10, 16], [35, 9, 16], [40, 16, 10]],
                                     [[41, 9, 16], [35, 16, 9]], [[36, 10, 16], [30, 16, 10]],
                                     [[47, 9, 16], [41, 16, 9]],
                                     [[20, 6, 16], [15, 16, 6]], [[40, 5, 16], [45, 16, 9]],
                                     [[30, 10, 16], [36, 16, 10]],
                                     [[42, 5, 16], [47, 16, 9]], [[26, 6, 16], [20, 16, 6]], [[41, 5, 16], [46, 16, 9]],
                                     [[25, 10, 16], [30, 16, 10]], [[31, 5, 16], [37, 16, 5]],
                                     [[19, 10, 16], [25, 16, 10]],
                                     [[36, 5, 16], [42, 16, 5]], [[13, 10, 16], [19, 16, 10]],
                                     [[35, 5, 16], [41, 16, 5]],
                                     [[14, 6, 16], [8, 16, 10]], [[25, 5, 16], [31, 16, 5]], [[19, 6, 16], [14, 16, 6]],
                                     [[20, 5, 16], [25, 16, 5]], [[31, 6, 16], [26, 16, 6]], [[30, 5, 16], [35, 16, 5]],
                                     [[37, 6, 16], [31, 16, 6]], [[31, 5, 16], [36, 16, 5]], [[42, 6, 16], [37, 16, 6]],
                                     [[26, 5, 16], [31, 16, 5]], [[34, 6, 16], [28, 16, 6]], [[35, 5, 16], [40, 16, 5]],
                                     [[40, 6, 16], [34, 16, 6]], [[29, 5, 16], [35, 16, 5]],
                                     [[7, 10, 16], [13, 16, 10]],
                                     [[24, 5, 16], [29, 16, 5]], [[12, 6, 16], [7, 16, 10]], [[14, 5, 16], [20, 16, 5]],
                                     [[25, 6, 16], [19, 16, 6]], [[20, 5, 16], [26, 16, 5]], [[31, 6, 16], [25, 16, 6]],
                                     [[9, 5, 16], [14, 16, 5]], [[36, 6, 16], [31, 16, 6]], [[19, 5, 16], [24, 16, 5]],
                                     [[41, 6, 16], [36, 16, 6]], [[15, 5, 16], [20, 16, 5]],
                                     [[24, 6, 16], [18, 5, 16], [12, 16, 6]], [[13, 5, 16], [19, 16, 5]],
                                     [[29, 6, 16], [24, 16, 6]], [[20, 5, 16], [25, 6, 16], [30, 16, 5]],
                                     [[46, 6, 16], [41, 16, 6]], [[14, 5, 16], [20, 16, 5]], [[48, 6, 16], [42, 16, 6]],
                                     [[12, 5, 16], [17, 16, 5]], [[45, 6, 16], [40, 16, 6]], [[8, 5, 16], [13, 16, 5]],
                                     [[37, 6, 16], [31, 5, 16], [25, 16, 6]], [[19, 5, 16], [25, 6, 16], [31, 16, 5]],
                                     [[31, 6, 16], [25, 16, 6]], [[13, 5, 16], [18, 16, 5]],
                                     [[39, 6, 16], [34, 5, 16], [29, 16, 6]],
                                     [[24, 5, 16], [29, 6, 16], [34, 16, 5]],
                                     [[35, 6, 16], [29, 16, 6]], [[7, 5, 16], [13, 16, 5]],
                                     [[47, 6, 16], [41, 5, 16], [35, 16, 6]],
                                     [[17, 5, 16], [23, 6, 16], [29, 16, 16], [35, 6, 16], [41, 16, 5]],
                                     [[41, 6, 16], [36, 5, 16], [31, 16, 6]], [[26, 5, 16], [31, 6, 16], [36, 16, 5]],
                                     [[28, 6, 16], [23, 16, 6]], [[20, 5, 16], [26, 16, 5]], [[40, 6, 16], [35, 16, 6]],
                                     [[6, 5, 16], [12, 16, 5]], [[34, 6, 16], [28, 16, 6]],
                                     [[12, 5, 16], [18, 6, 16], [24, 16, 5]], [[30, 6, 16], [24, 5, 16], [18, 16, 6]],
                                     [[18, 5, 16], [24, 16, 5]], [[42, 6, 16], [36, 5, 16], [30, 16, 6]],
                                     [[24, 5, 16], [30, 6, 16], [36, 16, 5]], [[36, 6, 16], [31, 16, 6]],
                                     [[13, 5, 16], [19, 16, 5]], [[35, 6, 16], [30, 16, 6]],
                                     [[19, 5, 16], [24, 16, 5]]]]
    assert game.moves == board_moves


def test_parse_PDN_file_success():
    pdn_file = os.path.join('training', 'OCA_2.0.pdn')
    with PDNReader.from_file(pdn_file) as reader:
        game_list = reader.get_game_list()
        assert len(game_list) == 22621
        assert game_list[5].name == "Edinburgh 1847, game 2: Anderson, A. vs. Wyllie, J."
        game = reader.read_game(22620)
        assert game.event == "German Open 2004"
        game = reader.read_game(5)
        assert game.event == "Edinburgh 1847, game 2"
        game = reader.read_game(0)
        assert game.event == "Manchester 1841"


def test_write_PDN_file_success(tmp_path):
    pdn_filepath = os.path.join(tmp_path, "sample.pdn")
    event = "German Open 2004"
    date = "2004-05-01"
    rnd = ""
    black_player = "Morgan, John"
    white_player = "Pawlek, Dennis"
    site = "Reutlingen"
    next_to_move = "black"
    black_men = range(1, 13)
    white_men = range(21, 33)
    black_kings = []
    white_kings = []
    board_orientation = "white_on_top"
    result = "1/2-1/2"
    moves = [[[11, 15], [22, 17]], [[15, 19], [24, 15]], [[10, 19], [23, 16]], [[12, 19], [25, 22]],
             [[7, 10], [27, 24]], [[10, 15], [17, 13]], [[9, 14], [29, 25]], [[6, 10], [22, 17]], [[1, 6], [26, 23]],
             [[19, 26], [30, 23]], [[8, 11], [24, 19]], [[15, 24], [28, 19]], [[3, 7], [25, 22]], [[11, 15], [32, 28]],
             [[15, 24], [28, 19]], [[7, 11], [19, 16]], [[11, 20], [23, 19]], [[14, 18], [22, 15]], [[4, 8], [31, 27]],
             [[5, 9], [27, 23]], [[9, 14], [19, 16]], [[10, 19, 26], [17, 10, 1]], ['1/2-1/2']]
    PDNWriter.to_file(pdn_filepath, event, site, date, rnd, black_player, white_player, next_to_move, black_men,
                      white_men, black_kings, white_kings, result, board_orientation, moves)
    with open(pdn_filepath) as f1:
        with open(os.path.join('training', 'german_open_2004.pdn')) as f2:
            assert f1.readlines() == f2.readlines()


def test_write_PDN_string_success():
    event = "German Open 2004"
    site = "Reutlingen"
    date = "2004-05-01"
    rnd = ""
    next_to_move = "black"
    black_player = "Morgan, John"
    white_player = "Pawlek, Dennis"
    black_men = range(1, 13)
    white_men = range(21, 33)
    black_kings = []
    white_kings = []
    board_orientation = "white_on_top"
    result = "1/2-1/2"
    moves = [[[11, 15], [22, 17]], [[15, 19], [24, 15]], [[10, 19], [23, 16]], [[12, 19], [25, 22]],
             [[7, 10], [27, 24]], [[10, 15], [17, 13]], [[9, 14], [29, 25]], [[6, 10], [22, 17]], [[1, 6], [26, 23]],
             [[19, 26], [30, 23]], [[8, 11], [24, 19]], [[15, 24], [28, 19]], [[3, 7], [25, 22]], [[11, 15], [32, 28]],
             [[15, 24], [28, 19]], [[7, 11], [19, 16]], [[11, 20], [23, 19]], [[14, 18], [22, 15]], [[4, 8], [31, 27]],
             [[5, 9], [27, 23]], [[9, 14], [19, 16]], [[10, 19, 26], [17, 10, 1]], ['1/2-1/2']]
    pdn = PDNWriter.to_string(event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                              black_kings, white_kings, result, board_orientation, moves)
    assert pdn == '[Event "German Open 2004"]\n' + \
           '[Date "2004-05-01"]\n' + \
           '[Black "Morgan, John"]\n' + \
           '[White "Pawlek, Dennis"]\n' + \
           '[Site "Reutlingen"]\n' + \
           '[Result "1/2-1/2"]\n' + \
           '[BoardOrientation "white_on_top"]\n' + \
           '1. 11-15 22-17 2. 15-19 24x15 3. 10x19 23x16 4. 12x19 25-22 5. 7-10 27-24 6. 10-15 17-13 7. 9-14 29-25 ' \
           '8. 6-10 22-17\n' \
           '9. 1-6 26-23 10. 19x26 30x23 11. 8-11 24-19 12. 15x24 28x19 13. 3-7 25-22 14. 11-15 32-28 15. 15x24 ' \
           '28x19\n' + \
           '16. 7-11 19-16 17. 11x20 23-19 18. 14-18 22x15 19. 4-8 31-27 20. 5-9 27-23 21. 9-14 19-16 22. 10x19x26 ' \
           '17x10x1 1/2-1/2\n'


def test_translate_to_fen():
    # Captive Cossacks - Pask's SOIC p. 83, Diagram 57
    next_to_move = "white"
    black_men = [17]
    white_men = [26]
    black_kings = [30]
    white_kings = [27]
    assert translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings) == \
           "W:W26,K27:B17,K30"
