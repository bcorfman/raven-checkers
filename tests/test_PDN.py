import os
from parsing.PDN import PDNReader, PDNWriter, _translate_to_fen


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
    assert game.moves == [[[10, 15], [23, 18]], [[7, 10], [22, 17]],
                          [[15, 22], [25, 18]], [[11, 15], [18, 11]], [[8, 15], [24, 20]],
                          [[4, 8], [27, 23]], [[9, 13], [20, 16]], [[13, 22], [26, 17]],
                          [[12, 19, 26], [30, 23]], [[3, 7], [23, 19]],
                          [[15, 24], [28, 19]], [[7, 11], [17, 14]], [[10, 17], [21, 14]],
                          [[2, 7], [32, 27]], [[8, 12], [29, 25]], [[6, 9], [31, 26]],
                          [[9, 18], [19, 15]], [[7, 10], [15, 8]], [[5, 9], [26, 22]],
                          [[10, 15], [22, 17]], [[1, 6], [17, 14]], [[9, 13], [14, 10]],
                          [[6, 9], [8, 3]], [[15, 19], [3, 7]], [[19, 23], [27, 24]],
                          [[23, 27], [24, 20]], [[13, 17], [25, 21]], [[17, 22], [21, 17]],
                          [[18, 23], [17, 13]], [[9, 14], [10, 6]], [[14, 17], [6, 2]],
                          [[23, 26], [7, 10]], [[22, 25], [10, 14]], [[17, 21], [14, 18]],
                          [[26, 31], [13, 9]], [[25, 30], [18, 22]], [[27, 32], [9, 5]],
                          [[30, 26], [22, 18]], [[26, 23], [18, 27]], [[32, 23], [5, 1]],
                          [[21, 25], [2, 7]], [[25, 30], [7, 10]], [[31, 26], [10, 15]],
                          [[26, 31], [1, 6]], [[30, 25], [6, 9]], [[23, 26], [9, 14]],
                          [[26, 22], [15, 19]], [[25, 21], [20, 16]], [[22, 17], [14, 18]],
                          [[17, 22], [18, 25]], [[21, 30], [16, 11]], [[31, 26], [11, 7]],
                          [[26, 23], [19, 26]], [[30, 23], [7, 3]], [[23, 18], [3, 8]],
                          [[18, 15], ["1-0"]]]


def test_parse_PDN_file_success():
    pdn_file = os.path.join('training', 'OCA_2.0.pdn')
    with PDNReader.from_file(pdn_file) as reader:
        assert len(reader.get_game_list()) == 22621
        game = reader.read_game(22620)
        assert game.event == "German Open 2004"


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
    moves = [[[11, 15], [22, 17]], [[15, 19], [24, 15]], [[10, 19], [23, 16]], [[12, 19], [25, 22]], [[7, 10], [27, 24]], 
             [[10, 15], [17, 13]], [[9, 14], [29, 25]], [[6, 10], [22, 17]], [[1, 6], [26, 23]], [[19, 26], [30, 23]], 
             [[8, 11], [24, 19]], [[15, 24], [28, 19]], [[3, 7], [25, 22]], [[11, 15], [32, 28]], [[15, 24], [28, 19]], 
             [[7, 11], [19, 16]], [[11, 20], [23, 19]], [[14, 18], [22, 15]], [[4, 8], [31, 27]], [[5, 9], [27, 23]],
             [[9, 14], [19, 16]], [[10, 19, 26], [17, 10, 1]], ['1/2-1/2']]
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
    moves = [[[11, 15], [22, 17]], [[15, 19], [24, 15]], [[10, 19], [23, 16]], [[12, 19], [25, 22]], [[7, 10], [27, 24]], 
             [[10, 15], [17, 13]], [[9, 14], [29, 25]], [[6, 10], [22, 17]], [[1, 6], [26, 23]], [[19, 26], [30, 23]], 
             [[8, 11], [24, 19]], [[15, 24], [28, 19]], [[3, 7], [25, 22]], [[11, 15], [32, 28]], [[15, 24], [28, 19]], 
             [[7, 11], [19, 16]], [[11, 20], [23, 19]], [[14, 18], [22, 15]], [[4, 8], [31, 27]], [[5, 9], [27, 23]],
             [[9, 14], [19, 16]], [[10, 19, 26], [17, 10, 1]], ['1/2-1/2']]
    pdn = PDNWriter.to_string(event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men, black_kings, white_kings,
                              result, board_orientation, moves)
    assert pdn == '[Event "German Open 2004"]\n' + \
           '[Date "2004-05-01"]\n' + \
           '[Black "Morgan, John"]\n' + \
           '[White "Pawlek, Dennis"]\n' + \
           '[Site "Reutlingen"]\n' + \
           '[Result "1/2-1/2"]\n' + \
           '[BoardOrientation "white_on_top"]\n' + \
           '1. 11-15 22-17 2. 15-19 24x15 3. 10x19 23x16 4. 12x19 25-22 5. 7-10 27-24 6. 10-15 17-13 7. 9-14 29-25 ' \
           '8. 6-10 22-17\n' \
           '9. 1-6 26-23 10. 19x26 30x23 11. 8-11 24-19 12. 15x24 28x19 13. 3-7 25-22 14. 11-15 32-28 15. 15x24 '\
           '28x19\n' + \
           '16. 7-11 19-16 17. 11x20 23-19 18. 14-18 22x15 19. 4-8 31-27 20. 5-9 27-23 21. 9-14 19-16 22. 10x19x26 '\
           '17x10x1 1/2-1/2\n'


def test_translate_to_fen():
    # Captive Cossacks - Pask's SOIC p. 83, Diagram 57
    next_to_move = "white"
    black_men = [17]
    white_men = [26]
    black_kings = [30]
    white_kings = [27]
    assert _translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings) == \
        "W:W26,K27:B17,K30"
