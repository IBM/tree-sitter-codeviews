public class Simple {
  public enum Direction {
    Up,
    Down,
    Right,
    Left
  }
  static void Main(string[] args) {
    var result = "";
    var result = operation
        switch {
            Direction.Up => Direction.Down,
            2 => "Case 2",
            3 => "Case 3",
            4 => "Case 4",
            _ => "No case availabe"
        };
    switch (first) {
    case 1000:
        var result = operation
        switch {
            Direction.Up => Direction.Down,
            2 => "Case 2",
            3 => "Case 3",
            4 => "Case 4",
            _ => "No case availabe"
        };
        break;
    case 1 when a == b:
      Console.WriteLine("Monday");
      goto case 2;
    case 0:
    case 2:
      switch (inner) {
      case 5:
        break;
      case 6:
        switch (deep) {
        case 50:
        case 1:
          dosomething();
          break;
        case 100:
        default:
          Console.WriteLine("Def");
          break;
        }
        Console.WriteLine("Saturday");
        break;
        //                    DOING WITHOUT THIS WAS CURRENT FALLTHROUGH BUT INVALID
      case 7:
        Console.WriteLine("Sunday");
        break;
      default:
        Console.WriteLine("Tuesday");
        break;
        //                    DOING WITHOUT THIS INVALID
      }
      Console.WriteLine("Tuesday");
      break;
    case 3:
      break;
    case 4:
      Console.WriteLine("Thursday");
      break;
    case 5:
      break;
    }
  }