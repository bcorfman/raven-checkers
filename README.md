# Raven Checkers
## Project description
Raven is a checkers game program, for one or two players. While there are examples of excellent & free checkers programs out on the net (such as [Martin Fierz's Checkerboard](http://www.fierz.ch/checkers.htm)), Raven has a few differences.

* **Open-source code**. Raven uses existing open source code as a basis ([Martin Fierz's Simple Checkers evaluation function](http://www.fierz.ch/engines.php) and [Peter Norvig's search code from the AIMA project](http://aima.cs.berkeley.edu/python/readme.html)) for its AI engine.
* **Cross-platform**. Raven is written using Python 2.7 using its standard libraries. It has been tested on Windows, OS X Yosemite, and Linux Mint (Cassandra).
* **Great for checkers study**. Raven allows you to quickly set up board configurations using standard checkerboard notation. You can also describe your moves in the annotation window, and you can save and load games for later study. This is great for working through checkers books and learning techniques and tactics.

<img src="http://i.stack.imgur.com/XcPri.jpg">

# Future plans
Most checkers or chess programs go the route of deep search combined with perfect opening and endgame databases. These techniques are well-explored and not really all that interesting to me. I plan on making a big change in future versions of Raven by relying more on planning than brute-force search.

Here's what I'm thinking:

* *Implement a planning AI*. These plans will be based on tactics and strategies from Richard Pask's books [Starting Out in Checkers](http://www.amazon.com/Starting-Out-Checkers-Richard-Pask/dp/1857442636) and [Play Better Checkers & Draughts](http://www.bobnewell.net/checkers/bookorders/getpbcd1.html), which I use in my own checkers study.
* *Parse training files in order to inform the AI about best moves and positions*, whether for openings or endgames. As the user adds more training information, the AI should automatically get better. I will be switching the file format to XML to make it easier for Raven to parse the information.
* *Represent potential formations (short dyke, long dyke, phalanx, pyramid, echelon) as constraint satisfaction problems (CSPs)* and use a quick search to evaluate whether each formation can still be achieved (after each turn) as part of the planning process. The WHITE_MAP and BLACK_MAP dictionaries can be used to populate the domain for the CSP variables (each checker used in a formation). CSP search can be long if the problems are too constrained, but this should be a representation with fairly loose constraints and few conflicts. 
* *Make the undo and redo work completely correct with the background AI processing*.
* *Begin documenting my design choices with UML*. I've been doing a fair amount of exploratory programming up to this point, but I need to illustrate my design if anyone has a hope of understanding it now.
* *Release a new version that contains the planner code*. Probably will use PyInstaller. Would like to make an OS X release as well as a Windows release this time around. Have to try to dig up a Linux machine now that my PC went up.
