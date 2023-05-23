public class Simple {
static void simpleStuff(){
        // Declaration statement.
        int counter;

        // Assignment statement.
        counter = 1;

        // Error! This is an expression, not an expression statement.
        // counter + 1;

        // Declaration statements with initializers are functionally
        // equivalent to  declaration statement followed by assignment statement:
        int[] radii = { 15, 32, 108, 74, 9 }; // Declare and initialize an array.
        const double pi = 3.14159; // Declare and initialize  constant.

        // foreach statement block that contains multiple statements.
        foreach (int radius in radii)
        {
            // Declaration statement with initializer.
            double circumference = pi * (2 * radius);

            // Expression statement (method invocation). A single-line
            // statement can span multiple text lines because line breaks
            // are treated as white space, which is ignored by the compiler.
            System.Console.WriteLine("Radius of circle #{0} is {1}. Circumference = {2:N2}",
                                    counter, radius, circumference);

            // Expression statement (postfix increment).
            counter++;
        }
        const double pi = 3.14159;
        string smol = "Small";
        using var reader = new StringReader(smol);
        string? item;
        do
        {
            item = reader.ReadLine();
            Console.WriteLine(item);
        } while (item != null);
        // Expression statement (assignment).
        area = 3.14 * (radius * radius);

        // Error. Not  statement because no assignment:
        //circ * 2;

        // Expression statement (method invocation).
        System.Console.WriteLine();

        // Expression statement (new object creation).
        System.Collections.Generic.List<string> strings =
            new System.Collections.Generic.List<string>();

            var result = operation switch
            {
                1 => "Case 1",
                2 => "Case 2",
                3 => "Case 3",
                4 => "Case 4",
                _ => "No case availabe"
            };
            switch (day)
            {
              case 1:
                Console.WriteLine("Monday");
              case 2:
                Console.WriteLine("Tuesday");
                break;
              case 3:
                Console.WriteLine("Wednesday");
                break;
              case 4:
                Console.WriteLine("Thursday");
                break;
              case 5:
                Console.WriteLine("Friday");
                break;
              case 6:
                Console.WriteLine("Saturday");
                break;
              case 7:
                Console.WriteLine("Sunday");
                break;
            }
            // Example #1: var is optional when
            // the select clause specifies a string
            string[] words = { "apple", "strawberry", "grape", "peach", "banana" };
            var wordQuery = from word in words
                            where word[0] == 'g'
                            select word;

            // Because each element in the sequence is a string,
            // not an anonymous type, var is optional here also.
            foreach (string s in wordQuery)
            {
                Console.WriteLine(s);
            }
            string manyLines = @"This is line one
            This is line two
            Here is line three
            The penultimate line is line four
            This is the final, fifth line.";

            using (var reader = new StringReader(manyLines))
            {
                string? item;
                do
                {
                    item = reader.ReadLine();
                    Console.WriteLine(item);
                } while (item != null);
            }
            fixed (char* value = "sam")
            {
                char* ptr = value;
                while (*ptr != '\0')
                {
                    Console.WriteLine(*ptr);
                    ++ptr;
                }
            }
            int num;
            // assign maximum value
            num = int.MaxValue;
            try
            {
                checked
                {
                    // forces stack overflow exception
                    num = num + 1;
                    Console.WriteLine(num);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
            while (true)
            {
                ; //Empty Statement
            }
            Console.ReadLine();
            // Local Function
            void AddValue(int a, int b)
            {
                Console.WriteLine("Value of a is: " + a);
                Console.WriteLine("Value of b is: " + b);
                Console.WriteLine("Sum of a and b is: {0}", a + b);
                Console.WriteLine();
            }

            // Calling Local function
            AddValue(20, 40);
            AddValue(40, 60);
}
}