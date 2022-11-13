import os
from datetime import datetime
from io import StringIO
from parsing.migrate import RCF2PDN
from parsing.PDN import PDNReader


def test_read_first_position_description_string():
    desc = "**Key Ending 10: First Position**\n\n" \
           "//Summary//\n\n" \
           "Force: 2 v 2.\n" \
           "Opposition: White has it.\n" \
           "Terms: White to move and win.\n" \
           "Description: The diagrammed position represents a late, and critical, phase of "\
           "First Position. Before tackling the winning procedure, it would be wise for "\
           "the student to take note of those features which distinguish First Position "\
           "from a nondescript two against two setting. In this way he will be able to "\
           "recognize it in its early stages, and take the appropriate action. Aside from "\
           "the attacker, having the Opposition, here White, the following conditions "\
           "must also hold:\n"\
           "# At least one of the defender's pieces is a single man rather than a king.\n"\
           "# The attacker has, or can develop, two kings while keeping the defender's single man pinned to the "\
           "right-hand side of the board. Typically, this man will initially be placed on square 3, 4 or 12. Of "\
           "course, if it was placed on square 1 or 2, then it would have free access to White's left-hand side, "\
           "and the position would just be a draw.\n"\
           "# The defender's other piece, which becomes a king (in the double-corner), is unable to reach the "\
           "sanctuary of the opposite double-corner.\n\n"\
           "Broadly speaking, White's winning procedure consists of attacking Black's king, "\
           "immobilizing it, and forcing Black's single man to advance into trouble. "\
           "Naturally, Black tries to avoid the advance of this man for as long as possible.\n"\
           "This theme, of attacking one piece to force another to move, arises in numerous "\
           "endings, and should be thoroughly grasped by the student.\n\n"\
           "-- From //Key Endings// by Richard Pask\n"\
           "<setup>"

    with StringIO(desc) as rcf:
        cvt = RCF2PDN()
        cvt._read_description(rcf)
        assert cvt.description == ["**Key Ending 10: First Position**\n",
                                   "\n",
                                   "//Summary//\n",
                                   "\n",
                                   "Force: 2 v 2.\n",
                                   "Opposition: White has it.\n",
                                   "Terms: White to move and win.\n",
                                   "Description: The diagrammed position represents a late, and critical, phase of "
                                   "First Position. Before tackling the winning procedure, it would be wise for the "
                                   "student to take note of those features which distinguish First Position from a "
                                   "nondescript two against two setting. In this way he will be able to recognize it "
                                   "in its early stages, and take the appropriate action. Aside from the attacker, "
                                   "having the Opposition, here White, the following conditions must also hold:\n",
                                   "# At least one of the defender's pieces is a single man rather than a king.\n",
                                   "# The attacker has, or can develop, two kings while keeping the defender's "
                                   "single man pinned to the right-hand side of the board. Typically, this man "
                                   "will initially be placed on square 3, 4 or 12. Of course, if it was placed "
                                   "on square 1 or 2, then it would have free access to White's left-hand side, "
                                   "and the position would just be a draw.\n",
                                   "# The defender's other piece, which becomes a king (in the double-corner), is "
                                   "unable to reach the sanctuary of the opposite double-corner.\n",
                                   "\n",
                                   "Broadly speaking, White's winning procedure consists of attacking Black's king, "
                                   "immobilizing it, and forcing Black's single man to advance into trouble. "
                                   "Naturally, Black tries to avoid the advance of this man for as long as possible.\n",
                                   "This theme, of attacking one piece to force another to move, arises in numerous "
                                   "endings, and should be thoroughly grasped by the student.\n",
                                   "\n",
                                   "-- From //Key Endings// by Richard Pask\n"]


def test_read_first_position_setup_string():
    setup = "white_first\n" + \
            "2_player_game\n" + \
            "flip_board 1\n" + \
            "black_men 12\n" + \
            "black_kings 28\n" + \
            "white_men\n" + \
            "white_kings 19 23\n"

    with StringIO(setup) as rcf:
        cvt = RCF2PDN()
        cvt._read_setup(rcf)
        assert cvt.next_to_move == 'white'
        assert cvt.num_players == 2
        assert cvt.flip_board == 1
        assert cvt.black_men == [12]
        assert cvt.black_kings == [28]
        assert cvt.white_men == []
        assert cvt.white_kings == [19, 23]


def test_first_position_rcf2pdn_migration():
    input_filename = os.path.join("training", "KeyEndgames", "FirstPosition.rcf")
    with open(input_filename) as rcf:
        pdn = RCF2PDN.with_string(rcf)
        reader = PDNReader.from_string(pdn)
        game = reader.read_game(0)
        assert game is not None


def test_read_first_position_moves_string():
    moves = "23-27;\n" + \
            "28-32;\n" + \
            "19-23;\n" + \
            "32-28;\n" + \
            "27-32;\n" + \
            "28-24;. The early advance with 12-16 " + \
            "[[./Training/KeyEndgames/support/FirstPosition_AlternativeA.rcf|loses%20quickly%20for%20Black]].\n" + \
            "23-18;. Of course 32-28, and the exchange with 24-19, cannot be permitted.\n" + \
            "24-28;. This represents Black's most stubborn defense. However, there " + \
            "[[./Training/KeyEndgames/support/FirstPosition_AlternativeB1.rcf|are]] " + \
            "[[./Training/KeyEndgames/support/FirstPosition_AlternativeB2.rcf|three]] " + \
            "[[./Training/KeyEndgames/support/FirstPosition_AlternativeB3.rcf|alternatives]] for White to master.\n" + \
            "18-15;\n" + \
            "28-24;\n" + \
            "32-28;\n" + \
            "24-27;. Black could alternately play 24-20 here, leading to " + \
            "[[./Training/KeyEndgames/support/FirstPosition_AlternativeC.rcf|this%20line%20of%20play]].\n" + \
            "15-18;\n" + \
            "12-16;. Forced now, as 27-32 loses quickly after 18-23.\n" + \
            "28-32;\n" + \
            "27-24;\n" + \
            "18-15;\n" + \
            "24-28;\n" + \
            "15-11;! Don't be tempted by 15-18?, as it " + \
            "[[./Training/KeyEndgames/support/FirstPosition_AlternativeD1.rcf|leads%20to%20a%20draw]].\n" + \
            "16-19;\n" + \
            "32-27;\n" + \
            "28-32;\n" + \
            "27-31;\n" + \
            "19-23;\n" + \
            "11-15;\n" + \
            "32-28;\n" + \
            "15-19;. **White wins.**\n"

    with StringIO(moves) as rcf:
        cvt = RCF2PDN()
        cvt._read_moves(rcf)
        assert cvt.moves == [[[23, 27], [28, 32]], [[19, 23], [32, 28]], [[27, 32], [28, 24]], [[23, 18], [24, 28]],
                             [[18, 15], [28, 24]], [[32, 28], [24, 27]], [[15, 18], [12, 16]], [[28, 32], [27, 24]],
                             [[18, 15], [24, 28]], [[15, 11], [16, 19]], [[32, 27], [28, 32]], [[27, 31], [19, 23]],
                             [[11, 15], [32, 28]], [[15, 19], '1-0']]
        assert cvt.annotations == [['', ''], ['', ''],
                                   ['', 'The early advance with 12-16 '
                                        '[[./Training/KeyEndgames/support/FirstPosition_AlternativeA.rcf|'
                                        'loses%20quickly%20for%20Black]].'],
                                   ['Of course 32-28, and the exchange with 24-19, cannot be permitted.',
                                    "This represents Black's most stubborn defense. However, there "
                                    '[[./Training/KeyEndgames/support/FirstPosition_AlternativeB1.rcf|are]] '
                                    '[[./Training/KeyEndgames/support/FirstPosition_AlternativeB2.rcf|three]] '
                                    '[[./Training/KeyEndgames/support/FirstPosition_AlternativeB3.rcf|alternatives]] '
                                    'for White to master.'],
                                   ['', ''], ['', 'Black could alternately play 24-20 here, leading to '
                                                  '[[./Training/KeyEndgames/support/FirstPosition_AlternativeC.rcf'
                                                  '|this%20line%20of%20play]].'],
                                   ['', 'Forced now, as 27-32 loses quickly after 18-23.'],
                                   ['', ''], ['', ''],
                                   ["! Don't be tempted by 15-18?, as it "
                                   '[[./Training/KeyEndgames/support/FirstPosition_AlternativeD1.rcf'
                                    '|leads%20to%20a%20draw]].', ''],
                                   ['', ''], ['', ''], ['', ''], ['**White wins.**', '']]


def test_read_glasgow_moves_string():
    moves = "11-15;\n" \
            "23-19;!\n" \
            "8-11;\n" \
            "22-17;\n" \
            "11-16;. These moves form the opening, which is excellent for inexperienced players to adopt.\n" \
            "24-20;\n" \
            "16-23;\n" \
            "27-11;\n" \
            "7-16;\n" \
            "20-11;\n" \
            "3-7;\n" \
            "28-24;. The alternative 11-8 is also playable.\n" \
            "7-16;\n" \
            "24-20;\n" \
            "16-19;\n" \
            "25-22;\n" \
            "4-8;\n" \
            "29-25;\n" \
            "19-24;. This leads to " \
            "[[training/Openings/support/Glasgow_Alternate1.rcf|interesting%20complications]].\n" \
            "17-14;. An interesting though only temporary sacrifice. " \
            "Instead, White can play safe with 17-13; 9-14, 26-23; etc.\n" \
            "9-18;\n" \
            "22-15;\n" \
            "10-19;\n" \
            "32-28;\n" \
            "6-10;! Now if White plays 26-23, Black wins with the " \
            "[[training/Openings/support/Glasgow_BlackWin.rcf|following%20line]].\n" \
            "25-22;. If now 8-11, White can draw with the " \
            "[[training/Openings/support/Glasgow_Draw.rcf|following%20line]].\n" \
            "5-9;\n" \
            "22-18;. If now 8-11 White plays 21-17 and holds the position despite the fact that he is temporarily " \
            'a man down. Black therefore "pitches" a man, and this leads to interesting complications.\n' \
            "9-14;\n" \
            "18-9;\n" \
            "1-5;\n" \
            "9-6;\n" \
            "2-9;\n" \
            "20-16;\n" \
            "9-14;\n" \
            "26-23;. The safest, at last recovering the sacrificed man.\n" \
            "19-26;\n" \
            "28-19;\n" \
            "5-9;\n" \
            "31-22;. Even game.\n"

    with StringIO(moves) as rcf:
        cvt = RCF2PDN()
        cvt._read_moves(rcf)
        assert cvt.moves == [[[11, 15], [23, 19]], [[8, 11], [22, 17]], [[11, 16], [24, 20]], [[16, 23], [27, 11]],
                             [[7, 16], [20, 11]], [[3, 7], [28, 24]], [[7, 16], [24, 20]], [[16, 19], [25, 22]],
                             [[4, 8], [29, 25]], [[19, 24], [17, 14]], [[9, 18], [22, 15]], [[10, 19], [32, 28]],
                             [[6, 10], [25, 22]], [[5, 9], [22, 18]], [[9, 14], [18, 9]], [[1, 5], [9, 6]],
                             [[2, 9], [20, 16]], [[9, 14], [26, 23]], [[19, 26], [28, 19]], [[5, 9], [31, 22]],
                             ['*']]
        assert cvt.annotations == [["", "!"], ["", ""],
                                   ["These moves form the opening, which is excellent for inexperienced players to "
                                    "adopt.", ""],
                                   ["", ""], ["", ""], ["", "The alternative 11-8 is also playable."], ["", ""],
                                   ["", ""], ["", ""],
                                   ["This leads to [[training/Openings/support/Glasgow_Alternate1.rcf|"
                                    "interesting%20complications]].",
                                   "An interesting though only temporary sacrifice. Instead, White can play safe with "
                                    "17-13; 9-14, 26-23; etc."],
                                   ["", ""], ["", ""],
                                   [r"! Now if White plays 26-23, Black wins with the "
                                    r"[[training/Openings/support/Glasgow_BlackWin.rcf|following%20line]].",
                                    r"If now 8-11, White can draw with the "
                                    r"[[training/Openings/support/Glasgow_Draw.rcf|following%20line]]."],
                                   ["",
                                    "If now 8-11 White plays 21-17 and holds the position despite the fact that he is "
                                    'temporarily a man down. Black therefore "pitches" a man, and this leads to '
                                    "interesting complications."],
                                   ["", ""], ["", ""], ["", ""],
                                   ["", "The safest, at last recovering the sacrificed man."],
                                   ["", ""], ["", "Even game."], [""]]


def test_glasgow_rcf2pdn_string():
    rcf_str = "<description>\n" \
              "**Glasgow opening**, part of the 11-15 group\n" \
              "11-15 is considered Black's best opening move. It is so popular that it has " \
              "branched off into more openings than any other initial move. Among the replies " \
              "that can be recommended for White are 23-19 or 23-18 or 22-18 or 22-17. On the " \
              "other hand, 24-20 and 24-19 and 21-17 are all considered inferior in varying degrees.\n" \
              "- from //How to Win At Checkers// by Fred Reinfeld\n" \
              "<setup>\n" \
              "black_first\n" \
              "2_player_game\n" \
              "flip_board 0\n" \
              "black_men 1 2 3 4 5 6 7 8 9 10 11 12\n" \
              "black_kings\n" \
              "white_men 21 22 23 24 25 26 27 28 29 30 31 32\n" \
              "white_kings\n" \
              "<moves>\n" \
              "11-15;\n" \
              "23-19;!\n" \
              "8-11;\n" \
              "22-17;\n" \
              "11-16;. These moves form the opening, which is excellent for inexperienced players to adopt.\n" \
              "24-20;\n" \
              "16-23;\n" \
              "27-11;\n" \
              "7-16;\n" \
              "20-11;\n" \
              "3-7;\n" \
              "28-24;. The alternative 11-8 is also playable.\n" \
              "7-16;\n" \
              "24-20;\n" \
              "16-19;\n" \
              "25-22;\n" \
              "4-8;\n" \
              "29-25;\n" \
              "19-24;. This leads to " \
              "[[training/Openings/support/Glasgow_Alternate1.rcf|interesting%20complications]].\n" \
              "17-14;. An interesting though only temporary sacrifice. " \
              "Instead, White can play safe with 17-13; 9-14, 26-23; etc.\n" \
              "9-18;\n" \
              "22-15;\n" \
              "10-19;\n" \
              "32-28;\n" \
              "6-10;! Now if White plays 26-23, Black wins with the " \
              "[[training/Openings/support/Glasgow_BlackWin.rcf|following%20line]].\n" \
              "25-22;. If now 8-11, White can draw with the " \
              "[[training/Openings/support/Glasgow_Draw.rcf|following%20line]].\n" \
              "5-9;\n" \
              "22-18;. If now 8-11 White plays 21-17 and holds the position despite the fact that he is temporarily " \
              'a man down. Black therefore "pitches" a man, and this leads to interesting complications.\n' \
              "9-14;\n" \
              "18-9;\n" \
              "1-5;\n" \
              "9-6;\n" \
              "2-9;\n" \
              "20-16;\n" \
              "9-14;\n" \
              "26-23;. The safest, at last recovering the sacrificed man.\n" \
              "19-26;\n" \
              "28-19;\n" \
              "5-9;\n" \
              "31-22;. Even game.\n"

    with StringIO(rcf_str) as rcf:
        pdn_str = RCF2PDN.with_string(rcf)
        now = datetime.now().strftime("%d/%m/%Y")
        assert pdn_str == '[Event "Glasgow opening"]\n' \
                          f'[Date "{now}"]\n' \
                          '[Round "*"]\n' \
                          '[Black "Player1"]\n' \
                          '[White "Player2"]\n' \
                          '[Site "*"]\n' \
                          '[Result "*"]\n' \
                          '[BoardOrientation "white_on_top"]\n' \
                          "% **Glasgow opening**, part of the 11-15 group\n" \
                          "% 11-15 is considered Black's best opening move. It is so popular that it " \
                          "has branched off into more openings than any other initial move. Among the " \
                          "replies that can be recommended for White are 23-19 or 23-18 or 22-18 or " \
                          "22-17. On the other hand, 24-20 and 24-19 and 21-17 are all considered " \
                          "inferior in varying degrees.\n" \
                          "% - from //How to Win At Checkers// by Fred Reinfeld\n"\
                          "\n"\
                          "1. 11-15 23-19! 2. 8-11 22-17 3. 11-16 {These moves form the opening, which is " \
                          "excellent for inexperienced players to\n" \
                          "adopt.} 24-20 4. 16x23 27x11 5. 7x16 20x11 6. 3-7 28-24 {The alternative 11-8 " \
                          "is also playable.} 7. 7x16 24-20\n" \
                          "8. 16-19 25-22 9. 4-8 29-25 10. 19-24 {This leads to\n" \
                          "[[training/Openings/support/Glasgow_Alternate1.rcf|interesting%20complications]].} "\
                          "17-14 {An interesting though only\n" \
                          "temporary sacrifice. Instead, White can play safe with 17-13; 9-14, 26-23; etc.} " \
                          "11. 9x18 22x15 12. 10x19 32-28\n" \
                          "13. 6-10! {Now if White plays 26-23, Black wins with the\n" \
                          "[[training/Openings/support/Glasgow_BlackWin.rcf|following%20line]].} " \
                          "25-22 {If now 8-11, White can draw with the\n" \
                          "[[training/Openings/support/Glasgow_Draw.rcf|following%20line]].} " \
                          "14. 5-9 22-18 {If now 8-11 White plays 21-17 and\n" \
                          "holds the position despite the fact that he is temporarily a man down. Black " \
                          'therefore "pitches" a man, and this leads\n' \
                          'to interesting complications.} 15. 9-14 18x9 16. 1-5 9-6 17. 2x9 20-16 18. 9-14 26-23 ' \
                          "{The safest, at last recovering\n" \
                          "the sacrificed man.} 19. 19x26 28x19 20. 5-9 31x22 {Even game.} *\n"
