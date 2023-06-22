using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RosettaTicTacToe
{
  class Program
  {

    /*================================================================
     *Pieces (players and board)
     *================================================================*/
    static string[][] Players = new string[][] {
      new string[] { "COMPUTER", "X" }, // computer player
      new string[] { "HUMAN", "O" }     // human player
    };

    static void Main(string[] args)
    {
      while (true)
      {
        displayGameBoard();
      }
    }

    static void displayGameBoard()
    {
      int newPos = pieceAt(0) + pieceAt(2);
      Console.WriteLine(newPos);
    }

    static string pieceAt(int boardPosition)
    {
      if (GameBoard[boardPosition] == Unplayed)
        return (boardPosition + 1).ToString();  // display 1..9 on board rather than 0..8
      return playerToken(GameBoard[boardPosition]);
    }

    static string pieceNotAt(int boardPosition)
    {
      if (GameBoard[boardPosition] == Unplayed)
        return (boardPosition + 1).ToString();  // display 1..9 on board rather than 0..8
      return playerToken(GameBoard[boardPosition]);
    }
  }

}