# Design Diagrams

### Design D0:

- Views: the Player watches the Game Screen
- Inputs: the Player sends the computer inputs by typing on a keyboard
- Both the Game Screen and the Keyboard are connected to the computer

![D0](D0.png)

### Design D1:

- The Chaser AI and Evader AI receives input from the Game Sim about the current game state
- Using that information the Chaser AI and Evader AI make decisions and send their input back to the Game Sim
- Depending on the game mode, the Chaser AI or the Evader AI can be replaced by the Player

![D1](D1.png)

### Design D2:

- The Game Screen displays the Game Sim using the Game Sim graphics
- As time progresses The Game updates its Game State as it receives new input using the Level Design and Physics
- The Chaser AI and Evader AI pass information from the Game Sim's Game State to their Neural Networks that dictate their next move
- The Chaser AI also passes information about all Chaser agents to its Neural Network

![D1](D2.png)